from flask import Flask, render_template, request, redirect, url_for
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
    busqueda = request.args.get('buscar', '').strip()
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)
    
    if busqueda:
        query = "SELECT id, nombre, precio FROM cortes WHERE nombre LIKE %s ORDER BY id DESC"
        cursor.execute(query, (f"%{busqueda}%",))
    else:
        query = "SELECT id, nombre, precio FROM cortes ORDER BY id DESC"
        cursor.execute(query)
        
    cortes_guardados = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template('index.html', cortes=cortes_guardados, busqueda=busqueda)

@app.route('/nuevo_corte', methods=['GET', 'POST'])
def nuevo_corte():
    if request.method == 'POST':
        nombre_corte = request.form['nombre']
        precio_corte = request.form['precio']
        conexion = conectar_db()
        cursor = conexion.cursor()
        query = "INSERT INTO cortes (nombre, precio) VALUES (%s, %s)"
        cursor.execute(query, (nombre_corte, precio_corte))
        conexion.commit()
        cursor.close()
        conexion.close()
        return redirect(url_for('index'))
    return render_template('formu.html')

# --- AQUÍ DEBE ESTAR LA RUTA DE LOGIN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('login.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)