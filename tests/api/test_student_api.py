import testit


@testit.nameSpace("API")
@testit.className("Students")
class TestStudentAPI:
  @testit.externalId("API-STU-001")
  @testit.displayName("Добавление студента с валидными данными")
  @testit.description("POST /add-user с Bearer-токеном и валидным телом. Ожидается 201.")
  @testit.labels("API", "Students")
  def test_add_student_success(self, authenticated_api_client, test_data):
    with testit.step("Отправить POST /add-user"):
      response = authenticated_api_client.add_student(test_data["valid_student"])
    with testit.step("Проверить статус 201 и данные студента"):
      assert response.status_code == 201
      assert response.json()["full_name"] == test_data["valid_student"]["full_name"]

  @testit.externalId("API-STU-002")
  @testit.displayName("Получение списка студентов")
  @testit.description("GET /users с Bearer-токеном. Ожидается 200 и непустой список.")
  @testit.labels("API", "Students")
  def test_get_students(self, authenticated_api_client, test_data):
    with testit.step("Добавить студента для проверки списка"):
      authenticated_api_client.add_student(test_data["valid_student"])
    with testit.step("Отправить GET /users"):
      response = authenticated_api_client.get_students()
    with testit.step("Проверить статус 200 и наличие записей"):
      assert response.status_code == 200
      assert len(response.json()) >= 1

  @testit.externalId("API-STU-003")
  @testit.displayName("Обновление данных студента")
  @testit.description("PUT /user/{id} с валидными данными. Ожидается 200.")
  @testit.labels("API", "Students")
  def test_update_student(self, authenticated_api_client, test_data):
    with testit.step("Создать студента"):
      student_id = authenticated_api_client.add_student(test_data["valid_student"]).json()["id"]
    with testit.step("Отправить PUT /user/{id}"):
      response = authenticated_api_client.update_student(
        student_id,
        {"full_name": "Обновлённый Студент", "age": 21, "gender": "Ж"},
      )
    with testit.step("Проверить обновлённое имя"):
      assert response.status_code == 200
      assert response.json()["full_name"] == "Обновлённый Студент"

  @testit.externalId("API-STU-004")
  @testit.displayName("Удаление студента")
  @testit.description("DELETE /user/{id}. Ожидается 200, затем GET возвращает 404.")
  @testit.labels("API", "Students")
  def test_delete_student(self, authenticated_api_client, test_data):
    with testit.step("Создать студента"):
      student_id = authenticated_api_client.add_student(test_data["valid_student"]).json()["id"]
    with testit.step("Отправить DELETE /user/{id}"):
      assert authenticated_api_client.delete_student(student_id).status_code == 200
    with testit.step("Проверить, что студент не найден"):
      assert authenticated_api_client.get_student(student_id).status_code == 404

  @testit.externalId("API-STU-005")
  @testit.displayName("Добавление студента с невалидным возрастом")
  @testit.description("POST /add-user с отрицательным возрастом. Ожидается 400.")
  @testit.labels("API", "Students", "Negative")
  def test_add_student_invalid_age(self, authenticated_api_client, test_data):
    with testit.step("Отправить POST /add-user с age=-5"):
      response = authenticated_api_client.add_student(test_data["invalid_age_student"])
    with testit.step("Проверить статус 400"):
      assert response.status_code == 400

  @testit.externalId("API-STU-006")
  @testit.displayName("Добавление студента с невалидным полом")
  @testit.description("POST /add-user с gender=X. Ожидается 400.")
  @testit.labels("API", "Students", "Negative")
  def test_add_student_invalid_gender(self, authenticated_api_client, test_data):
    with testit.step("Отправить POST /add-user с невалидным полом"):
      response = authenticated_api_client.add_student(test_data["invalid_gender_student"])
    with testit.step("Проверить статус 400"):
      assert response.status_code == 400

  @testit.externalId("API-STU-007")
  @testit.displayName("Добавление студента с невалидной датой")
  @testit.description("POST /add-user с некорректной датой. Ожидается 400.")
  @testit.labels("API", "Students", "Negative")
  def test_add_student_invalid_date(self, authenticated_api_client, test_data):
    with testit.step("Отправить POST /add-user с invalid-date"):
      response = authenticated_api_client.add_student(test_data["invalid_date_student"])
    with testit.step("Проверить статус 400"):
      assert response.status_code == 400

  @testit.externalId("API-STU-008")
  @testit.displayName("Обновление несуществующего студента возвращает 404")
  @testit.description("PUT /user/999999. Ожидается 404 Not Found.")
  @testit.labels("API", "Students", "Negative")
  def test_update_nonexistent_student(self, authenticated_api_client, test_data):
    with testit.step("Отправить PUT /user/999999"):
      response = authenticated_api_client.update_student(999999, test_data["valid_student"])
    with testit.step("Проверить статус 404"):
      assert response.status_code == 404

  @testit.externalId("API-STU-009")
  @testit.displayName("Токен инвалидируется после logout")
  @testit.description("После POST /logout старый Bearer-токен не должен работать. Ожидается 401.")
  @testit.labels("API", "Auth", "Students")
  def test_token_invalid_after_logout(self, authenticated_api_client, registered_admin):
    with testit.step("Убедиться, что токен получен"):
      assert authenticated_api_client.token is not None
    with testit.step("Выполнить POST /logout"):
      assert authenticated_api_client.logout().status_code == 200
    with testit.step("Проверить, что GET /users возвращает 401"):
      assert authenticated_api_client.get_students().status_code == 401
