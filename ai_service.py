import json
import os
import time
from collections import defaultdict, deque
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import Flask, jsonify, request
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
ALLOWED_ORIGINS = {item.strip().rstrip("/") for item in os.getenv(
    "FRONTEND_ORIGINS", "https://shreenathx.github.io,http://localhost:8000,http://127.0.0.1:8000"
).split(",") if item.strip()}
MODEL = os.getenv("AI_MODEL", "openrouter/free")
hits = defaultdict(deque)


@app.after_request
def cors(response):
    origin = request.headers.get("Origin", "").rstrip("/")
    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.errorhandler(413)
def too_large(_error):
    return jsonify(error="That request is too large. Please shorten it and try again."), 413


@app.errorhandler(Exception)
def unexpected(error):
    app.logger.exception("Request failed", exc_info=error)
    return jsonify(error="Something went wrong. Please try again."), 500


def rate_limit():
    address = request.remote_addr or "unknown"
    now = time.time()
    recent = hits[address]
    while recent and now - recent[0] > 60:
        recent.popleft()
    if len(recent) >= 12:
        return False
    recent.append(now)
    return True


def body():
    if request.mimetype != "application/json":
        raise ValueError("Send this request as JSON.")
    data = request.get_json(silent=False)
    if not isinstance(data, dict):
        raise ValueError("Request body must be a JSON object.")
    return data


def short_text(value, label, limit, required=True):
    if not isinstance(value, str):
        if required:
            raise ValueError(f"{label} is required.")
        return ""
    value = value.strip()
    if required and not value:
        raise ValueError(f"{label} is required.")
    if len(value) > limit:
        raise ValueError(f"{label} is too long. Please shorten it.")
    return value


def model_json(system, prompt, max_tokens=900):
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("AI is not configured on the server yet.")
    payload = json.dumps({
        "model": MODEL,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
        "temperature": 0.3,
        "max_tokens": max_tokens,
    }).encode("utf-8")
    req = Request("https://openrouter.ai/api/v1/chat/completions", data=payload, headers={
        "Authorization": f"Bearer {api_key}", "Content-Type": "application/json",
        "HTTP-Referer": "https://shreenathx.github.io/HabitFlow_Project/",
        "X-OpenRouter-Title": "Daymark Goal Coach",
    })
    try:
        with urlopen(req, timeout=28) as result:
            response = json.loads(result.read(1_000_000).decode("utf-8"))
        text = response["choices"][0]["message"]["content"]
        if not isinstance(text, str) or not text.strip():
            raise ValueError("The model returned an empty answer.")
        parsed = json.loads(text)
        if not isinstance(parsed, dict):
            raise ValueError("The model response was not an object.")
        return parsed
    except HTTPError as error:
        app.logger.warning("Model provider returned HTTP %s", error.code)
        raise RuntimeError("The AI service is busy or unavailable. Try again shortly.") from error
    except (URLError, TimeoutError, json.JSONDecodeError, KeyError, IndexError, TypeError) as error:
        app.logger.warning("Model provider request failed: %s", type(error).__name__)
        raise RuntimeError("The AI service could not complete that request. Try again shortly.") from error


def validate_origin():
    origin = request.headers.get("Origin", "").rstrip("/")
    if origin and origin not in ALLOWED_ORIGINS:
        return jsonify(error="This site is not allowed to use the coach."), 403
    if not rate_limit():
        return jsonify(error="Too many requests. Please wait a minute and try again."), 429
    return None


@app.get("/")
@app.get("/health")
def health():
    return jsonify(status="ok", ai_configured=bool(os.getenv("OPENROUTER_API_KEY")))


@app.route("/api/plan", methods=["POST", "OPTIONS"])
def plan():
    if request.method == "OPTIONS":
        return "", 204
    blocked = validate_origin()
    if blocked:
        return blocked
    try:
        data = body()
        goal = short_text(data.get("goal"), "Goal", 100)
        duration = data.get("duration_days", 60)
        if not isinstance(duration, int) or not 1 <= duration <= 365:
            raise ValueError("Duration must be between 1 and 365 days.")
        level = short_text(data.get("level", "New to this"), "Starting point", 50)
        minutes = data.get("minutes_per_day", 30)
        if not isinstance(minutes, int) or not 5 <= minutes <= 180:
            raise ValueError("Daily time must be between 5 and 180 minutes.")
        result = model_json(
            "Create a realistic, evidence-aware personal growth outline. Do not invent named resources, credentials, statistics or guarantees. For fitness, use conservative low-risk language and say to stop for pain; no diagnosis or treatment. Do not promise outcomes. Return JSON only with a short summary string and milestones array of 3 to 6 objects, each containing a short title and a focus string. Keep all actions achievable for the stated time and duration.",
            (f"Goal: {goal}\nDuration: {duration} days\nStarting point: {level}\n"
             f"Available most days: {minutes} minutes. Make a flexible plan with milestones that progress from foundations to practice and reflection."),
            850,
        )
        milestones = result.get("milestones")
        if not isinstance(milestones, list) or not 2 <= len(milestones) <= 6:
            raise RuntimeError("The AI returned a plan that needs another try.")
        clean = []
        for milestone in milestones:
            if not isinstance(milestone, dict):
                continue
            title = short_text(milestone.get("title"), "Milestone title", 70)
            focus = short_text(milestone.get("focus"), "Milestone focus", 260)
            clean.append({"title": title, "focus": focus})
        if len(clean) < 2:
            raise RuntimeError("The AI returned an incomplete plan. Try again.")
        summary = result.get("summary", "A flexible plan shaped around small, repeatable actions.")
        return jsonify(summary=short_text(summary, "Summary", 240), milestones=clean)
    except ValueError as error:
        return jsonify(error=str(error)), 400
    except RuntimeError as error:
        return jsonify(error=str(error)), 503


@app.route("/api/challenge", methods=["POST", "OPTIONS"])
def challenge():
    if request.method == "OPTIONS":
        return "", 204
    blocked = validate_origin()
    if blocked:
        return blocked
    try:
        data = body()
        goal = short_text(data.get("goal"), "Goal", 100)
        day = data.get("day", 1)
        duration = data.get("duration_days", 60)
        if not isinstance(day, int) or not 1 <= day <= 365 or not isinstance(duration, int) or not 1 <= duration <= 365:
            raise ValueError("Day and duration must be between 1 and 365.")
        level = short_text(data.get("level", "New to this"), "Starting point", 50)
        minutes = data.get("minutes_per_day", 30)
        if not isinstance(minutes, int) or not 5 <= minutes <= 180:
            raise ValueError("Daily time must be between 5 and 180 minutes.")
        result = model_json(
            "Design one safe and concrete personal growth challenge. Do not invent sources, factual claims or guaranteed outcomes. Fitness tasks must be conservative, accessible, offer rest and advise stopping if pain occurs. Do not prescribe diets, diagnose or treat. The verification should be a simple self-report and never claim external proof. Return JSON with title, instructions, minutes as an integer, and verification. Keep instructions under 450 characters.",
            (f"Goal: {goal}\nPlan day: {day} of {duration}\nStarting point: {level}\n"
             f"Available time: {minutes} minutes. Give one fresh challenge that advances the goal and is feasible today."),
            450,
        )
        title = short_text(result.get("title"), "Challenge title", 90)
        instructions = short_text(result.get("instructions"), "Instructions", 450)
        verification = short_text(result.get("verification"), "Verification", 180)
        task_minutes = result.get("minutes", minutes)
        if not isinstance(task_minutes, int) or not 1 <= task_minutes <= minutes:
            task_minutes = minutes
        return jsonify(title=title, instructions=instructions, verification=verification, minutes=task_minutes)
    except ValueError as error:
        return jsonify(error=str(error)), 400
    except RuntimeError as error:
        return jsonify(error=str(error)), 503


@app.route("/api/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return "", 204
    blocked = validate_origin()
    if blocked:
        return blocked
    try:
        data = body()
        message = short_text(data.get("message"), "Message", 1000)
        goal = short_text(data.get("goal", ""), "Goal", 100, required=False)
        history = data.get("history", [])
        if not isinstance(history, list) or len(history) > 8:
            raise ValueError("Conversation history is invalid.")
        safe_history = []
        for item in history:
            if isinstance(item, dict):
                user = item.get("user", "")
                assistant = item.get("assistant", "")
                if isinstance(user, str) and isinstance(assistant, str):
                    safe_history.extend([{"role": "user", "content": user[:500]}, {"role": "assistant", "content": assistant[:700]}])
        system = "You are Daymark, a practical and kind coach for learning, fitness, habits, creativity and general goals. Be concise, specific and non-judgmental. Ask a useful question when needed. Do not pretend to verify a user's actions. Never invent factual citations or resources. For medical, injury, mental health, legal or financial issues, give general support only and recommend an appropriately qualified professional for important decisions. Avoid strenuous fitness advice and remind users to stop if pain occurs. Return JSON only with one string field named reply."
        context = ([{"role": "system", "content": system + (f" The user's current goal is: {goal}." if goal else "")}]
                   + safe_history + [{"role": "user", "content": message}])
        result = model_json(system, json.dumps(context, ensure_ascii=False), 350)
        reply = result.get("reply")
        if not isinstance(reply, str) or not reply.strip() or len(reply) > 1800:
            raise RuntimeError("The coach returned an incomplete response. Try again.")
        return jsonify(reply=reply.strip())
    except ValueError as error:
        return jsonify(error=str(error)), 400
    except RuntimeError as error:
        return jsonify(error=str(error)), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
