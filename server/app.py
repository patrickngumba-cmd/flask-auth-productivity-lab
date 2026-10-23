from flask import request, session, make_response, jsonify
from flask_restful import Resource

from config import app, db, api
from models import User, Note
from schemas import user_schema, note_schema, notes_schema


class Signup(Resource):
    def post(self):
        data = request.get_json()
        if not data:
            return {"error": "No input data provided"}, 400

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return {"error": "Username and password are required"}, 400

        if User.query.filter_by(username=username).first():
            return {"error": "Username already exists"}, 422

        try:
            new_user = User(username=username)
            new_user.password_hash = password
            db.session.add(new_user)
            db.session.commit()

            session['user_id'] = new_user.id
            return user_schema.dump(new_user), 201
        except ValueError as err:
            db.session.rollback()
            return {"error": str(err)}, 422


class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {"error": "Unauthorized"}, 401

        user = User.query.filter_by(id=user_id).first()
        if not user:
            return {"error": "Unauthorized"}, 401

        return user_schema.dump(user), 200


class Login(Resource):
    def post(self):
        data = request.get_json()
        if not data:
            return {"error": "No input data provided"}, 400

        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if user and password and user.authenticate(password):
            session['user_id'] = user.id
            return user_schema.dump(user), 200

        return {"error": "Invalid username or password"}, 401


class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session['user_id'] = None
            return {}, 204
        return {"error": "Unauthorized"}, 401


api.add_resource(Signup, '/signup')
api.add_resource(CheckSession, '/check_session', '/me')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
