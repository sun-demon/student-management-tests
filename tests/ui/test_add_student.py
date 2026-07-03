from __future__ import annotations

import testit

from src.pages.add_student_page import AddStudentPage


class TestAddStudentUI:
  @testit.externalId("UI-AUTO-001")
  @testit.displayName("Успешное добавление студента через UI")
  @testit.workItemIds("TC-UI-001")
  def test_add_student_success(
    self,
    add_student_page: AddStudentPage,
    authenticated_api_client,
    ui_authenticated_session,
    test_data: dict,
  ):
    student = test_data["valid_student"]

    with testit.step("Заполнить форму валидными данными"):
      add_student_page.add_student(student)

    with testit.step("Проверить сообщение об успехе в UI"):
      assert "успешно добавлен" in add_student_page.get_success_message().lower()

    with testit.step("Проверить наличие студента в таблице"):
      assert add_student_page.is_student_in_table(student["full_name"])

    with testit.step("Проверить наличие студента через API"):
      assert authenticated_api_client.student_exists(
        student["full_name"],
        student["age"],
        student["gender"],
      )

  @testit.externalId("UI-AUTO-002")
  @testit.displayName("Добавление студента без ФИО")
  @testit.workItemIds("TC-UI-002")
  def test_add_student_missing_fullname(
    self,
    add_student_page,
    ui_authenticated_session,
    test_data: dict,
  ):
    student = dict(test_data["valid_student"])
    student["full_name"] = ""

    add_student_page.add_student(student)
    error = add_student_page.get_error_message()
    assert "ФИО" in error

  @testit.externalId("UI-AUTO-003")
  @testit.displayName("Добавление студента с невалидным возрастом")
  @testit.workItemIds("TC-UI-003")
  def test_add_student_invalid_age(
    self,
    add_student_page,
    ui_authenticated_session,
    test_data: dict,
  ):
    student = test_data["invalid_age_student"]
    add_student_page.add_student(student)
    error = add_student_page.get_error_message()
    assert "возраст" in error.lower()

  @testit.externalId("UI-AUTO-004")
  @testit.displayName("Добавление студента без указания пола")
  @testit.workItemIds("TC-UI-004")
  def test_add_student_missing_gender(
    self,
    add_student_page,
    ui_authenticated_session,
    test_data: dict,
  ):
    student = test_data["missing_gender_student"]
    add_student_page.add_student(student)
    error = add_student_page.get_error_message()
    assert "пол" in error.lower()

  @testit.externalId("UI-AUTO-005")
  @testit.displayName("Добавление студента с ФИО со спецсимволами")
  @testit.workItemIds("TC-UI-006")
  def test_add_student_valid_data_special_chars(
    self,
    add_student_page,
    authenticated_api_client,
    ui_authenticated_session,
    test_data: dict,
  ):
    student = test_data["student_special_chars"]
    add_student_page.add_student(student)
    assert "успешно добавлен" in add_student_page.get_success_message().lower()
    assert add_student_page.is_student_in_table(student["full_name"])
