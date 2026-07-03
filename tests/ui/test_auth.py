import testit


class TestAuthUI:
  @testit.externalId("UI-AUTH-001")
  @testit.displayName("Успешная авторизация в UI")
  def test_login_success(self, login_page, registered_admin):
    login_page.login(registered_admin["username"], registered_admin["password"])
    assert login_page.is_logged_in()

  @testit.externalId("UI-AUTH-002")
  @testit.displayName("Авторизация с неверным паролем")
  def test_login_invalid_password(self, login_page, registered_admin):
    login_page.login(registered_admin["username"], "wrong-password")
    assert "неверн" in login_page.get_error_message().lower()
