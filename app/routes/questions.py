from flask import Blueprint, jsonify, request, current_app as app
from ..extensions import auth, db, limiter
from ..models import UserAnswer, User, Favorite
from flask_limiter.util import get_remote_address

questions_bp = Blueprint('questions', __name__, url_prefix='/questions')

@questions_bp.route('/', methods=['GET'])
@auth.login_required
def list_questions():
    return jsonify({'message': '總共有5個問題，用 /questions/<id> 取得問題內容'}), 200

@questions_bp.route('/<int:id>', methods=['GET', 'POST'])
@limiter.limit("10 per minute", methods=["POST"], key_func=get_remote_address)
@auth.login_required
def manage_questions(id):
    if request.method == 'GET':
        try:
            text = open(f'{app.root_path}/questions/Q{id}.txt','r',encoding='utf-8').read()
            return jsonify({'id': id, 'question': text}), 200
        except FileNotFoundError:
            return jsonify({'error':'問題不存在'}), 404
    
    elif request.method == 'POST':
        user = auth.current_user()
        if not user:
            return jsonify({'error': '未登入或無效的用戶'}), 401
        
        if id == 1:
            data = request.get_json() or {}
            fav = data.get('answer', '').strip()
            if not fav:
                return jsonify({'error': '請提供您最喜歡的隊輔名稱'}), 400

            # （如要確保每人只能存一次，可先刪除舊紀錄）
            Favorite.query.filter_by(user_id=user.id).delete()

            record = Favorite(user_id=user.id, favorite_name=fav)
            db.session.add(record)
            db.session.commit()

            return jsonify({
                'message': '最喜歡的隊輔已送出',
                'favorite': fav
            }), 200
        
        data = request.get_json() or {}
        ans  = data.get('answer')
        if not ans:
            return jsonify({'error':'請提供答案'}), 400
        
        try:
            with open(f'{app.root_path}/questions/Ans{id}.txt', 'r', encoding='utf-8') as f:
                correct_answer = f.read().strip()
            app.logger.debug(f"Loaded correct answer for question {id}")
        except FileNotFoundError:
            app.logger.error(f"Answer file Ans{id}.txt not found")
            return jsonify({'error': '答案檔案不存在', 'message': f'找不到問題 {id} 的答案檔案'}), 404
        except Exception as e:
            app.logger.error(f"Error reading answer for question {id}: {str(e)}")
            return jsonify({'error': '讀取答案失敗', 'message': str(e)}), 500

        if ans.strip().lower() == correct_answer.lower():
            # Check if user has already answered this question
            existing = UserAnswer.query.filter_by(user_id=user.id, question_id=id).first()
            if existing:
                return jsonify({'error': '已經回答過此題，無法重複得分'}), 400
            
            # record answer
            record = UserAnswer(user_id=user.id, question_id=id)
            db.session.add(record)
            old_iq = user.iq
            user.iq += 10
            db.session.commit()
            app.logger.debug(f"User {user.username} answered question {id} correctly. IQ: {old_iq} -> {user.iq}")
            return jsonify({'message': '回答正確！你的 IQ 增加了 10', 'new_iq': user.iq}), 200
        else:
            app.logger.debug(f"User {user.username} answered question {id} incorrectly")
            return jsonify({'error': '回答錯誤', 'message': '答案不正確，請再試一次'}), 400


@questions_bp.route('/1/favorites', methods=['GET'])
def favorite_stats():
    # 查詢所有 favorite_name 及其計數
    stats = (
        db.session.query(
            Favorite.favorite_name,
            db.func.count(Favorite.id).label('count')
        )
        .group_by(Favorite.favorite_name)
        .all()
    )
    # 組成 JSON
    result = [{'name': name, 'count': cnt} for name, cnt in stats]
    return jsonify(result), 200