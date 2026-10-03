from app import create_app

def client_for(tmp_path, lab, patched=False):
    return create_app(lab, state_dir=tmp_path / lab, patched=patched).test_client()

def test_recovery_vulnerable_and_patched(tmp_path):
    client = client_for(tmp_path, "recovery")
    client.post("/api/forgot", json={"username": "student"})
    token = client.get("/api/inbox").json["messages"][0]["token"]
    assert client.post("/api/reset", json={"username": "admin", "token": token, "password": "new-admin-password"}).status_code == 200
    assert client.post("/api/login", json={"username": "admin", "password": "new-admin-password"}).status_code == 200
    assert "OSWE{" in client.get("/api/admin").json["flag"]
    patched = client_for(tmp_path, "recovery", True)
    patched.post("/api/forgot", json={"username": "student"})
    token = patched.get("/api/inbox").json["messages"][0]["token"]
    assert patched.post("/api/reset", json={"username": "admin", "token": token, "password": "new-admin-password"}).status_code == 403

def test_reports_oracle_and_parameterization(tmp_path):
    client = client_for(tmp_path, "reports")
    assert client.get("/api/search?q=Quarterly").json["found"] is True
    payload = "x' UNION SELECT secret FROM vault WHERE substr(secret,1,1)='O' --"
    assert client.get("/api/search", query_string={"q": payload}).json["found"] is True
    patched = client_for(tmp_path, "reports", True)
    assert patched.get("/api/search", query_string={"q": payload}).json["found"] is False

def test_studio_chain_and_patched_mode(tmp_path):
    client = client_for(tmp_path, "studio")
    client.post("/api/login", json={"username": "designer", "password": "designer-password"})
    assert client.post("/api/profile", json={"role": "editor"}).json["profile"]["role"] == "editor"
    assert client.post("/api/preview", json={"template": "{{ 7 * 7 }}"}).json["rendered"] == "49"
    patched = client_for(tmp_path, "studio", True)
    patched.post("/api/login", json={"username": "designer", "password": "designer-password"})
    assert patched.post("/api/profile", json={"role": "editor"}).json["profile"]["role"] == "viewer"

