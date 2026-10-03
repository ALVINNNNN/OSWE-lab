# OSWE Lab learner guide

These are original, deliberately vulnerable Flask applications for local white-box practice. They are not copies of exam content and are not affiliated with OffSec.

## Start

```bash
git clone https://github.com/ALVINNNNN/OSWE-lab.git
cd OSWE-lab
docker compose up --build -d
docker compose ps
```

Open `http://127.0.0.1:8101`, `:8102`, or `:8103`. Each instance creates a random flag at startup. Keep targets bound to localhost. Reset one target with `docker compose restart recovery` (replace the service name as needed).

## 01 Account Recovery

Request a recovery message for `student`, read the token from `/api/inbox`, and inspect how `/api/reset` uses it. The objective is to access `/api/admin` as `admin`. Skills: source tracing, token ownership, authentication logic, and session handling.

## 02 Report Portal

`/api/search?q=...` returns only `found: true/false`. Build true and false cases, then use a boolean SQL oracle to recover the `vault.secret` value one character at a time. Skills: SQLite syntax, UNION queries, boolean inference, and scripting.

## 03 Template Studio

Sign in with `designer` / `designer-password`. Inspect the profile update and preview handlers. The objective is to reach the editor-only preview and read the flag through server-side template evaluation. Use the HTTP response; do not create a reverse shell. Skills: mass assignment, authorization, Jinja SSTI, and exploit chaining.

## Patched mode

Run `PATCHED=1 docker compose up --build -d` and repeat your exploit. A correct patch should block the attack while preserving normal behavior.

## Safety

Run only in disposable local containers. Do not expose the vulnerable ports to the Internet. The Compose file drops Linux capabilities, uses a non-root user, enables read-only filesystems, and gives each target its own internal network.

