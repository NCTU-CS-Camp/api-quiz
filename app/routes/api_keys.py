from flask import Blueprint, jsonify, current_app as app
import os, json, random

api_keys_bp = Blueprint('api_keys', __name__, url_prefix='/api-key')

@api_keys_bp.before_app_request
def load_api_keys():
    """啟動時讀一次 JSON 檔到 app.config"""
    path = os.path.join(app.root_path, 'api_keys.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            app.config['API_KEYS_LIST'] = json.load(f)
    except Exception as e:
        app.logger.error(f"讀取 api_keys.json 失敗：{e}")
        app.config['API_KEYS_LIST'] = []

@api_keys_bp.route('/', methods=['GET'])
def get_random_api_key():
    keys = app.config.get('API_KEYS_LIST', [])
    if not keys:
        return jsonify({'error': '沒有可用的 API key'}), 500
    return jsonify({'api_key': random.choice(keys)}), 200
