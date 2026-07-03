from __future__ import annotations

from selenium.webdriver.common.by import By

from src.pages.base_page import BasePage


class LoginPage(BasePage):
  USERNAME_INPUT = (By.ID, "username")
  PASSWORD_INPUT = (By.ID, "password")
  LOGIN_BUTTON = (By.ID, "login-btn")
  ERROR_MESSAGE = (By.CSS_SELECTOR, ".error")

  def open_login(self) -> None:
    self.open("/login")

  def login(self, username: str, password: str) -> None:
    self.open_login()
    self.wait_for_element_visible(self.USERNAME_INPUT).send_keys(username)
    self.driver.find_element(*self.PASSWORD_INPUT).send_keys(password)
    self.wait_for_element_clickable(self.LOGIN_BUTTON).click()

  def is_logged_in(self) -> bool:
    try:
      self.wait_for_element_visible((By.ID, "logout-btn"))
      return True
    except Exception:
      return False

  def get_error_message(self) -> str:
    return self.wait_for_element_visible(self.ERROR_MESSAGE).text
