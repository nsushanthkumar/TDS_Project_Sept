from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.api.schemas import GenerateRequest
from app.domain.use_cases import GenerateAndPublishApp
from app.services.llm_service import LLMService
from app.services.repo_service import RepoService
from app.services.notifier import Notifier
from app.services.evidence_logger import EvidenceLogger
from app.infra.settings import get_settings


# Keep the same public route path
api_bp = Blueprint("api", __name__)


@api_bp.route("/api-endpoint", methods=["POST"])
def handle_request():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No JSON data provided"}), 400

    try:
        req_model = GenerateRequest(**data)
    except ValidationError as ve:
        return jsonify({"status": "error", "message": ve.errors()}), 400

    # Secret verification
    if req_model.secret != get_settings().secret:
        return jsonify({"status": "error", "message": "Invalid secret"}), 400

    use_case = GenerateAndPublishApp(LLMService(), RepoService(), Notifier(), EvidenceLogger())
    result = use_case.execute(req_model, request.remote_addr, request.url)
    status_code = 200 if result.get("status") == "success" else 500
    return jsonify(result), status_code
