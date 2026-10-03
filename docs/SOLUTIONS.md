# Solutions (spoilers)

Only read this after attempting the lab.

## 01 Account Recovery

`/api/forgot` creates a token for `student` and stores the token owner. The reset handler checks that the token exists but, in vulnerable mode, updates whichever username is supplied. Request a student token, then submit that token with `username=admin` and a password you choose. Sign in as admin and call `/api/admin`.

Fix: bind the token to the account being changed and consume it only after checking `tokens[token] == username`. Also use single-use, expiring tokens and generic responses.

## 02 Report Portal

The query is `SELECT title FROM reports WHERE title LIKE '%<input>%' AND published = 1`. A UNION boolean oracle can ask whether a predicate about `vault.secret` is true. Automate positions and candidates by checking the JSON `found` bit.

Fix: parameterize the LIKE value (`LIKE ?`) and keep the query structure constant. Validate length and log rejected inputs without returning SQL errors.

## 03 Template Studio

The profile endpoint accepts arbitrary JSON keys, so set `role` to `editor`. The preview endpoint then compiles attacker-controlled text with Jinja. A template can reach Python objects through Jinja's object graph and invoke a subprocess to read the flag; keep the payload local and return command output in the response.

Fix: allowlist editable profile fields and derive authorization from server-side state. Render user text as data inside a fixed template; never compile it as a template.

