"""Report Portal: a one-bit SQLite oracle, with no reflected query results."""
import sqlite3

from flask import jsonify, request

META = {
    "title": "Report Portal", "number": "02", "level": "Intermediate", "time": "45–90 min",
    "subtitle": "No rows returned. Plenty of information.",
    "brief": "The report search reveals only whether a match exists. Trace its SQL query, build a boolean oracle, and automate extraction of the secret from the vault table. No flag is returned directly by search.",
    "hints": ["Compare requests that must be true and requests that must be false.", "The search term is interpolated inside a LIKE string. SQLite supports UNION and substr().", "A UNION SELECT against vault can produce a row only when a predicate about secret is true. Extract it one character at a time."],
    "forms": [{"title": "Search published reports", "path": "/api/search", "method": "GET", "fields": {"q": "Quarterly"}}],
}


def register(app, directory, flag):
    db_path = directory / "reports.sqlite3"
    with sqlite3.connect(db_path) as db:
        db.executescript("DROP TABLE IF EXISTS reports; DROP TABLE IF EXISTS vault; CREATE TABLE reports(title TEXT, published INTEGER); CREATE TABLE vault(secret TEXT);")
        db.executemany("INSERT INTO reports VALUES (?, ?)", [("Quarterly results", 1), ("Hiring forecast", 1), ("Draft strategy", 0)])
        db.execute("INSERT INTO vault VALUES (?)", (flag,))

    @app.get("/api/search")
    def search():
        term = request.args.get("q", "")
        if len(term) > 500:
            return jsonify(error="Search too long"), 400
        try:
            with sqlite3.connect(db_path) as db:
                if app.config["PATCHED"]:
                    rows = db.execute("SELECT title FROM reports WHERE title LIKE ? AND published = 1", (f"%{term}%",)).fetchone()
                else:
                    # Vulnerability: untrusted text becomes SQL syntax.
                    rows = db.execute(f"SELECT title FROM reports WHERE title LIKE '%{term}%' AND published = 1").fetchone()
            return jsonify(found=rows is not None)
        except sqlite3.Error:
            return jsonify(error="Invalid search"), 400
