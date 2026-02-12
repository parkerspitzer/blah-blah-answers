import logging

from flask import Flask

from app import config
from app.sms import sms_bp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def create_app():
    app = Flask(__name__)
    app.register_blueprint(sms_bp)

    @app.route("/health")
    def health():
        return {"status": "ok", "provider": config.AI_PROVIDER}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host=config.HOST, port=config.PORT)
