from flask import request, jsonify
from app.api.schemas import GenerateRequest
from app.domain.use_cases import GenerateAndPublishApp
from app.services.llm_service import LLMService
from app.services.repo_service import RepoService
from app.services.notifier import Notifier
from app.services.evidence_logger import EvidenceLogger
def main():
    # Create and run the Flask app via the new factory to keep a single app definition
    from app import create_app

    # validate_config is called inside create_app
    flask_app = create_app()

    from app.infra.settings import get_settings
    s = get_settings()
    port = s.port
    print(f"Starting LLM Code Deployment API on port {port}")
    print(f"API endpoint: http://localhost:{port}/api-endpoint")
    flask_app.run(host="0.0.0.0", port=port, debug=True)


if __name__ == "__main__":
    main()
