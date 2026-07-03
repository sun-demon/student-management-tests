from __future__ import annotations

from selenium.webdriver.common.by import By

from src.pages.base_page import BasePage


class LoginPage(BasePage):
  USERNAME_INPUT = (By.ID, "username")
  PASSWORD_INPUT = (By.ID, "password")
  LOGIN_BUTTON = (By.ID, "login-btn")
  ERROR_MESSAGE = (By.CSS_SELECTOR, ".alert-error")

  def open_login(self) -> None:
    self.open("/login")

  def login(self, username: str, password: str) -> None:
    self.open_login()
    self.wait_for_element_visible(self.USERNAME_INPUT).send_keys(username)
    self.driver.find_element(*self.PASSWORD_INPUT).send_keys(password)
    self.wait_for_element_clickable(self.LOGIN_BUTTON).click()
    self.wait.until(lambda d: "/add-user" in d.current_url or d.find_elements(*self.ERROR_MESSAGE))

  def is_logged_in(self) -> bool:
    return "/add-user" in self.driver.current_url or bool(self.driver.find_elements(By.ID, "logout-btn"))

  def get_error_message(self) -> str:
    return self.wait_for_element_visible(self.ERROR_MESSAGE).text
