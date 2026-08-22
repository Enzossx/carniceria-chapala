from flask import Flask, render_template, request, redirect, url_for, Response, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'clave_secreta_chapala'

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def conectar_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",
        database="chapala"
    )

# Modelo de usuario con rol es_admin
class Usuario(UserMixin):
    def __init__(self, id, nombre, email, es_admin=0):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.es_admin = es_admin

@login_manager.user_loader
def load_user(user_id):
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, email, es_admin FROM usuarios WHERE id = %s", (user_id,))
    res = cursor.fetchone()
    cursor.close()
    conexion.close()
    if res:
        return Usuario(res['id'], res['nombre'], res['email'], res.get('es_admin', 0))
    return None

# Ruta Principal
@app.route('/')
def index():
    busqueda = request.args.get('buscar', '').strip()
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)
    
    if busqueda:
        cursor.execute("SELECT id, nombre, precio FROM cortes WHERE nombre LIKE %s ORDER BY id DESC", (f"%{busqueda}%",))
    else:
        cursor.execute("SELECT id, nombre, precio FROM cortes ORDER BY id DESC")
        
    cortes_guardados = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template('index.html', cortes=cortes_guardados, busqueda=busqueda)

# Ruta para Agregar Nuevo Corte (Protegida)
@app.route('/nuevo_corte', methods=['GET', 'POST'])
@login_required
def nuevo_corte():
    if not current_user.es_admin:
        flash("No tienes permisos de administrador para agregar cortes.")
        return redirect(url_for('index'))

    if request.method == 'POST':
        nombre_corte = request.form['nombre']
        precio_corte = request.form['precio']
        
        imagen_blob = None
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and file.filename != '':
                imagen_blob = file.read()

        conexion = conectar_db()
        cursor = conexion.cursor()
        query = "INSERT INTO cortes (nombre, precio, imagen) VALUES (%s, %s, %s)"
        cursor.execute(query, (nombre_corte, precio_corte, imagen_blob))
        
        conexion.commit()
        cursor.close()
        conexion.close()
        return redirect(url_for('index'))
        
    return render_template('formu.html')

# Ruta para Obtener Imagen del Corte
@app.route('/imagen_corte/<int:id_corte>')
def imagen_corte(id_corte):
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT imagen FROM cortes WHERE id = %s", (id_corte,))
    resultado = cursor.fetchone()
    cursor.close()
    conexion.close()

    if resultado and resultado[0]:
        return Response(resultado[0], mimetype='image/jpeg')
    return ''

# Ruta para Registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        
        password_hashed = generate_password_hash(password)

        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conexion.close()
            flash("El correo electrónico ya se encuentra registrado.")
            return redirect(url_for('register'))

        cursor.execute("INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)", 
                       (nombre, email, password_hashed))
        conexion.commit()
        
        user_id = cursor.lastrowid
        cursor.close()
        conexion.close()

        usuario_nuevo = Usuario(user_id, nombre, email, es_admin=0)
        login_user(usuario_nuevo, remember=True)
        return redirect(url_for('index'))

    return render_template('register.html')

# Ruta para Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['usuario']
        password = request.form['password']

        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email = %s OR nombre = %s", (email, email))
        user = cursor.fetchone()
        cursor.close()
        conexion.close()

        if user and check_password_hash(user['password'], password):
            usuario_obj = Usuario(user['id'], user['nombre'], user['email'], user.get('es_admin', 0))
            login_user(usuario_obj, remember=True)
            return redirect(url_for('index'))
        else:
            flash("Usuario o contraseña incorrectos.")
            return redirect(url_for('login'))

    return render_template('login.html')

# Ruta para Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)