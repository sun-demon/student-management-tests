from __future__ import annotations

import uuid
from typing import Any

import requests

from src.utils.config import BASE_URL


class ApiClient:
  def __init__(self, base_url: str = BASE_URL) -> None:
    self.base_url = base_url.rstrip("/")
    self.session = requests.Session()
    self.token: str | None = None

  def reset(self) -> requests.Response:
    return self.session.post(f"{self.base_url}/reset")

  def register(self, username: str | None = None, password: str | None = None) -> requests.Response:
    if username is None:
      username = f"admin_{uuid.uuid4().hex[:8]}"
    if password is None:
      password = "TestPass123!"
    return self.session.post(
      f"{self.base_url}/register",
      json={"username": username, "password": password},
    )

  def login(self, username: str, password: str) -> requests.Response:
    response = self.session.post(
      f"{self.base_url}/login",
      json={"username": username, "password": password},
    )
    if response.ok:
      self.token = response.json().get("access_token")
    return response

  def logout(self) -> requests.Response:
    return self.session.post(
      f"{self.base_url}/logout",
      headers=self._auth_headers(),
    )

  def add_student(self, payload: dict[str, Any]) -> requests.Response:
    return self.session.post(
      f"{self.base_url}/add-user",
      json=payload,
      headers=self._auth_headers(),
    )

  def get_students(self) -> requests.Response:
    return self.session.get(
      f"{self.base_url}/users",
      headers=self._auth_headers(),
    )

  def get_student(self, student_id: int) -> requests.Response:
    return self.session.get(
      f"{self.base_url}/user/{student_id}",
      headers=self._auth_headers(),
    )

  def update_student(self, student_id: int, payload: dict[str, Any]) -> requests.Response:
    return self.session.put(
      f"{self.base_url}/user/{student_id}",
      json=payload,
      headers=self._auth_headers(),
    )

  def delete_student(self, student_id: int) -> requests.Response:
    return self.session.delete(
      f"{self.base_url}/user/{student_id}",
      headers=self._auth_headers(),
    )

  def student_exists(self, full_name: str, age: int, gender: str) -> bool:
    response = self.get_students()
    if not response.ok:
      return False
    for student in response.json():
      if (
        student.get("full_name") == full_name
        and student.get("age") == age
        and student.get("gender") == gender
      ):
        return True
    return False

  def _auth_headers(self) -> dict[str, str]:
    if not self.token:
      return {}
    return {"Authorization": f"Bearer {self.token}"}
