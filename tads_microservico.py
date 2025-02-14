# -*- coding: utf-8 -*-
"""TADS_microservico.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Q6EbD3F41Zs_PZmlYhKzYFjoFW4zDzEF
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from pyngrok import ngrok
from threading import Thread

app = Flask(__name__)

basedir = os.path.abspath(os.getcwd())
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Data(db.Model):
    id = db.Column(db.String, primary_key=True)
    content = db.Column(db.JSON, nullable=False)

    def __repr__(self):
        return f'<Data {self.id}>'

# Função para criar as tabelas dentro do contexto da aplicação Flask
def create_tables():
    with app.app_context():
        db.create_all()

# Rota para adicionar dados via POST
@app.route('/data', methods=['POST'])
def add_data():
    if request.is_json:
        content = request.get_json()
        records = []

        for record in content:
            id = record.get("id")
            if not id:
                return jsonify({"error": "Campo 'id' é obrigatório"}), 400

            if Data.query.get(id):
                return jsonify({"error": f"Registro com id '{id}' já existe"}), 400

            new_data = Data(id=id, content=record)
            records.append(new_data)

        db.session.add_all(records)
        db.session.commit()
        return jsonify({"message": "Dados adicionados com sucesso"}), 201
    else:
        return jsonify({"error": "O corpo da solicitação deve estar no formato JSON"}), 400

# Rota para retornar todos os dados via GET
@app.route('/data', methods=['GET'])
def get_data():
    all_data = Data.query.all()
    results = [
        {
            "content": data.content
        } for data in all_data]

    return jsonify(results), 200

# Rota para retornar um dado específico por ID
@app.route('/data/<string:id>', methods=['GET'])
def get_data_by_id(id):
    data = Data.query.get(id)
    if data:
        return jsonify({
            "id": data.id,
            "content": data.content
        }), 200
    else:
        return jsonify({"error": "Dados não encontrados"}), 404

# Função para iniciar o servidor Flask e ngrok
def run_flask():
    with app.app_context():
        create_tables()
        
        # Inicia o servidor Flask em uma thread separada
        thread = Thread(target=lambda: app.run(debug=True, use_reloader=False))
        thread.start()

        # Inicia o ngrok
        public_url = ngrok.connect(5000)
        print(" * ngrok URL:", public_url)

# Inicia o servidor Flask e ngrok
run_flask()