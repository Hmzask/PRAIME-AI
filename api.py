from flask import Blueprint , jsonify, request
from Database import User_cred


api = Blueprint('api',__name__)
    
@api.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User_cred.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict())


@api.route('/api/users',methods=['GET'])
def get_all_users():
    users = User_cred.query.all()
    if not users:
        return jsonify({'Error':'No users '}), 404
    return jsonify([u.to_dict()for u in users])


@api.route('/api/ask', methods=['POST'])
def ask_model():
    from app import model
    data = request.get_json() # setting up data to accept the coming data in json format.
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    try:
        response = model.generate_content(prompt)
        return jsonify({'response': response.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
