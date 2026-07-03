from __future__ import annotations

from selenium.webdriver.common.by import By

from src.pages.base_page import BasePage


class StudentsListPage(BasePage):
  STUDENTS_TABLE = (By.ID, "students-table")
  SEARCH_INPUT = (By.ID, "student-search")
  CONFIRM_DELETE_BUTTON = (By.ID, "confirm-delete-btn")
  DELETE_MODAL = (By.ID, "delete-modal")
  LOGOUT_BUTTON = (By.ID, "logout-btn")

  def open_students_list(self) -> None:
    self.open("/users-page")
    if "/login" in self.driver.current_url:
      raise AssertionError("Нет UI-авторизации: открылась страница входа вместо /users-page")
    self.wait.until(
      lambda d: d.find_elements(*self.STUDENTS_TABLE) or d.find_elements(By.CSS_SELECTOR, ".empty-state")
    )

  def get_visible_student_names(self) -> list[str]:
    rows = self.driver.find_elements(By.CSS_SELECTOR, "#students-table tbody tr")
    names: list[str] = []
    for row in rows:
      if row.is_displayed():
        names.append(row.find_element(By.CSS_SELECTOR, "strong").text)
    return names

  def is_student_visible(self, full_name: str) -> bool:
    return full_name in self.get_visible_student_names()

  def search(self, query: str) -> None:
    search = self.wait_for_element_visible(self.SEARCH_INPUT)
    search.clear()
    search.send_keys(query)

  def delete_student(self, full_name: str) -> None:
    delete_button = self.driver.find_element(
      By.CSS_SELECTOR,
      f'.delete-btn[data-student-name="{full_name}"]',
    )
    self.wait_for_element_clickable(delete_button).click()
    self.wait.until(lambda d: "open" in d.find_element(*self.DELETE_MODAL).get_attribute("class"))
    self.wait_for_element_clickable(self.CONFIRM_DELETE_BUTTON).click()
    self.wait.until(lambda d: full_name not in self.get_visible_student_names())

  def logout(self) -> None:
    self.wait_for_element_clickable(self.LOGOUT_BUTTON).click()
    self.wait_for_url_contains("/login")
