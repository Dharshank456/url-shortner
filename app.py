from flask import Flask, request, redirect, render_template, jsonify
from database import get_connection
from config import Config

import logging
import random
import string
import validators
import os

app = Flask(__name__)
app.config.from_object(Config)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)


def generate_short_code(length=6):
    return "".join(
        random.choices(
            string.ascii_letters + string.digits,
            k=length
        )
    )


@app.route("/")
def home():
    return render_template(
        "index.html",
        pod_name=os.getenv("HOSTNAME", "unknown-pod"),
        app_name=Config.APP_NAME,
        app_env=Config.APP_ENV,
        app_version=Config.APP_VERSION,
        secret_loaded="YES" if Config.SECRET_KEY else "NO"
    )


# -------------------------
# Kubernetes Health Checks
# -------------------------

@app.route("/health")
def health():
    return jsonify(
        {
            "status": "UP"
        }
    ), 200


@app.route("/ready")
def ready():
    try:
        conn = get_connection()
        conn.close()

        return jsonify(
            {
                "status": "READY"
            }
        ), 200

    except Exception as e:

        logger.error("Database not ready: %s", e)

        return jsonify(
            {
                "status": "NOT READY"
            }
        ), 503


# -------------------------
# URL Shortener
# -------------------------

@app.route("/shorten", methods=["POST"])
def shorten_url():

    original_url = request.form["url"]
    custom_alias = request.form.get("custom_alias")

    if not validators.url(original_url):
        return "Invalid URL", 400

    short_code = (
        custom_alias.strip()
        if custom_alias
        else generate_short_code()
    )

    with get_connection() as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT short_code
                FROM urls
                WHERE short_code=%s
                """,
                (short_code,)
            )

            existing = cur.fetchone()

            if existing:
                return "Alias already exists", 400

            cur.execute(
                """
                INSERT INTO urls
                (short_code, original_url)
                VALUES (%s,%s)
                """,
                (
                    short_code,
                    original_url
                )
            )

        conn.commit()

    logger.info(
        "Created short URL %s",
        short_code
    )

    return render_template(
        "result.html",
        short_code=short_code
    )


@app.route("/<short_code>")
def redirect_to_url(short_code):

    short_code = short_code.strip()

    with get_connection() as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT original_url
                FROM urls
                WHERE short_code=%s
                """,
                (short_code,)
            )

            result = cur.fetchone()

            if result is None:
                return "URL Not Found", 404

            cur.execute(
                """
                UPDATE urls
                SET clicks = clicks + 1
                WHERE short_code=%s
                """,
                (short_code,)
            )

        conn.commit()

    logger.info(
        "Redirected %s",
        short_code
    )

    return redirect(
        result["original_url"]
    )


@app.route("/stats/<short_code>")
def stats(short_code):

    with get_connection() as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT original_url,
                       clicks
                FROM urls
                WHERE short_code=%s
                """,
                (short_code,)
            )

            result = cur.fetchone()

    if result is None:
        return "URL Not Found", 404

    return render_template(
        "stats.html",
        original_url=result["original_url"],
        clicks=result["clicks"]
    )


# -------------------------
# Error Handlers
# -------------------------

@app.errorhandler(404)
def not_found(error):
    return "Page Not Found", 404


@app.errorhandler(500)
def internal_server_error(error):
    logger.exception(error)
    return "Internal Server Error", 500


if __name__ == "__main__":

    logger.info(
        "Starting %s (%s)",
        Config.APP_NAME,
        Config.APP_ENV
    )

    app.run(
        host=Config.HOST,
        port=Config.PORT
    )
