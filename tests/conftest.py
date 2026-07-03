from __future__ import annotations

import json
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Generator

import pytest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from src.pages.add_student_page import AddStudentPage
from src.pages.login_page import LoginPage
from src.pages.register_page import RegisterPage
from src.pages.students_list_page import StudentsListPage
from src.utils.api_client import ApiClient
from src.utils.config import BASE_URL, HEADLESS

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEST_DATA_PATH = PROJECT_ROOT / "src" / "test_data" / "test_data.json"


@pytest.fixture(scope="session")
def test_data() -> dict:
  with TEST_DATA_PATH.open(encoding="utf-8") as file:
    return json.load(file)


@pytest.fixture(scope="session")
def mock_server() -> Generator[str, None, None]:
  """Запускает локальный mock-сервер, если BASE_URL указывает на localhost."""
  base_url = BASE_URL.rstrip("/")
  if "127.0.0.1" not in base_url and "localhost" not in base_url:
    yield base_url
    return

  process = subprocess.Popen(
    [sys.executable, str(PROJECT_ROOT / "mock_server" / "app.py")],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
  )

  for _ in range(30):
    try:
      response = requests.get(f"{base_url}/", timeout=1)
      if response.status_code == 200:
        break
    except requests.RequestException:
      time.sleep(0.5)
  else:
    process.terminate()
    pytest.fail("Не удалось запустить mock-сервер")

  yield base_url

  process.terminate()
  process.wait(timeout=5)


@pytest.fixture(autouse=True)
def reset_app_state(mock_server: str) -> Generator[None, None, None]:
  """Сброс состояния только для локального mock-сервера."""
  is_local = "127.0.0.1" in mock_server or "localhost" in mock_server
  if is_local:
    requests.post(f"{mock_server}/reset", timeout=5)
  yield
  if is_local:
    requests.post(f"{mock_server}/reset", timeout=5)


@pytest.fixture
def api_client(mock_server: str) -> ApiClient:
  return ApiClient(base_url=mock_server)


@pytest.fixture
def registered_admin(api_client: ApiClient) -> dict[str, str]:
  """Регистрация администратора через API (как в ТЗ)."""
  username = f"test_admin_{uuid.uuid4().hex[:8]}"
  password = "SecurePass123!"
  response = api_client.register(username=username, password=password)
  assert response.status_code == 201, response.text
  return {"username": username, "password": password}


@pytest.fixture
def authenticated_api_client(api_client: ApiClient, registered_admin: dict[str, str]) -> ApiClient:
  """API-клиент с Bearer-токеном."""
  api_client.ensure_authenticated(registered_admin["username"], registered_admin["password"])
  return api_client


@pytest.fixture
def driver(mock_server: str) -> Generator[webdriver.Chrome, None, None]:
  import os
  import shutil

  options = Options()
  if HEADLESS:
    options.add_argument("--headless=new")
  options.add_argument("--no-sandbox")
  options.add_argument("--disable-dev-shm-usage")
  options.add_argument("--disable-gpu")
  options.add_argument("--window-size=1920,1080")

  chrome_binary = (
    os.getenv("CHROME_BIN")
    or os.getenv("CHROME_PATH")
    or shutil.which("google-chrome")
    or shutil.which("google-chrome-stable")
    or shutil.which("chromium")
    or shutil.which("chromium-browser")
  )
  if chrome_binary:
    options.binary_location = chrome_binary
  else:
    pytest.skip("Chrome/Chromium не установлен — UI-тесты пропущены")

  chromedriver_path = os.getenv("CHROMEDRIVER_PATH") or os.getenv("CHROMEDRIVER_BIN")
  if chromedriver_path:
    browser = webdriver.Chrome(service=Service(chromedriver_path), options=options)
  else:
    browser = webdriver.Chrome(options=options)
  browser.implicitly_wait(0)
  yield browser
  browser.quit()


@pytest.fixture
def login_page(driver: webdriver.Chrome, mock_server: str) -> LoginPage:
  return LoginPage(driver, mock_server)


@pytest.fixture
def add_student_page(driver: webdriver.Chrome, mock_server: str) -> AddStudentPage:
  return AddStudentPage(driver, mock_server)


@pytest.fixture
def register_page(driver: webdriver.Chrome, mock_server: str) -> RegisterPage:
  return RegisterPage(driver, mock_server)


@pytest.fixture
def students_list_page(driver: webdriver.Chrome, mock_server: str) -> StudentsListPage:
  return StudentsListPage(driver, mock_server)


@pytest.fixture
def ui_authenticated_session(
  login_page: LoginPage,
  registered_admin: dict[str, str],
) -> dict[str, str]:
  """Авторизация в UI после регистрации администратора через API."""
  login_page.login(registered_admin["username"], registered_admin["password"])
  login_page.wait.until(
    EC.visibility_of_element_located((By.ID, "logout-btn"))
  )
  assert login_page.is_logged_in(), "Авторизация в UI не завершилась вовремя"
  return registered_admin
