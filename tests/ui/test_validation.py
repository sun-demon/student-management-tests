import testit


@testit.nameSpace("UI")
@testit.className("Validation")
class TestValidationUI:
  @testit.externalId("UI-VAL-001")
  @testit.displayName("Невалидный формат даты поступления")
  @testit.description("Дата 31/02/2024 в поле enrollment_date. Ожидается ошибка валидации.")
  @testit.tags("UI", "Students", "Negative")
  def test_add_student_invalid_date_format(
    self,
    add_student_page,
    ui_authenticated_session,
    test_data: dict,
  ):
    student = dict(test_data["valid_student"])
    student["enrollment_date"] = "31/02/2024"
    with testit.step("Заполнить форму с невалидной датой"):
      add_student_page.add_student(student)
    with testit.step("Проверить сообщение об ошибке"):
      error = add_student_page.get_error_message()
      assert "дата" in error.lower() or "формат" in error.lower()
