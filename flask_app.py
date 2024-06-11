## flask --app flask_app --debug run
from flask import Flask, request, render_template, make_response, redirect
import os
import recomendar

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html") # para el login

@app.route("/login", methods=["POST"])
def login():
    username = request.form['username']

    res = recomendar.sql_select(f"SELECT * FROM users WHERE username = '{username}'")
    if res == []: # no existe
        recomendar.crear_usuario(username)        

    return make_response(redirect(f"/recomendaciones/{username}"))

@app.route("/recomendaciones/<username>", methods=["GET"])
def recomendaciones(username):  
    episodios, algoritmo = recomendar.recomendar(username)
    cant_valorados = len(recomendar.valorados(username))
    cant_ignorados = len(recomendar.ignorados(username))

    return render_template("recomendaciones.html", episodios=episodios, username=username, cant_valorados=cant_valorados, cant_ignorados=cant_ignorados, algoritmo=algoritmo)

@app.route("/interacciones/<username>", methods=["POST"])
def interacciones(username):

    for episode_code in request.form.keys():
        vote = int(request.form[episode_code])
        recomendar.sql_execute(f"INSERT INTO reviews(username, episode_code, vote) VALUES (?, ?, ?)", (username, episode_code, vote))

    return make_response(redirect(f"/recomendaciones/{username}"))

@app.route("/reset/<username>", methods=["GET"])
def reset(username):
    recomendar.sql_execute(f"DELETE FROM reviews WHERE username = ?", (username,))
    return make_response(redirect(f"/recomendaciones/{username}"))
