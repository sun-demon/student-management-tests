from __future__ import annotations

from selenium.webdriver.common.by import By

from src.pages.base_page import BasePage


class RegisterPage(BasePage):
  USERNAME_INPUT = (By.ID, "username")
  PASSWORD_INPUT = (By.ID, "password")
  REGISTER_BUTTON = (By.ID, "register-btn")
  ERROR_MESSAGE = (By.CSS_SELECTOR, ".alert-error")

  def open_register(self) -> None:
    self.open("/register")

  def register(self, username: str, password: str) -> None:
    self.open_register()
    self.wait_for_element_visible(self.USERNAME_INPUT).send_keys(username)
    self.driver.find_element(*self.PASSWORD_INPUT).send_keys(password)
    self.wait_for_element_clickable(self.REGISTER_BUTTON).click()
    self.wait.until(
      lambda d: "/login" in d.current_url or d.find_elements(*self.ERROR_MESSAGE)
    )

  def is_on_login_page(self) -> bool:
    return "/login" in self.driver.current_url

  def get_error_message(self) -> str:
    return self.wait_for_element_visible(self.ERROR_MESSAGE).text
