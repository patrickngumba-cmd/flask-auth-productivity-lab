from flask import request, session
from flask_restful import Resource
from marshmallow import ValidationError

from config import app, db, api
from models import User, Note
from schemas import user_schema, note_schema, notes_schema


def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.filter_by(id=user_id).first()


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
        user = get_current_user()
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


class NoteList(Resource):
    def get(self):
        user = get_current_user()
        if not user:
            return {"error": "Unauthorized"}, 401

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)

        pagination = Note.query.filter_by(user_id=user.id).order_by(Note.id.asc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return {
            "notes": notes_schema.dump(pagination.items),
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "total_pages": pagination.pages
        }, 200

    def post(self):
        user = get_current_user()
        if not user:
            return {"error": "Unauthorized"}, 401

        data = request.get_json()
        if not data:
            return {"error": "No input data provided"}, 400

        try:
            validated = note_schema.load(data)
            new_note = Note(
                title=validated['title'],
                content=validated['content'],
                user_id=user.id
            )
            db.session.add(new_note)
            db.session.commit()
            return note_schema.dump(new_note), 201
        except ValidationError as err:
            return {"errors": err.messages}, 400
        except ValueError as err:
            db.session.rollback()
            return {"error": str(err)}, 400


class NoteDetail(Resource):
    def get(self, id):
        user = get_current_user()
        if not user:
            return {"error": "Unauthorized"}, 401

        note = Note.query.filter_by(id=id, user_id=user.id).first()
        if not note:
            return {"error": "Note not found"}, 404

        return note_schema.dump(note), 200

    def patch(self, id):
        user = get_current_user()
        if not user:
            return {"error": "Unauthorized"}, 401

        note = Note.query.filter_by(id=id, user_id=user.id).first()
        if not note:
            return {"error": "Note not found"}, 404

        data = request.get_json()
        if not data:
            return {"error": "No input data provided"}, 400

        try:
            if 'title' in data:
                note.title = data['title']
            if 'content' in data:
                note.content = data['content']

            db.session.commit()
            return note_schema.dump(note), 200
        except ValueError as err:
            db.session.rollback()
            return {"error": str(err)}, 400

    def delete(self, id):
        user = get_current_user()
        if not user:
            return {"error": "Unauthorized"}, 401

        note = Note.query.filter_by(id=id, user_id=user.id).first()
        if not note:
            return {"error": "Note not found"}, 404

        db.session.delete(note)
        db.session.commit()
        return {"message": "Note deleted successfully"}, 200


api.add_resource(Signup, '/signup')
api.add_resource(CheckSession, '/check_session', '/me')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(NoteList, '/notes')
api.add_resource(NoteDetail, '/notes/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)