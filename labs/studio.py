"""Template Studio: chain mass assignment with server-side template injection."""
import secrets

from flask import jsonify, render_template_string, request, session

META = {
    "title": "Template Studio", "number": "03", "level": "Intermediate", "time": "60–90 min",
    "subtitle": "A profile edit becomes a server-side foothold.",
    "brief": "Sign in as designer, review the profile update and preview handlers, and chain two bugs to execute a harmless command inside your disposable target. Retrieve the flag from /tmp/oswe-state/flag.txt. Do not use a reverse shell; the HTTP response is sufficient.",
    "hints": ["Compare the fields accepted by profile updates with those used for authorization.", "Can you update role to editor? Test a harmless arithmetic expression in preview.", "The Jinja template is compiled from your input. Trace accessible template globals to a command execution primitive, then read the local flag file."],
    "forms": [
        {"title": "Sign in", "path": "/api/login", "fields": {"username": "designer", "password": "designer-password"}},
        {"title": "Update profile", "path": "/api/profile", "fields": {"display_name": "Designer", "role": "viewer"}},
        {"title": "Preview template", "path": "/api/preview", "fields": {"template": "Hello {{ name }}"}},
    ],
}


def register(app, directory, flag):
    profiles = {}

    @app.post("/api/login")
    def login():
        body = request.get_json(silent=True) or {}
        if body.get("username") != "designer" or body.get("password") != "designer-password":
            return jsonify(error="Invalid credentials"), 401
        session.clear()
        sid = secrets.token_hex(16)
        session["sid"] = sid
        profiles[sid] = {"display_name": "Designer", "role": "viewer"}
        return jsonify(profile=profiles[sid])

    @app.post("/api/profile")
    def profile():
        current = profiles.get(session.get("sid"))
        if current is None:
            return jsonify(error="Sign in first"), 401
        body = request.get_json(silent=True) or {}
        if app.config["PATCHED"]:
            if "display_name" in body:
                current["display_name"] = str(body["display_name"])[:80]
        else:
            # Vulnerability 1: authorization fields are writable by the user.
            current.update(body)
        return jsonify(profile=current)

    @app.post("/api/preview")
    def preview():
        current = profiles.get(session.get("sid"))
        if not current:
            return jsonify(error="Sign in first"), 401
        if current.get("role") != "editor":
            return jsonify(error="Editor role required"), 403
        template = str((request.get_json(silent=True) or {}).get("template", ""))
        if app.config["PATCHED"]:
            # User input stays data in a fixed template; never recompile it as code.
            rendered = render_template_string("{{ text }}", text=template)
        else:
            # Vulnerability 2: attacker-controlled text becomes Jinja code.
            rendered = render_template_string(template, name=current.get("display_name"))
        return jsonify(rendered=rendered)
