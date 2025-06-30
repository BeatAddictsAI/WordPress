from flask import Flask, request, jsonify, send_file
import os
import shutil
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Mock Stripe validation for environments missing SSL support
PLATINUM_CUSTOMER_IDS = {"cus_platinum_test1", "cus_platinum_test2"}

@app.route('/export_daw', methods=['POST'])
def export_daw():
    data = request.json
    customer_id = data.get("customer_id")

    if customer_id not in PLATINUM_CUSTOMER_IDS:
        return jsonify({"error": "Platinum tier required"}), 403

    als_template_path = "daw_templates/musicgen_template.als"
    output_path = "static/outputs/exported_project.als"

    try:
        shutil.copy(als_template_path, output_path)
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": f"File operation failed: {str(e)}"}), 500
