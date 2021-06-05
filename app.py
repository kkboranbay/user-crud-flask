# dev environment
# psql -h {SERVICE IP} -p {PORT} -d myapp -U myuser
# 1. create table clients(id SERIAL PRIMARY KEY, name VARCHAR(255));
# 2. insert into clients(name) values('Sultan Dev');

# test environment
# psql -h {SERVICE IP} -p {PORT} -d myapp -U myuser
# 1. create table clients(id SERIAL PRIMARY KEY, name VARCHAR(255));
# 2. insert into clients(name) values('Sultan Test');

# prod environment
# psql -h {SERVICE IP} -p {PORT} -d myapp -U myuser
# 1. create table clients(id SERIAL PRIMARY KEY, name VARCHAR(255));
# 2. insert into clients(name) values('Sultan Prod');

import os
import json
import time
import random
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from metrics import register_metrics

config = {
    'DATABASE_URI': os.environ.get('DATABASE_URI'),
    'GREETING': os.environ.get('GREETING'),
    'ENVIRONMENT': os.environ.get('ENVIRONMENT'),
}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config['DATABASE_URI']
db = SQLAlchemy(app)
CORS(app)

class User(db.Model):
    __tablename__ = "clients"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '%s/%s' % (self.id, self.name)

@app.route('/all', methods=['GET'])
def all():
    if request.method == 'GET':
        data = User.query.order_by(User.id).all()
        result = []
        for i in range(len(data)):
            user = {
                'id': str(data[i]).split('/')[0],
                'name': str(data[i]).split('/')[1],
            }
            result.append(user)
        return json.dumps(result)

@app.route('/store', methods=['POST'])
def store():
    if request.method == 'POST':
        body = request.json
        name = body['name']

        data = User(name)
        db.session.add(data)
        db.session.commit()

        return jsonify({
            'status': 'New client saved to PostgreSQL!',
            'name': name,
        })

@app.route('/get/<string:id>', methods=['GET'])
def get(id):
    if request.method == 'GET':
        data = User.query.get(id)
        result = {
            'id': str(data).split('/')[0],
            'name': str(data).split('/')[1],
        }
        return jsonify(result)

@app.route('/delete/<string:id>', methods=['DELETE'])
def delete(id):
    if request.method == 'DELETE':
        user = User.query.filter_by(id=id).first()
        db.session.delete(user)
        db.session.commit()
        return jsonify({'status': 'Client '+id+' is deleted from PostgreSQL'})

@app.route('/update/<string:id>', methods=['PUT'])
def update(id):
    if request.method == 'PUT':
        body = request.json
        newName = body['name']
        user = User.query.filter_by(id=id).first()
        user.name = newName
        db.session.commit()
        return jsonify({'status': 'Client '+id+' is updated from PostgreSQL'})

@app.route("/")
def hello():
    return config['GREETING'] + ' from ' + 'environment: ' + config['ENVIRONMENT']

@app.route("/config")
def configuration():
    return 'config'

@app.route("/oops")
def oops():
    return 'oops', 500

@app.route('/metrics')
def metrics():
    from prometheus_client import generate_latest
    return generate_latest()

if __name__ == '__main__':
    register_metrics(app)
    app.run(host='0.0.0.0', port='9000')