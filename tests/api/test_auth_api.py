import pytest
import testit


class TestAuthAPI:
  @testit.externalId("API-AUTH-001")
  @testit.displayName("Успешная регистрация через API")
  def test_register_success(self, api_client):
    response = api_client.register()
    assert response.status_code == 201
    assert "username" in response.json()

  @testit.externalId("API-AUTH-002")
  @testit.displayName("Регистрация с существующим username")
  def test_register_duplicate_username(self, api_client, registered_admin):
    response = api_client.register(
      username=registered_admin["username"],
      password="AnotherPass123!",
    )
    assert response.status_code == 409

  @testit.externalId("API-AUTH-003")
  @testit.displayName("Регистрация с пустыми полями")
  def test_register_empty_fields(self, api_client):
    response = api_client.register(username="", password="")
    assert response.status_code == 400

  @testit.externalId("API-AUTH-004")
  @testit.displayName("Успешная авторизация через API")
  def test_login_success(self, api_client, registered_admin):
    response = api_client.login(registered_admin["username"], registered_admin["password"])
    assert response.status_code == 200
    assert response.json().get("access_token")

  @testit.externalId("API-AUTH-005")
  @testit.displayName("Авторизация с неверным паролем")
  def test_login_wrong_password(self, api_client, registered_admin):
    response = api_client.login(registered_admin["username"], "bad-password")
    assert response.status_code == 401

  @testit.externalId("API-AUTH-006")
  @testit.displayName("Авторизация несуществующего пользователя")
  def test_login_unknown_user(self, api_client):
    response = api_client.login("ghost_user", "password")
    assert response.status_code == 401
