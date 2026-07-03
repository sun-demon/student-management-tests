import uuid

import testit


@testit.nameSpace("UI")
@testit.className("Auth")
class TestRegisterUI:
  @testit.externalId("UI-AUTH-003")
  @testit.displayName("Успешная регистрация через UI")
  @testit.description("Регистрация нового администратора через /register. Ожидается редирект на /login.")
  @testit.tags("UI", "Auth", "Register")
  def test_register_success(self, register_page):
    username = f"ui_admin_{uuid.uuid4().hex[:8]}"
    with testit.step("Заполнить форму регистрации"):
      register_page.register(username, "SecurePass123!")
    with testit.step("Проверить переход на страницу входа"):
      assert register_page.is_on_login_page()


@testit.nameSpace("UI")
@testit.className("Auth")
class TestLogoutUI:
  @testit.externalId("UI-AUTH-004")
  @testit.displayName("Выход из системы через UI")
  @testit.description("Нажатие «Выйти» завершает сессию и открывает /login.")
  @testit.tags("UI", "Auth", "Logout")
  def test_logout_success(self, students_list_page, ui_authenticated_session):
    with testit.step("Открыть список студентов и выйти"):
      students_list_page.open_students_list()
      students_list_page.logout()
    with testit.step("Проверить страницу входа"):
      assert "/login" in students_list_page.driver.current_url

  @testit.externalId("UI-AUTH-005")
  @testit.displayName("Редирект на вход без авторизации")
  @testit.description("Попытка открыть /add-user без сессии. Ожидается /login.")
  @testit.tags("UI", "Auth", "Negative")
  def test_unauthenticated_redirect(self, add_student_page):
    with testit.step("Открыть /add-user без авторизации"):
      add_student_page.open("/add-user")
    with testit.step("Проверить редирект на /login"):
      add_student_page.wait_for_url_contains("/login")
