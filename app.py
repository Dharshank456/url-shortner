from flask import Flask, request, redirect, render_template
from database import init_db, get_connection
import random
import string
import validators

app = Flask(__name__)

# Initialize DB safely
init_db()


def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/shorten", methods=["POST"])
def shorten_url():

    original_url = request.form["url"]
    custom_alias = request.form.get("custom_alias")

    # Validate URL
    if not validators.url(original_url):
        return "Invalid URL", 400

    # Decide short code
    short_code = custom_alias.strip() if custom_alias else generate_short_code()

    conn = get_connection()

    # Check if alias already exists
    existing = conn.execute(
        "SELECT short_code FROM urls WHERE short_code = ?",
        (short_code,)
    ).fetchone()

    if existing:
        conn.close()
        return "Alias already exists", 400

    # Insert into DB
    conn.execute(
        "INSERT INTO urls (short_code, original_url) VALUES (?, ?)",
        (short_code, original_url)
    )

    conn.commit()
    conn.close()

    # 🔥 FIX: generate correct EC2/local URL dynamically
    short_url = request.host_url.rstrip("/") + "/" + short_code

    return f"""
    <h2>URL Created Successfully</h2>
    <p><a href="{short_url}">{short_url}</a></p>
    """


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

    # update clicks
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

    return f"""
    <h2>Stats</h2>
    <p>Original URL: {result['original_url']}</p>
    <p>Clicks: {result['clicks']}</p>
    """


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
