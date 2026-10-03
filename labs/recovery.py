"""Account recovery: trace token ownership across the reset workflow."""
import secrets

from flask import jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

META = {
    "title": "Account Recovery", "number": "01", "level": "Foundation", "time": "30–45 min",
    "subtitle": "One valid token. The wrong identity.",
    "brief": "You are student at Northstar Support. Review the reset flow, take over admin, and retrieve the administrator flag. The inbox simulates mail delivered only to your own account.",
    "hints": ["Follow the token from creation to password replacement.", "Which username does the server associate with the token? Which username controls the update?", "Request a student token, then change the username in the reset request."],
    "forms": [
        {"title": "Request recovery email", "path": "/api/forgot", "fields": {"username": "student"}},
        {"title": "Your inbox", "path": "/api/inbox", "method": "GET", "fields": {}},
        {"title": "Reset password", "path": "/api/reset", "fields": {"username": "student", "token": "", "password": "NewPassword123!"}},
        {"title": "Sign in", "path": "/api/login", "fields": {"username": "student", "password": "student-password"}},
        {"title": "Admin dashboard", "path": "/api/admin", "method": "GET", "fields": {}},
    ],
}


def register(app, directory, flag):
    users = {"student": generate_password_hash("student-password"), "admin": generate_password_hash(secrets.token_hex(24))}
    tokens = {}
    inbox = []

    @app.post("/api/forgot")
    def forgot():
        username = (request.get_json(silent=True) or {}).get("username")
        if username in users:
            token = secrets.token_urlsafe(24)
            tokens[token] = username
            if username == "student":
                inbox.append({"to": "student", "token": token})
        return jsonify(message="If the account exists, a recovery message was sent.")

    @app.get("/api/inbox")
    def mailbox():
        return jsonify(messages=inbox[-10:])

    @app.post("/api/reset")
    def reset():
        body = request.get_json(silent=True) or {}
        token, username, password = body.get("token"), body.get("username"), body.get("password", "")
        if token not in tokens or username not in users or not isinstance(password, str) or len(password) < 8:
            return jsonify(error="Invalid reset request"), 400
        if app.config["PATCHED"] and tokens[token] != username:
            return jsonify(error="Token does not belong to this account"), 403
        # Vulnerability: validity is checked, but token ownership is not bound to the update.
        users[username] = generate_password_hash(password)
        del tokens[token]
        return jsonify(message="Password updated")

    @app.post("/api/login")
    def login():
        body = request.get_json(silent=True) or {}
        username, password = body.get("username", ""), body.get("password", "")
        if username not in users or not check_password_hash(users[username], password):
            return jsonify(error="Invalid credentials"), 401
        session.clear()
        session["user"] = username
        return jsonify(message="Signed in", username=username)

    @app.get("/api/admin")
    def admin():
        if session.get("user") != "admin":
            return jsonify(error="Administrator access required"), 403
        return jsonify(flag=flag)
