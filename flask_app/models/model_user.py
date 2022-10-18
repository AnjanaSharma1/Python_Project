from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import app, bcrypt, DATABASE
from flask import flash, session
from flask_app.models import model_car
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class User:
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.pw = data['pw']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.car = []
        self.fullname = f"{self.first_name.capitalize()} {self.last_name.capitalize()}"
    
    
    # creating (CRUD)
    @classmethod
    def create_user(cls, data):
        query = 'INSERT INTO users (first_name, last_name, email, pw) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(pw)s);'
        return connectToMySQL(DATABASE).query_db(query, data)
    
    # reading(CRUD)
    
    @classmethod
    def get_one_user(cls, data):
        query = 'SELECT * FROM users LEFT JOIN car ON users.id = car.user_id WHERE users.id = %(id)s;'
        result = connectToMySQL(DATABASE).query_db(query, data)
        if not result:
            return False
        user = cls(result[0])
        for car in result:
            car_data = {
                'id': car['id'],
                'model': car['model'],
                'date': car['date'],
                'make': car['make'],
                'description': car['description'],
                'price': car['price'],
                'created_at': car['car.created_at'],
                'updated_at': car['car.updated_at']
            }
            user.car.append(model_car.Car(car_data))
        return user
    
    
    
    @classmethod
    def get_all_users(cls):
        query = 'SELECT * FROM users;'
        users_from_db = connectToMySQL(DATABASE).query_db(query)
        if not users_from_db:
            return []
        users = []
        for dict in users_from_db:
            users.append(dict)
        return users
    
    
    @classmethod
    def get_by_email(cls, data):
        query = 'SELECT * FROM users WHERE email = %(email)s;'
        result = connectToMySQL(DATABASE).query_db(query, data)
        if not result:
            return False
        return cls(result[0])
    
    
    @classmethod
    def update_user(cls, data):
        query = 'UPDATE users SET first_name=%(first_name)s, last_name=%(last_name)s, email=%(email)s, pw=%(pw)s WHERE id = %(id)s;'
        user = connectToMySQL(DATABASE).query_db(query, data)
        return cls(user)
    
    
    @classmethod
    def delete_user(cls, data):
        query = 'DELETE FROM users WHERE id = %(id)s;'
        user = connectToMySQL(DATABASE).query_db(query, data)
        return cls(user)
    
    
    
    
    # validation
    
    @staticmethod
    def validate_login(data):
        is_valid = True
        if len(data['email']) < 1:
            is_valid = False
            flash('Invalid Email', 'err_login')
        elif not EMAIL_REGEX.match(data['email']):
            is_valid = False
            flash('Invalid Email', 'err_login')
        if len(data['pw']) < 8:
            is_valid = False
            flash('Invalid Password length.', 'err_login')
        if is_valid:
            potential_user = User.get_by_email({'email': data['email']})
            if not potential_user:
                flash('Email not found', 'err_login')
                is_valid = False
            else:
                if not bcrypt.check_password_hash(potential_user.pw, data['pw']):
                    flash('Wrong password', 'err_login')
                    is_valid = False
                else:
                    session['uuid'] = potential_user.id
        return is_valid