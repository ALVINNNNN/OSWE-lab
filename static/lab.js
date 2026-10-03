"use strict";
document.querySelectorAll(".api-form").forEach(form => {
  form.addEventListener("submit", async event => {
    event.preventDefault();
    const output = form.querySelector(".response");
    const button = form.querySelector("button");
    const data = Object.fromEntries(new FormData(form));
    const method = form.dataset.method;
    const url = new URL(form.getAttribute("action"), location.origin);
    const options = {method, credentials: "same-origin"};
    if (method === "GET") url.search = new URLSearchParams(data);
    else { options.headers = {"Content-Type": "application/json"}; options.body = JSON.stringify(data); }
    button.disabled = true;
    output.textContent = "Sending…";
    try {
      const response = await fetch(url, options);
      const body = await response.text();
      let formatted = body;
      try { formatted = JSON.stringify(JSON.parse(body), null, 2); } catch (_) {}
      output.textContent = "HTTP " + response.status + "\n" + formatted;
    } catch (error) { output.textContent = "Request failed: " + error.message; }
    finally { button.disabled = false; }
  });
});
document.querySelector("#flag-form").addEventListener("submit", async event => {
  event.preventDefault();
  const output = document.querySelector("#flag-result");
  try {
    const response = await fetch("/api/submit", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(Object.fromEntries(new FormData(event.target)))});
    const result = await response.json();
    output.textContent = result.message;
    output.className = result.correct ? "success" : "error";
  } catch (_) { output.textContent = "Cannot reach this lab. Check that the container is running."; }
});
