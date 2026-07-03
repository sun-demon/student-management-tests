import testit


@testit.nameSpace("API")
@testit.className("System")
class TestSystemAPI:
  @testit.externalId("API-SYS-001")
  @testit.displayName("Главная страница доступна")
  @testit.description("GET /. Ожидается 200.")
  @testit.tags("API", "System")
  def test_home_page_available(self, api_client):
    with testit.step("Отправить GET /"):
      response = api_client.session.get(f"{api_client.base_url}/")
    with testit.step("Проверить статус 200"):
      assert response.status_code == 200
      assert "EduManage" in response.text

  @testit.externalId("API-SYS-002")
  @testit.displayName("OpenAPI спецификация доступна")
  @testit.description("GET /openapi.json. Ожидается 200 и поле openapi.")
  @testit.tags("API", "System", "Swagger")
  def test_openapi_spec_available(self, api_client):
    with testit.step("Отправить GET /openapi.json"):
      response = api_client.session.get(f"{api_client.base_url}/openapi.json")
    with testit.step("Проверить структуру OpenAPI"):
      assert response.status_code == 200
      body = response.json()
      assert body["openapi"].startswith("3.")
      assert "/register" in body["paths"]
      assert "/users" in body["paths"]

  @testit.externalId("API-SYS-003")
  @testit.displayName("Swagger UI доступен")
  @testit.description("GET /swagger. Ожидается 200.")
  @testit.tags("API", "System", "Swagger")
  def test_swagger_page_available(self, api_client):
    with testit.step("Отправить GET /swagger"):
      response = api_client.session.get(f"{api_client.base_url}/swagger")
    with testit.step("Проверить статус 200"):
      assert response.status_code == 200
      assert "swagger" in response.text.lower()
