from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Generator

import pytest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from src.pages.add_student_page import AddStudentPage
from src.pages.login_page import LoginPage
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
  requests.post(f"{mock_server}/reset", timeout=5)
  yield
  requests.post(f"{mock_server}/reset", timeout=5)


@pytest.fixture
def api_client(mock_server: str) -> ApiClient:
  return ApiClient(base_url=mock_server)


@pytest.fixture
def registered_admin(api_client: ApiClient) -> dict[str, str]:
  username = "test_admin"
  password = "SecurePass123!"
  response = api_client.register(username=username, password=password)
  assert response.status_code == 201, response.text
  return {"username": username, "password": password}


@pytest.fixture
def authenticated_api_client(api_client: ApiClient, registered_admin: dict[str, str]) -> ApiClient:
  response = api_client.login(registered_admin["username"], registered_admin["password"])
  assert response.status_code == 200, response.text
  return api_client


@pytest.fixture
def driver(mock_server: str) -> Generator[webdriver.Chrome, None, None]:
  import shutil

  options = Options()
  if HEADLESS:
    options.add_argument("--headless=new")
  options.add_argument("--no-sandbox")
  options.add_argument("--disable-dev-shm-usage")
  options.add_argument("--window-size=1920,1080")

  chrome_binary = (
    shutil.which("google-chrome")
    or shutil.which("google-chrome-stable")
    or shutil.which("chromium")
    or shutil.which("chromium-browser")
  )
  if chrome_binary:
    options.binary_location = chrome_binary
  else:
    pytest.skip("Chrome/Chromium не установлен — UI-тесты пропущены")

  service = Service(ChromeDriverManager().install())
  browser = webdriver.Chrome(service=service, options=options)
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
def ui_authenticated_session(
  login_page: LoginPage,
  registered_admin: dict[str, str],
) -> dict[str, str]:
  login_page.login(registered_admin["username"], registered_admin["password"])
  assert login_page.is_logged_in(), "Авторизация в UI не завершилась вовремя"
  return registered_admin
