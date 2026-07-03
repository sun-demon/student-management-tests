from __future__ import annotations

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.utils.config import DEFAULT_TIMEOUT, POLL_FREQUENCY


class BasePage:
  def __init__(self, driver: WebDriver, base_url: str) -> None:
    self.driver = driver
    self.base_url = base_url.rstrip("/")
    self.wait = WebDriverWait(driver, DEFAULT_TIMEOUT, poll_frequency=POLL_FREQUENCY)

  def open(self, path: str = "/") -> None:
    self.driver.get(f"{self.base_url}{path}")

  def wait_for_url_contains(self, fragment: str) -> None:
    self.wait.until(EC.url_contains(fragment))

  def wait_for_element_visible(self, locator: tuple[str, str]):
    return self.wait.until(EC.visibility_of_element_located(locator))

  def wait_for_element_clickable(self, locator: tuple[str, str]):
    return self.wait.until(EC.element_to_be_clickable(locator))
