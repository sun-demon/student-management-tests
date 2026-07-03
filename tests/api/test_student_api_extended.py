import testit


@testit.nameSpace("API")
@testit.className("Students")
class TestStudentAPIExtended:
  @testit.externalId("API-STU-010")
  @testit.displayName("Получение студента по ID")
  @testit.description("GET /user/{id} для существующего студента. Ожидается 200.")
  @testit.tags("API", "Students")
  def test_get_student_by_id(self, authenticated_api_client, test_data):
    with testit.step("Создать студента"):
      student_id = authenticated_api_client.add_student(test_data["valid_student"]).json()["id"]
    with testit.step("Отправить GET /user/{id}"):
      response = authenticated_api_client.get_student(student_id)
    with testit.step("Проверить данные студента"):
      assert response.status_code == 200
      body = response.json()
      assert body["id"] == student_id
      assert body["full_name"] == test_data["valid_student"]["full_name"]

  @testit.externalId("API-STU-011")
  @testit.displayName("Получение несуществующего студента")
  @testit.description("GET /user/999999. Ожидается 404.")
  @testit.tags("API", "Students", "Negative")
  def test_get_student_not_found(self, authenticated_api_client):
    with testit.step("Отправить GET /user/999999"):
      response = authenticated_api_client.get_student(999999)
    with testit.step("Проверить статус 404"):
      assert response.status_code == 404

  @testit.externalId("API-STU-012")
  @testit.displayName("Удаление несуществующего студента")
  @testit.description("DELETE /user/999999. Ожидается 404.")
  @testit.tags("API", "Students", "Negative")
  def test_delete_nonexistent_student(self, authenticated_api_client):
    with testit.step("Отправить DELETE /user/999999"):
      response = authenticated_api_client.delete_student(999999)
    with testit.step("Проверить статус 404"):
      assert response.status_code == 404

  @testit.externalId("API-STU-013")
  @testit.displayName("Добавление студента без авторизации")
  @testit.description("POST /add-user без Bearer-токена. Ожидается 401.")
  @testit.tags("API", "Students", "Auth", "Negative")
  def test_add_student_without_auth(self, api_client, test_data):
    with testit.step("Отправить POST /add-user без токена"):
      response = api_client.add_student(test_data["valid_student"])
    with testit.step("Проверить статус 401"):
      assert response.status_code == 401

  @testit.externalId("API-STU-014")
  @testit.displayName("Получение списка студентов без авторизации")
  @testit.description("GET /users без Bearer-токена. Ожидается 401.")
  @testit.tags("API", "Students", "Auth", "Negative")
  def test_get_students_without_auth(self, api_client):
    with testit.step("Отправить GET /users без токена"):
      response = api_client.get_students()
    with testit.step("Проверить статус 401"):
      assert response.status_code == 401

  @testit.externalId("API-STU-015")
  @testit.displayName("Добавление студента без ФИО")
  @testit.description("POST /add-user с пустым full_name. Ожидается 400.")
  @testit.tags("API", "Students", "Negative")
  def test_add_student_missing_fullname(self, authenticated_api_client, test_data):
    payload = dict(test_data["valid_student"])
    payload["full_name"] = ""
    with testit.step("Отправить POST /add-user без ФИО"):
      response = authenticated_api_client.add_student(payload)
    with testit.step("Проверить статус 400"):
      assert response.status_code == 400
      assert "ФИО" in str(response.json())

  @testit.externalId("API-STU-016")
  @testit.displayName("Добавление студента без пола")
  @testit.description("POST /add-user без gender. Ожидается 400.")
  @testit.tags("API", "Students", "Negative")
  def test_add_student_missing_gender(self, authenticated_api_client, test_data):
    with testit.step("Отправить POST /add-user без пола"):
      response = authenticated_api_client.add_student(test_data["missing_gender_student"])
    with testit.step("Проверить статус 400"):
      assert response.status_code == 400

  @testit.externalId("API-STU-017")
  @testit.displayName("Частичное обновление студента")
  @testit.description("PUT /user/{id} только с полем age. Ожидается 200.")
  @testit.tags("API", "Students")
  def test_partial_update_student(self, authenticated_api_client, test_data):
    with testit.step("Создать студента"):
      student_id = authenticated_api_client.add_student(test_data["valid_student"]).json()["id"]
    with testit.step("Обновить только возраст"):
      response = authenticated_api_client.update_student(student_id, {"age": 25})
    with testit.step("Проверить обновлённый возраст и сохранённое ФИО"):
      assert response.status_code == 200
      body = response.json()
      assert body["age"] == 25
      assert body["full_name"] == test_data["valid_student"]["full_name"]

  @testit.externalId("API-STU-018")
  @testit.displayName("Добавление неактивного студента")
  @testit.description("POST /add-user с is_active=false. Ожидается 201.")
  @testit.tags("API", "Students")
  def test_add_inactive_student(self, authenticated_api_client, test_data):
    student = dict(test_data["student_special_chars"])
    student["is_active"] = False
    with testit.step("Отправить POST /add-user"):
      response = authenticated_api_client.add_student(student)
    with testit.step("Проверить статус 201 и is_active=false"):
      assert response.status_code == 201
      assert response.json()["is_active"] is False
