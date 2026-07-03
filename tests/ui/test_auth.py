import testit


@testit.nameSpace("UI")
@testit.className("Auth")
class TestAuthUI:
  @testit.externalId("UI-AUTH-001")
  @testit.displayName("Успешная авторизация в UI")
  @testit.description("Вход через /login после регистрации администратора через API.")
  @testit.labels("UI", "Auth", "Login")
  def test_login_success(self, login_page, registered_admin):
    with testit.step("Открыть страницу входа и авторизоваться"):
      login_page.login(registered_admin["username"], registered_admin["password"])
    with testit.step("Проверить успешный вход по кнопке «Выйти»"):
      assert login_page.is_logged_in()

  @testit.externalId("UI-AUTH-002")
  @testit.displayName("Авторизация с неверным паролем")
  @testit.description("Вход с неверным паролем. Ожидается сообщение об ошибке.")
  @testit.labels("UI", "Auth", "Login", "Negative")
  def test_login_invalid_password(self, login_page, registered_admin):
    with testit.step("Попытаться войти с неверным паролем"):
      login_page.login(registered_admin["username"], "wrong-password")
    with testit.step("Проверить сообщение об ошибке"):
      assert "неверн" in login_page.get_error_message().lower()
