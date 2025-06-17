from flask import Blueprint, jsonify, request, current_app as app
from ..extensions import auth, db

questions_bp = Blueprint('questions', __name__, url_prefix='/questions')

@questions_bp.route('', methods=['GET'])
@auth.login_required
def list_questions():
    return jsonify({'message': '總共有5個問題，用 /questions/<id> 取得問題內容'}), 200

@questions_bp.route('/<int:id>', methods=['GET'])
@auth.login_required
def get_question(id):
    try:
        text = open(f'questions/Q{id}.txt','r',encoding='utf-8').read()
        return jsonify({'id': id, 'question': text}), 200
    except FileNotFoundError:
        return jsonify({'error':'問題不存在'}), 404

@questions_bp.route('/<int:id>', methods=['POST'])
@auth.login_required
def answer_question(id):
    user = auth.current_user()
    if not user:
        return jsonify({'error': '未登入或無效的用戶'}), 401
    
    data = request.get_json() or {}
    ans  = data.get('answer')
    if not ans:
        return jsonify({'error':'請提供答案'}), 400
    
    try:
        with open(f'questions/Ans{id}.txt', 'r', encoding='utf-8') as f:
            correct_answer = f.read().strip()
        app.logger.debug(f"Loaded correct answer for question {id}")
    except FileNotFoundError:
        app.logger.error(f"Answer file Ans{id}.txt not found")
        return jsonify({'error': '答案檔案不存在', 'message': f'找不到問題 {id} 的答案檔案'}), 404
    except Exception as e:
        app.logger.error(f"Error reading answer for question {id}: {str(e)}")
        return jsonify({'error': '讀取答案失敗', 'message': str(e)}), 500

    if ans.strip() == correct_answer:
        old_iq = user.iq
        user.iq += 10
        db.session.commit()
        app.logger.info(f"User {user.username} answered question {id} correctly. IQ: {old_iq} -> {user.iq}")
        return jsonify({'message': '回答正確！你的 IQ 增加了 10', 'new_iq': user.iq}), 200
    else:
        app.logger.info(f"User {user.username} answered question {id} incorrectly")
        return jsonify({'error': '回答錯誤', 'message': '答案不正確，請再試一次'}), 400

