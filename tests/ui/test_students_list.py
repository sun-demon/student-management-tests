import testit

from src.pages.add_student_page import AddStudentPage
from src.pages.students_list_page import StudentsListPage


@testit.nameSpace("UI")
@testit.className("StudentsList")
class TestStudentsListUI:
  @testit.externalId("UI-LIST-001")
  @testit.displayName("Список студентов отображает добавленную запись")
  @testit.description("После добавления студента запись видна на /users-page.")
  @testit.tags("UI", "Students")
  def test_students_list_shows_added_student(
    self,
    add_student_page: AddStudentPage,
    students_list_page: StudentsListPage,
    ui_authenticated_session,
    test_data: dict,
  ):
    student = test_data["valid_student"]
    with testit.step("Добавить студента через форму"):
      add_student_page.add_student(student)
    with testit.step("Открыть список студентов"):
      students_list_page.open_students_list()
    with testit.step("Проверить наличие ФИО в таблице"):
      assert students_list_page.is_student_visible(student["full_name"])

  @testit.externalId("UI-LIST-002")
  @testit.displayName("Поиск студента по ФИО")
  @testit.description("Фильтр на /users-page скрывает записи, не совпадающие с запросом.")
  @testit.tags("UI", "Students")
  def test_students_search_filter(
    self,
    add_student_page: AddStudentPage,
    students_list_page: StudentsListPage,
    authenticated_api_client,
    ui_authenticated_session,
    test_data: dict,
  ):
    first = dict(test_data["valid_student"])
    second = dict(test_data["student_special_chars"])
    with testit.step("Добавить двух студентов через API"):
      authenticated_api_client.ensure_authenticated(
        ui_authenticated_session["username"],
        ui_authenticated_session["password"],
      )
      authenticated_api_client.add_student(first)
      authenticated_api_client.add_student(second)
    with testit.step("Открыть список и выполнить поиск"):
      students_list_page.open_students_list()
      students_list_page.search(second["full_name"])
    with testit.step("Проверить, что виден только искомый студент"):
      visible = students_list_page.get_visible_student_names()
      assert second["full_name"] in visible
      assert first["full_name"] not in visible

  @testit.externalId("UI-LIST-003")
  @testit.displayName("Удаление студента из списка")
  @testit.description("Удаление через модальное окно на /users-page.")
  @testit.tags("UI", "Students")
  def test_delete_student_from_list(
    self,
    authenticated_api_client,
    students_list_page: StudentsListPage,
    ui_authenticated_session,
    test_data: dict,
  ):
    student = test_data["valid_student"]
    with testit.step("Создать студента через API"):
      authenticated_api_client.ensure_authenticated(
        ui_authenticated_session["username"],
        ui_authenticated_session["password"],
      )
      authenticated_api_client.add_student(student)
    with testit.step("Удалить студента через UI"):
      students_list_page.open_students_list()
      assert students_list_page.is_student_visible(student["full_name"])
      students_list_page.delete_student(student["full_name"])
    with testit.step("Проверить отсутствие записи в таблице"):
      assert not students_list_page.is_student_visible(student["full_name"])
