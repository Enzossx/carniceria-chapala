from flask import Flask, render_template, request, redirect, url_for, Response, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
import mysql.connector

app = Flask(__name__)
app.secret_key = 'clave_secreta_chapala'

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'enzosalvatierra44@gmail.com'  # Cambia por tu correo
app.config['MAIL_PASSWORD'] = 'ttrg wmly vgfy ypbq'    # Cambia por tu contraseña de aplicación de Google
app.config['MAIL_DEFAULT_SENDER'] = ('Carnicería Chapala', 'enzosalvatierra44@gmail.com')

mail = Mail(app)
serializer = URLSafeTimedSerializer(app.secret_key)

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

# Ruta para ver el detalle de un corte
@app.route('/corte/<int:id_corte>')
def detalle_corte(id_corte):
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, precio FROM cortes WHERE id = %s", (id_corte,))
    corte = cursor.fetchone()
    cursor.close()
    conexion.close()

    if not corte:
        flash("El corte seleccionado no existe.")
        return redirect(url_for('index'))

    return render_template('comprar.html', corte=corte)

# Ruta para agregar un ítem al carrito
@app.route('/agregar_al_carrito/<int:id_corte>', methods=['POST'])
@login_required
def agregar_al_carrito(id_corte):
    try:
        cantidad = float(request.form.get('cantidad', 1))
    except (ValueError, TypeError):
        cantidad = 1.0

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)
    
    cursor.execute("SELECT id, cantidad FROM carrito WHERE id_usuario = %s AND id_corte = %s", (current_user.id, id_corte))
    item = cursor.fetchone()

    if item:
        cursor.execute("UPDATE carrito SET cantidad = cantidad + %s WHERE id = %s", (cantidad, item['id']))
    else:
        cursor.execute("INSERT INTO carrito (id_usuario, id_corte, cantidad) VALUES (%s, %s, %s)", (current_user.id, id_corte, cantidad))

    conexion.commit()
    cursor.close()
    conexion.close()

    flash("Corte agregado al carrito con éxito.")
    return redirect(url_for('ver_carrito'))

# Ruta para ver el carrito
@app.route('/carrito')
@login_required
def ver_carrito():
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)
    
    query = """
        SELECT c.id AS id_item, c.id_corte, c.cantidad, cor.nombre, cor.precio, (c.cantidad * cor.precio) AS subtotal
        FROM carrito c
        JOIN cortes cor ON c.id_corte = cor.id
        WHERE c.id_usuario = %s
    """
    cursor.execute(query, (current_user.id,))
    items = cursor.fetchall()
    
    total = sum(item['subtotal'] for item in items)
    
    cursor.close()
    conexion.close()
    return render_template('carrito.html', items=items, total=total)

# Ruta para quitar un ítem del carrito
@app.route('/eliminar_del_carrito/<int:id_item>')
@login_required
def eliminar_del_carrito(id_item):
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM carrito WHERE id = %s AND id_usuario = %s", (id_item, current_user.id))
    conexion.commit()
    cursor.close()
    conexion.close()
    flash("Ítem eliminado del carrito.")
    return redirect(url_for('ver_carrito'))

# Ruta para pagar todo el carrito
@app.route('/pagar_carrito', methods=['POST'])
@login_required
def pagar_carrito():
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    query = """
        SELECT c.id_corte, c.cantidad, cor.precio
        FROM carrito c
        JOIN cortes cor ON c.id_corte = cor.id
        WHERE c.id_usuario = %s
    """
    cursor.execute(query, (current_user.id,))
    items = cursor.fetchall()

    if not items:
        flash("El carrito está vacío.")
        cursor.close()
        conexion.close()
        return redirect(url_for('ver_carrito'))

    total = sum(item['cantidad'] * item['precio'] for item in items)

    cursor.execute("INSERT INTO ventas (id_usuario, total) VALUES (%s, %s)", (current_user.id, total))
    id_venta = cursor.lastrowid

    for item in items:
        cursor.execute(
            "INSERT INTO detalle_ventas (id_venta, id_corte, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)",
            (id_venta, item['id_corte'], item['cantidad'], item['precio'])
        )

    cursor.execute("DELETE FROM carrito WHERE id_usuario = %s", (current_user.id,))

    conexion.commit()
    cursor.close()
    conexion.close()

    flash("¡Compra realizada con éxito!")
    return redirect(url_for('historial'))

# Ruta para ver el historial de compras
@app.route('/historial')
@login_required
def historial():
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT id, total, fecha FROM ventas WHERE id_usuario = %s ORDER BY fecha DESC", (current_user.id,))
    compras = cursor.fetchall()

    for compra in compras:
        cursor.execute("""
            SELECT dv.cantidad, dv.precio_unitario, c.nombre AS nombre_corte
            FROM detalle_ventas dv
            JOIN cortes c ON dv.id_corte = c.id
            WHERE dv.id_venta = %s
        """, (compra['id'],))
        compra['detalles'] = cursor.fetchall()

    cursor.close()
    conexion.close()
    return render_template('historial.html', compras=compras)

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

# Paso 1: Pedir el correo para restablecer contraseña
@app.route('/request_reset', methods=['GET', 'POST'])
def request_reset():
    if request.method == 'POST':
        email = request.form['email']
        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone()
        cursor.close()
        conexion.close()

        if usuario:
            token = serializer.dumps(email, salt='reset-password-salt')
            link = url_for('reset_with_token', token=token, _external=True)
            
            try:
                msg = Message("Restablecer Contraseña - Carnicería Chapala", recipients=[email])
                msg.body = f"Hola,\n\nHas solicitado restablecer tu contraseña en Carnicería Chapala. Haz clic en el siguiente enlace o cópialo en tu navegador para cambiarla:\n\n{link}\n\nEste enlace expira en 30 minutos.\n\nSi no realizaste esta solicitud, ignora este mensaje."
                mail.send(msg)
            except Exception as e:
                flash("Ocurrió un error al enviar el correo. Verifica tu configuración.")
                return redirect(url_for('request_reset'))

        flash("Si el correo ingresado se encuentra registrado, recibirás un mensaje con las instrucciones.")
        return redirect(url_for('login'))

    return render_template('request_reset.html')

# Paso 2: Cambiar la contraseña validando el token enviado por mail
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    try:
        email = serializer.loads(token, salt='reset-password-salt', max_age=1800) # Token válido por 30 minutos
    except (SignatureExpired, BadTimeSignature):
        flash("El enlace de restablecimiento ha expirado o es inválido. Por favor solicita uno nuevo.")
        return redirect(url_for('request_reset'))

    if request.method == 'POST':
        nueva_password = request.form['password']
        password_hashed = generate_password_hash(nueva_password)

        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("UPDATE usuarios SET password = %s WHERE email = %s", (password_hashed, email))
        conexion.commit()
        cursor.close()
        conexion.close()

        flash("¡Tu contraseña se ha actualizado con éxito! Ya puedes iniciar sesión.")
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)

# Ruta para Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)