from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
CORS(app)
db = SQLAlchemy(app)

class User(db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), nullable=False)
  surname = db.Column(db.String(80), nullable=False)  # исправлено: добавлено поле surname
  phone = db.Column(db.String(80), unique=True, nullable=False)
  birth_date = db.Column(db.String(80), nullable=True)

  def json(self):
    return {
      'id': self.id,
      'Name': self.name,
      'Surname': self.surname,
      'Phone': self.phone,
      'BirthDate': self.birth_date
    }

# Для разработки: сбрасываем и пересоздаем таблицы при запуске
with app.app_context():
  db.drop_all()    # Внимание: удаляет все таблицы. Не используйте в production!
  db.create_all()

@app.route("/v1/users", methods=["GET"])
def get_users():
  try:
    users = User.query.all()
    return make_response(jsonify([user.json() for user in users]), 200)
  except Exception as e:
    return make_response(jsonify({'error': 'Failed to fetch users', 'details': str(e)}), 500)

@app.route("/v1/add", methods=["POST"])
def add_user():
  try:
    data = request.get_json()
    if not data:
      return make_response(jsonify({'error': 'Invalid JSON'}), 400)
    existing_user = User.query.filter_by(phone=data["Phone"]).first()
    if existing_user:
      return make_response(jsonify({'error': 'User with this phone already exists'}), 400)
    new_user = User(
      name=data['Name'],
      surname=data['Surname'],
      phone=data['Phone'],
      birth_date=data.get('BirthDate')
    )
    db.session.add(new_user)
    db.session.commit()
    return make_response(jsonify({'message': 'User created successfully'}), 201)
  except Exception as e:
    return make_response(jsonify({'error': 'Failed to add user', 'details': str(e)}), 500)

@app.route("/v1/update", methods=["PUT"])
def update_user():
  try:
    data = request.get_json()
    if not data:
      return make_response(jsonify({'error': 'Invalid JSON'}), 400)

    user = None
    if "id" in data:
      user = User.query.get(data["id"])
    elif "Phone" in data:
      user = User.query.filter_by(phone=data["Phone"]).first()
    elif "Name" in data and "Surname" in data:
      user = User.query.filter_by(name=data["Name"], surname=data["Surname"]).first()

    if not user:
      return make_response(jsonify({'error': 'User not found'}), 404)

    field = data.get("Field")
    new_value = data.get("NewValue")
    if not field or not new_value:
      return make_response(jsonify({'error': 'Field and NewValue are required for update'}), 400)

    if field == "Name":
      user.name = new_value
    elif field == "Surname":
      user.surname = new_value
    elif field == "Phone":
      existing_user = User.query.filter_by(phone=new_value).first()
      if existing_user and existing_user.id != user.id:
        return make_response(jsonify({'error': 'Phone number already in use'}), 400)
      user.phone = new_value
    elif field == "BirthDate":
      user.birth_date = new_value
    else:
      return make_response(jsonify({'error': 'Invalid field specified'}), 400)

    db.session.commit()
    return make_response(jsonify({'message': 'User updated successfully'}), 200)
  except Exception as e:
    db.session.rollback()
    return make_response(jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500)

@app.route("/v1/delete", methods=["DELETE"])
def delete_user():
  try:
    data = request.get_json()
    if not data:
      return make_response(jsonify({'error': 'Invalid JSON'}), 400)

    user = None
    if "id" in data:
      user = User.query.get(data["id"])
    elif "Phone" in data:
      user = User.query.filter_by(phone=data["Phone"]).first()
    elif "Name" in data and "Surname" in data:
      user = User.query.filter_by(name=data["Name"], surname=data["Surname"]).first()

    if not user:
      return make_response(jsonify({'error': 'User not found'}), 404)

    db.session.delete(user)
    db.session.commit()
    return make_response(jsonify({'message': 'User deleted successfully'}), 200)
  except Exception as e:
    db.session.rollback()
    return make_response(jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500)

@app.route("/v1/search", methods=["POST"])
def search_users():
  try:
    data = request.get_json()
    query = User.query
    if "Name" in data and data["Name"]:
      query = query.filter(User.name.ilike(f"%{data['Name']}%"))
    if "Surname" in data and data["Surname"]:
      query = query.filter(User.surname.ilike(f"%{data['Surname']}%"))
    if "Phone" in data and data["Phone"]:
      query = query.filter(User.phone.ilike(f"%{data['Phone']}%"))
    if "BirthDate" in data and data["BirthDate"]:
      query = query.filter(User.birth_date.ilike(f"%{data['BirthDate']}%"))
    users = query.all()
    return make_response(jsonify([user.json() for user in users]), 200)
  except Exception as e:
    return make_response(jsonify({'error': 'Failed to search users', 'details': str(e)}), 500)


if __name__ == "__main__":
  app.run(debug=True)
