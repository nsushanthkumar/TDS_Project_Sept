from flask import Flask, jsonify
from app.infra.logging import setup_logging


def create_app() -> Flask:
    # Lazy import to avoid circular dependencies
    from app.api.routes import api_bp
    from app.infra.settings import validate_required_env

    # Validate configuration at startup and set up logging
    validate_required_env()
    setup_logging()

    app = Flask(__name__)

    # Health endpoint
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "healthy"}), 200

    # Register API blueprint (keeps path as /api-endpoint)
    app.register_blueprint(api_bp)

    return app
