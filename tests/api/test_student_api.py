import testit


class TestStudentAPI:
  @testit.externalId("API-STU-001")
  @testit.displayName("Добавление студента с валидными данными")
  def test_add_student_success(self, authenticated_api_client, test_data):
    response = authenticated_api_client.add_student(test_data["valid_student"])
    assert response.status_code == 201
    body = response.json()
    assert body["full_name"] == test_data["valid_student"]["full_name"]

  @testit.externalId("API-STU-002")
  @testit.displayName("Получение списка студентов")
  def test_get_students(self, authenticated_api_client, test_data):
    authenticated_api_client.add_student(test_data["valid_student"])
    response = authenticated_api_client.get_students()
    assert response.status_code == 200
    assert len(response.json()) >= 1

  @testit.externalId("API-STU-003")
  @testit.displayName("Обновление данных студента")
  def test_update_student(self, authenticated_api_client, test_data):
    create_response = authenticated_api_client.add_student(test_data["valid_student"])
    student_id = create_response.json()["id"]
    update_payload = {"full_name": "Обновлённый Студент", "age": 21, "gender": "Ж"}
    response = authenticated_api_client.update_student(student_id, update_payload)
    assert response.status_code == 200
    assert response.json()["full_name"] == "Обновлённый Студент"

  @testit.externalId("API-STU-004")
  @testit.displayName("Удаление студента")
  def test_delete_student(self, authenticated_api_client, test_data):
    create_response = authenticated_api_client.add_student(test_data["valid_student"])
    student_id = create_response.json()["id"]
    delete_response = authenticated_api_client.delete_student(student_id)
    assert delete_response.status_code == 200
    get_response = authenticated_api_client.get_student(student_id)
    assert get_response.status_code == 404

  @testit.externalId("API-STU-005")
  @testit.displayName("Добавление студента с невалидным возрастом")
  def test_add_student_invalid_age(self, authenticated_api_client, test_data):
    response = authenticated_api_client.add_student(test_data["invalid_age_student"])
    assert response.status_code == 400

  @testit.externalId("API-STU-006")
  @testit.displayName("Добавление студента с невалидным полом")
  def test_add_student_invalid_gender(self, authenticated_api_client, test_data):
    response = authenticated_api_client.add_student(test_data["invalid_gender_student"])
    assert response.status_code == 400

  @testit.externalId("API-STU-007")
  @testit.displayName("Добавление студента с невалидной датой")
  def test_add_student_invalid_date(self, authenticated_api_client, test_data):
    response = authenticated_api_client.add_student(test_data["invalid_date_student"])
    assert response.status_code == 400

  @testit.externalId("API-STU-008")
  @testit.displayName("Обновление несуществующего студента возвращает 404")
  def test_update_nonexistent_student(self, authenticated_api_client, test_data):
    response = authenticated_api_client.update_student(999999, test_data["valid_student"])
    assert response.status_code == 404

  @testit.externalId("API-STU-009")
  @testit.displayName("Токен инвалидируется после logout")
  def test_token_invalid_after_logout(self, authenticated_api_client, registered_admin):
    token = authenticated_api_client.token
    assert token is not None
    logout_response = authenticated_api_client.logout()
    assert logout_response.status_code == 200
    students_response = authenticated_api_client.get_students()
    assert students_response.status_code == 401
