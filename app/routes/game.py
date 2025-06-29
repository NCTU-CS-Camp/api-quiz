from flask import Blueprint, jsonify, request, current_app as app
from ..extensions import auth, db, limiter
from ..models import User  # 移除 AIConversation
from flask_limiter.util import get_remote_address
import json
import os
import requests
from dotenv import load_dotenv

game_bp = Blueprint('ai_game', __name__, url_prefix='/ai-game')

# Load environment variables
load_dotenv()

def get_gemini_response(user_input, system_prompt, api_key):
    """Call Gemini API and return response"""
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "system_instruction": {
            "parts": [
                {"text": system_prompt}
            ]
        },
        "contents": [
            {
                "parts": [
                    {"text": user_input}
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        result = response.json()
        
        # Extract Gemini response content
        output = result["candidates"][0]["content"]["parts"][0]["text"]
        return output
    except Exception as e:
        app.logger.error(f"Gemini API error: {str(e)}")
        return f"AI服務暫時無法使用: {str(e)}"


@game_bp.route('/level/<int:level_num>', methods=['POST'])
@limiter.limit("20 per minute", key_func=get_remote_address)
@auth.login_required
def chat_with_ai_level(level_num):
    """直接回傳 output prompt，不做升級判斷。"""
    user = auth.current_user()
    if not user:
        return jsonify({'error': '未登入或無效的用戶'}), 401
    data = request.get_json() or {}
    user_input = data.get('message', '').strip()
    if not user_input:
        return jsonify({'error': '請提供訊息內容'}), 400
    # 取得 API key
    try:
        api_keys_path = os.path.join(app.root_path, 'api_keys.json')
        with open(api_keys_path, 'r', encoding='utf-8') as f:
            api_keys = json.load(f)
        if not api_keys:
            return jsonify({'error': '沒有可用的 API key'}), 500
        import random
        api_key = random.choice(api_keys)
    except Exception as e:
        app.logger.error(f"Failed to load api_keys.json: {str(e)}")
        return jsonify({'error': 'AI 金鑰設定錯誤', 'message': str(e)}), 500
    # 取得 level 設定
    try:
        levels_path = os.path.join(app.root_path, 'levels.json')
        with open(levels_path, 'r', encoding='utf-8') as f:
            levels_data = json.load(f)
    except Exception as e:
        app.logger.error(f"Failed to load levels.json: {str(e)}")
        return jsonify({'error': '系統設定錯誤'}), 500
    level_str = str(level_num)
    if level_str not in levels_data:
        return jsonify({'error': f'無效的AI等級: {level_num}'}), 400
    level_config = levels_data[level_str]
    system_prompt = level_config["system_prompt"]
    # 呼叫 Gemini
    ai_output = get_gemini_response(user_input, system_prompt, api_key)
    return jsonify({'output': ai_output}), 200

@game_bp.route('/level/info', methods=['GET'])
@auth.login_required
def level_info():
    """取得指定 level 或目前 user 的 game_level 對應的 levels.json 設定"""
    user = auth.current_user()
    if not user:
        return jsonify({'error': '未登入或無效的用戶'}), 401
    # 取得 query string level
    target_level = request.args.get('level', type=int)
    # 取得 levels.json 設定
    try:
        levels_path = os.path.join(app.root_path, 'levels.json')
        with open(levels_path, 'r', encoding='utf-8') as f:
            levels_data = json.load(f)
        if target_level is not None:
            level_str = str(target_level)
            if level_str not in levels_data:
                return jsonify({'error': f'無效的AI等級: {target_level}'}), 400
            level_info = levels_data[level_str]
            return jsonify({'level': target_level, 'level_info': level_info}), 200
        else:
            game_level = user.game_level
            level_str = str(game_level)
            if level_str not in levels_data:
                return jsonify({'error': f'無效的AI等級: {game_level}'}), 400
            level_info = levels_data[level_str]
            return jsonify({'game_level': game_level, 'level_info': level_info}), 200
    except Exception as e:
        app.logger.error(f"Failed to load levels.json: {str(e)}")
        return jsonify({'error': '系統設定錯誤'}), 500

@game_bp.route('/level/upgrade', methods=['POST'])
@auth.login_required
def upgrade_level():
    """驗證密碼並升級關卡，max game_level is 3, upgrade to 4 returns win_game。"""
    user = auth.current_user()
    if not user:
        return jsonify({'error': '未登入或無效的用戶'}), 401
    data = request.get_json() or {}
    answer = data.get('answer', '').strip()
    # 取得目前關卡
    game_level = user.game_level
    # 取得 secret
    try:
        levels_path = os.path.join(app.root_path, 'levels.json')
        with open(levels_path, 'r', encoding='utf-8') as f:
            levels_data = json.load(f)
        level_str = str(game_level)
        if level_str not in levels_data:
            return jsonify({'error': f'無效的AI等級: {game_level}'}), 400
        secret = levels_data[level_str]["secret"]
    except Exception as e:
        app.logger.error(f"Failed to load levels.json: {str(e)}")
        return jsonify({'error': '系統設定錯誤'}), 500
    # 檢查答案
    correct = (answer.lower().strip() == secret.lower().strip())
    win_game = False
    if correct:
        if user.game_level < 3:
            user.game_level += 1
            db.session.commit()
        elif user.game_level == 3:
            win_game = True
    return jsonify({
        'correct': correct,
        'game_level': user.game_level,
        'win_game': win_game
    }), 200

@game_bp.route('/level/check', methods=['GET'])
@auth.login_required
def check_level_get():
    """GET 方式驗證指定 level 的密碼，不會升級 user 狀態，僅回傳正確與否。"""
    user = auth.current_user()
    if not user:
        return jsonify({'error': '未登入或無效的用戶'}), 401
    level = request.args.get('level', type=int)
    answer = request.args.get('answer', '').strip()
    if not level or not answer:
        return jsonify({'error': '缺少 level 或 answer'}), 400
    try:
        levels_path = os.path.join(app.root_path, 'levels.json')
        with open(levels_path, 'r', encoding='utf-8') as f:
            levels_data = json.load(f)
        level_str = str(level)
        if level_str not in levels_data:
            return jsonify({'error': f'無效的AI等級: {level}'}), 400
        secret = levels_data[level_str]["secret"]
    except Exception as e:
        app.logger.error(f"Failed to load levels.json: {str(e)}")
        return jsonify({'error': '系統設定錯誤'}), 500
    correct = (answer.lower().strip() == secret.lower().strip())
    return jsonify({
        'level': level,
        'correct': correct
    }), 200
