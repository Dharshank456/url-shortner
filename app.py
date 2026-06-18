from flask import Flask, request, redirect, render_template
from database import init_db, get_connection
import random
import string
import validators
import os

app = Flask(__name__)


# ✅ IMPORTANT: DO NOT RUN DB INIT AT IMPORT TIME IN CI
# Run only when explicitly enabled
if os.getenv("INIT_DB", "0") == "1":
    init_db()


def generate_short_code(length=6):
    return ''.join(
        random.choices(string.ascii_letters + string.digits, k=length)
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/shorten", methods=["POST"])
def shorten_url():

    original_url = request.form["url"]
    custom_alias = request.form.get("custom_alias")

    if not validators.url(original_url):
        return "Invalid URL", 400

    short_code = custom_alias.strip() if custom_alias else generate_short_code()

    conn = get_connection()

    existing = conn.execute(
        "SELECT short_code FROM urls WHERE short_code = ?",
        (short_code,)
    ).fetchone()

    if existing:
        conn.close()
        return "Alias already exists", 400

    conn.execute(
        "INSERT INTO urls (short_code, original_url) VALUES (?, ?)",
        (short_code, original_url)
    )

    conn.commit()
    conn.close()

    return render_template("result.html", short_code=short_code)


@app.route("/<short_code>")
def redirect_to_url(short_code):

    short_code = short_code.strip()

    conn = get_connection()

    result = conn.execute(
        "SELECT original_url FROM urls WHERE short_code = ?",
        (short_code,)
    ).fetchone()

    if result is None:
        conn.close()
        return "URL Not Found", 404

    conn.execute(
        "UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?",
        (short_code,)
    )

    conn.commit()
    conn.close()

    return redirect(result["original_url"])


@app.route("/stats/<short_code>")
def stats(short_code):

    short_code = short_code.strip()

    conn = get_connection()

    result = conn.execute(
        "SELECT original_url, clicks FROM urls WHERE short_code = ?",
        (short_code,)
    ).fetchone()

    conn.close()

    if result is None:
        return "URL Not Found", 404

    return render_template(
        "stats.html",
        original_url=result["original_url"],
        clicks=result["clicks"]
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
