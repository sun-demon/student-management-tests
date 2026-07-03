import testit


@testit.nameSpace("API")
@testit.className("Auth")
class TestAuthAPI:
  @testit.externalId("API-AUTH-001")
  @testit.displayName("Успешная регистрация через API")
  @testit.description("POST /register с уникальным username и password. Ожидается 201.")
  @testit.labels("API", "Auth", "Register")
  def test_register_success(self, api_client):
    with testit.step("Отправить POST /register с новым пользователем"):
      response = api_client.register()
    with testit.step("Проверить статус 201 и наличие username в ответе"):
      assert response.status_code == 201
      assert "username" in response.json()

  @testit.externalId("API-AUTH-002")
  @testit.displayName("Регистрация с существующим username")
  @testit.description("Повторная регистрация с тем же username. Ожидается 409.")
  @testit.labels("API", "Auth", "Register", "Negative")
  def test_register_duplicate_username(self, api_client, registered_admin):
    with testit.step("Отправить POST /register с существующим username"):
      response = api_client.register(
        username=registered_admin["username"],
        password="AnotherPass123!",
      )
    with testit.step("Проверить статус 409 Conflict"):
      assert response.status_code == 409

  @testit.externalId("API-AUTH-003")
  @testit.displayName("Регистрация с пустыми полями")
  @testit.description("POST /register с пустыми username и password. Ожидается 400.")
  @testit.labels("API", "Auth", "Register", "Negative")
  def test_register_empty_fields(self, api_client):
    with testit.step("Отправить POST /register с пустыми полями"):
      response = api_client.register(username="", password="")
    with testit.step("Проверить статус 400 Bad Request"):
      assert response.status_code == 400

  @testit.externalId("API-AUTH-004")
  @testit.displayName("Успешная авторизация через API")
  @testit.description("POST /login с валидными учётными данными. Ожидается 200 и access_token.")
  @testit.labels("API", "Auth", "Login")
  def test_login_success(self, api_client, registered_admin):
    with testit.step("Отправить POST /login"):
      response = api_client.login(registered_admin["username"], registered_admin["password"])
    with testit.step("Проверить статус 200 и наличие access_token"):
      assert response.status_code == 200
      assert response.json().get("access_token")

  @testit.externalId("API-AUTH-005")
  @testit.displayName("Авторизация с неверным паролем")
  @testit.description("POST /login с неверным паролем. Ожидается 401.")
  @testit.labels("API", "Auth", "Login", "Negative")
  def test_login_wrong_password(self, api_client, registered_admin):
    with testit.step("Отправить POST /login с неверным паролем"):
      response = api_client.login(registered_admin["username"], "bad-password")
    with testit.step("Проверить статус 401 Unauthorized"):
      assert response.status_code == 401

  @testit.externalId("API-AUTH-006")
  @testit.displayName("Авторизация несуществующего пользователя")
  @testit.description("POST /login с несуществующим username. Ожидается 401.")
  @testit.labels("API", "Auth", "Login", "Negative")
  def test_login_unknown_user(self, api_client):
    with testit.step("Отправить POST /login для несуществующего пользователя"):
      response = api_client.login("ghost_user", "password")
    with testit.step("Проверить статус 401 Unauthorized"):
      assert response.status_code == 401
