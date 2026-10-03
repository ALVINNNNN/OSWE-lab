"""Shared lab shell; each container runs exactly one selected challenge."""
import importlib
import os
import secrets
from pathlib import Path

from flask import Flask, abort, jsonify, render_template, request

LABS = ("recovery", "reports", "studio")


def create_app(lab_id=None, state_dir=None, patched=None):
    lab_id = lab_id or os.environ.get("LAB_ID", "recovery")
    if lab_id not in LABS:
        raise ValueError("Unknown lab")
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=secrets.token_hex(32),
        SESSION_COOKIE_NAME=f"oswe_{lab_id}",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Strict",
        MAX_CONTENT_LENGTH=16_384,
        PATCHED=(os.environ.get("PATCHED", "0") == "1") if patched is None else patched,
    )
    directory = Path(state_dir or os.environ.get("STATE_DIR", "/tmp/oswe-state"))
    directory.mkdir(parents=True, exist_ok=True)
    flag = f"OSWE{{{secrets.token_hex(12)}}}"
    flag_path = directory / "flag.txt"
    flag_path.write_text(flag, encoding="utf-8")
    flag_path.chmod(0o600)
    app.config["FLAG_PATH"] = str(flag_path)
    module = importlib.import_module(f"labs.{lab_id}")
    module.register(app, directory, flag)

    @app.before_request
    def same_origin():
        # Do not let unrelated websites POST into a learner's localhost target.
        origin = request.headers.get("Origin")
        if request.method not in ("GET", "HEAD", "OPTIONS") and origin and origin != request.host_url.rstrip("/"):
            abort(403)

    @app.after_request
    def headers(response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    @app.get("/")
    def index():
        return render_template("lab.html", lab=module.META, lab_id=lab_id, patched=app.config["PATCHED"])

    @app.get("/health")
    def health():
        return jsonify(status="ok", lab=lab_id, patched=app.config["PATCHED"])

    @app.get("/source")
    def source():
        # Explicit allowlist: no user-controlled file paths.
        name = request.args.get("file", "lab")
        paths = {"lab": Path(module.__file__), "shell": Path(__file__)}
        if name not in paths:
            abort(404)
        return app.response_class(paths[name].read_text(), mimetype="text/plain")

    @app.post("/api/submit")
    def submit():
        supplied = str((request.get_json(silent=True) or {}).get("flag", ""))
        correct = secrets.compare_digest(supplied.encode(), flag.encode())
        return jsonify(correct=correct, message="Flag accepted. Now patch the root cause." if correct else "Incorrect flag; try again."), 200 if correct else 400

    return app
