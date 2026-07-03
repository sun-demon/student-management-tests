"""Веб-приложение для управления студентами (демо-стенд + API)."""

from __future__ import annotations

import os
import re
import secrets
from datetime import datetime, timezone

from flask import Flask, jsonify, redirect, render_template, request, url_for

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.getenv("SECRET_KEY", "edu-manage-demo-secret")

users_db: dict[str, dict] = {}
students_db: dict[int, dict] = {}
tokens_db: dict[str, str] = {}
next_student_id = 1

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _generate_token() -> str:
    return secrets.token_hex(32)


def _get_bearer_token() -> str | None:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None


def _require_auth():
    token = _get_bearer_token()
    if not token or token not in tokens_db:
        return None
    return tokens_db[token]


def _ui_auth_required() -> str | None:
    token = request.cookies.get("session_token")
    if not token or token not in tokens_db:
        return None
    return tokens_db[token]


def _current_user() -> str | None:
    return _ui_auth_required()


def _redirect_with_ui_session(username: str):
    token = _generate_token()
    tokens_db[token] = username
    response = redirect(url_for("add_user_page"))
    response.set_cookie("session_token", token, httponly=True, samesite="Lax")
    return response


def _stats() -> dict[str, int]:
    students = list(students_db.values())
    return {
        "total": len(students),
        "active": sum(1 for s in students if s.get("is_active")),
        "admins": len(users_db),
    }


def _base_context(**extra):
    return {
        "current_user": _current_user(),
        "stats": _stats(),
        **extra,
    }


def _validate_student_payload(data: dict, partial: bool = False) -> tuple[dict | None, tuple | None]:
    errors: list[str] = []

    full_name = data.get("full_name")
    age = data.get("age")
    gender = data.get("gender")
    enrollment_date = data.get("enrollment_date")
    is_active = data.get("is_active", False)

    if not partial or "full_name" in data:
        if not full_name or not str(full_name).strip():
            errors.append("Поле ФИО обязательно для заполнения")

    if not partial or "age" in data:
        if age is None or age == "":
            errors.append("Поле Возраст обязательно для заполнения")
        else:
            try:
                age = int(age)
                if age < 0:
                    errors.append("Возраст не может быть отрицательным")
            except (TypeError, ValueError):
                errors.append("Возраст должен быть целым числом")

    if not partial or "gender" in data:
        if gender not in ("М", "Ж"):
            errors.append('Поле Пол обязательно (допустимые значения: "М" или "Ж")')

    if enrollment_date:
        if not DATE_PATTERN.match(str(enrollment_date)):
            errors.append("Дата поступления должна быть в формате YYYY-MM-DD")

    if errors:
        return None, (jsonify({"errors": errors}), 400)

    validated: dict = {}
    if not partial or "full_name" in data:
        validated["full_name"] = str(full_name).strip()
    if not partial or "age" in data:
        validated["age"] = int(age)
    if not partial or "gender" in data:
        validated["gender"] = gender
    if not partial or "enrollment_date" in data:
        validated["enrollment_date"] = enrollment_date or None
    if not partial or "is_active" in data:
        validated["is_active"] = bool(is_active)

    return validated, None


def _create_student(validated: dict) -> dict:
    global next_student_id
    student = {
        "id": next_student_id,
        **validated,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    students_db[next_student_id] = student
    next_student_id += 1
    return student


def openapi_document() -> dict:
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "EduManage Student API",
            "description": "API для регистрации администраторов и управления студентами",
            "version": "1.0.0",
        },
        "servers": [{"url": request.host_url.rstrip("/")}],
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            }
        },
        "paths": {
            "/register": {
                "post": {
                    "summary": "Регистрация администратора",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "username": {"type": "string"},
                                        "password": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {"201": {"description": "Created"}},
                }
            },
            "/login": {
                "post": {
                    "summary": "Авторизация",
                    "responses": {"200": {"description": "OK"}},
                }
            },
            "/logout": {
                "post": {
                    "summary": "Выход",
                    "security": [{"bearerAuth": []}],
                    "responses": {"200": {"description": "OK"}},
                }
            },
            "/add-user": {
                "post": {
                    "summary": "Добавить студента",
                    "security": [{"bearerAuth": []}],
                    "responses": {"201": {"description": "Created"}},
                }
            },
            "/users": {
                "get": {
                    "summary": "Список студентов",
                    "security": [{"bearerAuth": []}],
                    "responses": {"200": {"description": "OK"}},
                }
            },
            "/user/{id}": {
                "get": {
                    "summary": "Получить студента",
                    "security": [{"bearerAuth": []}],
                    "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "responses": {"200": {"description": "OK"}, "404": {"description": "Not found"}},
                },
                "put": {
                    "summary": "Обновить студента",
                    "security": [{"bearerAuth": []}],
                    "responses": {"200": {"description": "OK"}, "404": {"description": "Not found"}},
                },
                "delete": {
                    "summary": "Удалить студента",
                    "security": [{"bearerAuth": []}],
                    "responses": {"200": {"description": "OK"}, "404": {"description": "Not found"}},
                },
            },
        },
    }


@app.route("/")
def index():
    return render_template("index.html", active_page="home", **_base_context())


@app.route("/openapi.json")
def openapi_spec():
    return jsonify(openapi_document())


@app.route("/swagger")
def swagger_page():
    return render_template("swagger.html", active_page="swagger", **_base_context())


@app.route("/register", methods=["GET", "POST"], endpoint="register_page")
def register_page():
    if request.method == "POST" and request.is_json:
        data = request.get_json(silent=True) or {}
        username = str(data.get("username", "")).strip()
        password = str(data.get("password", ""))
        if not username or not password:
            return jsonify({"error": "username и password обязательны"}), 400
        if username in users_db:
            return jsonify({"error": "Пользователь уже существует"}), 409
        users_db[username] = {"password": password}
        return jsonify({"message": "Регистрация успешна", "username": username}), 201

    if request.method == "GET":
        return render_template(
            "register.html",
            active_page="register",
            auth_layout=True,
            error=None,
            **_base_context(),
        )

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    if not username or not password:
        return (
            render_template(
                "register.html",
                active_page="register",
                auth_layout=True,
                error="Заполните все поля",
                **_base_context(),
            ),
            400,
        )
    if username in users_db:
        return (
            render_template(
                "register.html",
                active_page="register",
                auth_layout=True,
                error="Пользователь уже существует",
                **_base_context(),
            ),
            409,
        )
    users_db[username] = {"password": password}
    return _redirect_with_ui_session(username)


@app.route("/login", methods=["GET", "POST"], endpoint="login_page")
def login_page():
    if request.method == "POST" and request.is_json:
        data = request.get_json(silent=True) or {}
        username = str(data.get("username", "")).strip()
        password = str(data.get("password", ""))
        user = users_db.get(username)
        if not user or user["password"] != password:
            return jsonify({"error": "Неверные учётные данные"}), 401
        token = _generate_token()
        tokens_db[token] = username
        return jsonify({"access_token": token, "token_type": "Bearer"}), 200

    if request.method == "GET":
        return render_template(
            "login.html",
            active_page="login",
            auth_layout=True,
            error=None,
            **_base_context(),
        )

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    user = users_db.get(username)
    if not user or user["password"] != password:
        return (
            render_template(
                "login.html",
                active_page="login",
                auth_layout=True,
                error="Неверные учётные данные",
                **_base_context(),
            ),
            401,
        )

    return _redirect_with_ui_session(username)


@app.post("/logout")
def logout_api():
    token = _get_bearer_token()
    if token and token in tokens_db:
        del tokens_db[token]
    return jsonify({"message": "Выход выполнен"}), 200


@app.route("/add-user", methods=["GET", "POST"], endpoint="add_user_page")
def add_user_page():
    if request.method == "POST" and request.is_json:
        if not _require_auth():
            return jsonify({"error": "Требуется авторизация"}), 401
        data = request.get_json(silent=True) or {}
        validated, error_response = _validate_student_payload(data)
        if error_response:
            return error_response
        return jsonify(_create_student(validated)), 201

    if not _ui_auth_required():
        return redirect(url_for("login_page"))

    if request.method == "GET":
        return render_template(
            "add_user.html",
            active_page="add",
            error=None,
            success=None,
            form_data=None,
            **_base_context(),
        )

    payload = {
        "full_name": request.form.get("full_name"),
        "age": request.form.get("age"),
        "gender": request.form.get("gender"),
        "enrollment_date": request.form.get("enrollment_date"),
        "is_active": request.form.get("is_active") == "on",
    }
    validated, error_response = _validate_student_payload(payload)
    if error_response:
        body, status = error_response
        error_data = body.get_json()
        error_text = "; ".join(error_data.get("errors", ["Ошибка валидации"]))
        return (
            render_template(
                "add_user.html",
                active_page="add",
                error=error_text,
                success=None,
                form_data=payload,
                **_base_context(),
            ),
            status,
        )

    student = _create_student(validated)
    return render_template(
        "add_user.html",
        active_page="add",
        error=None,
        success=f"Студент «{student['full_name']}» успешно добавлен",
        form_data=None,
        **_base_context(),
    )


@app.get("/logout-ui", endpoint="logout_ui")
def logout_ui():
    token = request.cookies.get("session_token")
    if token and token in tokens_db:
        del tokens_db[token]
    response = redirect(url_for("login_page"))
    response.delete_cookie("session_token")
    return response


@app.get("/users")
def list_users_api():
    if not _require_auth():
        return jsonify({"error": "Требуется авторизация"}), 401
    return jsonify(list(students_db.values())), 200


@app.route("/users-page", endpoint="users_page")
def users_page():
    if not _ui_auth_required():
        return redirect(url_for("login_page"))

    students = sorted(students_db.values(), key=lambda s: s["id"], reverse=True)
    return render_template(
        "users.html",
        active_page="students",
        students=students,
        **_base_context(),
    )


@app.post("/delete-user/<int:user_id>", endpoint="delete_user_ui")
def delete_user_ui(user_id: int):
    if not _ui_auth_required():
        return redirect(url_for("login_page"))
    students_db.pop(user_id, None)
    return redirect(url_for("users_page"))


@app.get("/user/<int:user_id>")
def get_user_api(user_id: int):
    if not _require_auth():
        return jsonify({"error": "Требуется авторизация"}), 401
    student = students_db.get(user_id)
    if not student:
        return jsonify({"error": "Пользователь не найден"}), 404
    return jsonify(student), 200


@app.put("/user/<int:user_id>")
def update_user_api(user_id: int):
    if not _require_auth():
        return jsonify({"error": "Требуется авторизация"}), 401
    student = students_db.get(user_id)
    if not student:
        return jsonify({"error": "Пользователь не найден"}), 404

    data = request.get_json(silent=True) or {}
    validated, error_response = _validate_student_payload(data, partial=True)
    if error_response:
        return error_response

    student.update(validated)
    students_db[user_id] = student
    return jsonify(student), 200


@app.delete("/user/<int:user_id>")
def delete_user_api(user_id: int):
    if not _require_auth():
        return jsonify({"error": "Требуется авторизация"}), 401
    if user_id not in students_db:
        return jsonify({"error": "Пользователь не найден"}), 404
    del students_db[user_id]
    return jsonify({"message": "Удалено"}), 200


@app.post("/reset")
def reset_state():
    """Служебный эндпоинт для сброса состояния между автотестами."""
    users_db.clear()
    students_db.clear()
    tokens_db.clear()
    global next_student_id
    next_student_id = 1
    return jsonify({"message": "Состояние сброшено"}), 200


def create_app() -> Flask:
    return app


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
