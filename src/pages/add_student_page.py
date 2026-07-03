from __future__ import annotations

from typing import Any

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from src.pages.base_page import BasePage


class AddStudentPage(BasePage):
  FULL_NAME_INPUT = (By.ID, "full_name")
  AGE_INPUT = (By.ID, "age")
  GENDER_SELECT = (By.ID, "gender")
  ENROLLMENT_DATE_INPUT = (By.ID, "enrollment_date")
  IS_ACTIVE_CHECKBOX = (By.ID, "is_active")
  SUBMIT_BUTTON = (By.ID, "add-btn")
  ERROR_MESSAGE = (By.CSS_SELECTOR, ".alert-error")
  SUCCESS_MESSAGE = (By.CSS_SELECTOR, ".alert-success")
  STUDENTS_TABLE = (By.ID, "students-table")
  FORM_ALERT = (By.CSS_SELECTOR, ".alert-error, .alert-success")

  def open_add_student(self) -> None:
    self.open("/add-user")
    if "/login" in self.driver.current_url:
      raise AssertionError("Нет UI-авторизации: открылась страница входа вместо /add-user")
    self.wait_for_element_visible(self.FULL_NAME_INPUT)

  def clear_form(self) -> None:
    self.driver.find_element(*self.FULL_NAME_INPUT).clear()
    self.driver.find_element(*self.AGE_INPUT).clear()
    self.driver.find_element(*self.ENROLLMENT_DATE_INPUT).clear()
    Select(self.driver.find_element(*self.GENDER_SELECT)).select_by_value("")
    checkbox = self.driver.find_element(*self.IS_ACTIVE_CHECKBOX)
    if checkbox.is_selected():
      checkbox.click()

  def fill_form(self, student: dict[str, Any]) -> None:
    self.clear_form()
    if "full_name" in student and student["full_name"] is not None:
      self.driver.find_element(*self.FULL_NAME_INPUT).send_keys(student["full_name"])
    if "age" in student and student["age"] is not None and student["age"] != "":
      self.driver.find_element(*self.AGE_INPUT).send_keys(str(student["age"]))
    if student.get("gender"):
      Select(self.driver.find_element(*self.GENDER_SELECT)).select_by_value(student["gender"])
    if student.get("enrollment_date"):
      self.driver.find_element(*self.ENROLLMENT_DATE_INPUT).send_keys(student["enrollment_date"])
    if student.get("is_active"):
      checkbox = self.driver.find_element(*self.IS_ACTIVE_CHECKBOX)
      if not checkbox.is_selected():
        checkbox.click()

  def submit(self) -> None:
    alerts_before = len(self.driver.find_elements(*self.FORM_ALERT))
    self.wait_for_element_clickable(self.SUBMIT_BUTTON).click()
    self.wait.until(
      lambda d: len(d.find_elements(*self.FORM_ALERT)) > alerts_before
      or d.find_elements(*self.SUCCESS_MESSAGE)
      or d.find_elements(*self.ERROR_MESSAGE)
    )

  def add_student(self, student: dict[str, Any]) -> None:
    self.open_add_student()
    self.fill_form(student)
    self.submit()

  def get_error_message(self) -> str:
    return self.wait_for_element_visible(self.ERROR_MESSAGE).text

  def get_success_message(self) -> str:
    return self.wait_for_element_visible(self.SUCCESS_MESSAGE).text

  def open_students_list(self) -> None:
    self.open("/users-page")
    self.wait_for_element_visible(self.STUDENTS_TABLE)

  def is_student_in_table(self, full_name: str) -> bool:
    self.open_students_list()
    rows = self.driver.find_elements(By.CSS_SELECTOR, "#students-table tbody tr")
    return any(full_name in row.text for row in rows)
