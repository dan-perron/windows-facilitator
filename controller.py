from flask import request, jsonify
from agent.service import find_and_click, simulate_ootp_workflow, check_ootp_window
from agent.commish_config import CommishHomeCheckboxConfig

def register_routes(app):
    @app.route("/click", methods=["POST"])
    def click():
        data = request.get_json()
        x = data.get("x")
        y = data.get("y")
        if x is None or y is None:
            return jsonify({"status": "error", "message": "Missing coordinates"}), 400
        try:
            import pyautogui
            pyautogui.click(x, y)
            return jsonify({"status": "clicked", "x": x, "y": y})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/health", methods=["GET"])
    def health():
        success, message = check_ootp_window()
        if success:
            return jsonify({"status": "ok", "message": message})
        return jsonify({"status": "error", "message": message}), 503

    @app.route("/simulate", methods=["POST"])
    def simulate():
        data = request.get_json() or {}
        app.logger.info(f"Received /simulate body: {data}")
        checkboxes = data.get("commish_checkboxes", {})
        manual_import_teams = data.get("manual_import_teams", False)
        backup_league_folder = data.get("backup_league_folder", True)
        dry_run = data.get("dry_run", False)
        try:
            config = CommishHomeCheckboxConfig(**checkboxes)
            result, status = simulate_ootp_workflow(config, manual_import_teams, backup_league_folder, dry_run)
            return jsonify(result), status
        except Exception as e:
            error_message = str(e)
            app.logger.error(f"Error in simulate endpoint: {error_message}")
            return jsonify({
                "status": "error",
                "message": error_message
            }), 500 