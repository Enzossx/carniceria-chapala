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



from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Ejemplo de tu ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para el formulario del nuevo corte
@app.route('/nuevo_corte', methods=['GET', 'POST'])
def nuevo_corte():
    if request.method == 'POST':
        nombre_corte = request.form['nombre']
        precio_corte = request.form['precio']
        
        # Conexión a la base de datos e inserción...
        conexion = conectar_db()
        cursor = conexion.cursor()
        query = "INSERT INTO cortes (nombre, precio) VALUES (%s, %s)"
        cursor.execute(query, (nombre_corte, precio_corte))
        conexion.commit()
        cursor.close()
        conexion.close()
        
        # Redirige al inicio tras guardar
        return redirect(url_for('index'))
    
    # Si entra por GET, renderiza el formulario formu.html
    return render_template('formu.html')

if __name__ == '__main__':
    app.run(debug=True)






















