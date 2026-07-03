import testit


class TestValidationUI:
  @testit.externalId("UI-VAL-001")
  @testit.displayName("Невалидный формат даты поступления")
  def test_add_student_invalid_date_format(
    self,
    add_student_page,
    ui_authenticated_session,
    test_data: dict,
  ):
    student = dict(test_data["valid_student"])
    student["enrollment_date"] = "31/02/2024"
    add_student_page.add_student(student)
    error = add_student_page.get_error_message()
    assert "дата" in error.lower() or "формат" in error.lower()
