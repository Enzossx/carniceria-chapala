from flask import Flask, render_template,request,redirect,url_for
import mysql.connector
app = Flask(__name__)


def conectar_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",
        database="chapala"
    )


@app.route('/')
def index():
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)
    return render_template('index.html')


@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']

    return render_template('formu.html')


if __name__ == '__main__':
    app.run(debug=True)























