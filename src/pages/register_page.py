from __future__ import annotations

from selenium.webdriver.common.by import By

from src.pages.base_page import BasePage


class RegisterPage(BasePage):
  USERNAME_INPUT = (By.ID, "username")
  PASSWORD_INPUT = (By.ID, "password")
  REGISTER_BUTTON = (By.ID, "register-btn")

  def open_register(self) -> None:
    self.open("/register")

  def register(self, username: str, password: str) -> None:
    self.open_register()
    self.wait_for_element_visible(self.USERNAME_INPUT).send_keys(username)
    self.driver.find_element(*self.PASSWORD_INPUT).send_keys(password)
    self.wait_for_element_clickable(self.REGISTER_BUTTON).click()
