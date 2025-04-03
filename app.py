from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import json
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Opciones predefinidas
EMPRESAS = ["SKIT", "KONCILIA"]

# Funciones de carga y guardado
def cargar_datos(archivo):
    if os.path.exists(archivo):
        with open(archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def guardar_datos(datos, archivo):
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

def cargar_clientes():
    return cargar_datos('clientes.json')

def cargar_categorias():
    return cargar_datos('categorias.json')

def cargar_contratos():
    return cargar_datos('contratos.json')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def cargar_usuarios():
    return cargar_datos('users.json')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = cargar_usuarios()
        
        user = next((user for user in users if user['username'] == username and user['password'] == password), None)
        
        if user:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    clientes = cargar_clientes()
    categorias = cargar_categorias()
    contratos = cargar_contratos()
    
    if request.method == 'POST':
        nuevo_contrato = {
            'año': request.form['año'],
            'empresa': request.form['empresa'],
            'cliente': request.form['cliente'],
            'contrato': request.form['contrato'],
            'valor_pesos': float(request.form['valor_pesos'] or 0),
            'valor_dolares': float(request.form['valor_dolares'] or 0),
            'descripcion': request.form['descripcion'],
            'categoria': request.form['categoria'],
            'valor_mensual': float(request.form['valor_mensual'] or 0),
            'condiciones': request.form['condiciones'],
            'fecha_inicio': request.form['fecha_inicio'],
            'fecha_vencimiento': request.form['fecha_vencimiento'],
            'valor_facturado': float(request.form['valor_facturado'] or 0),
            'valor_pendiente': float(request.form['valor_pendiente'] or 0),
            'estado': request.form['estado'],
            'numero_factura': request.form['numero_factura'],
            'numero_poliza': request.form['numero_poliza'],
            'fecha_vencimiento_poliza': request.form['fecha_vencimiento_poliza'],
            'comentario_poliza': request.form['comentario_poliza']
        }
        
        # Calculate progress
        if nuevo_contrato['valor_pesos'] > 0:
            nuevo_contrato['progreso'] = (nuevo_contrato['valor_facturado'] / nuevo_contrato['valor_pesos']) * 100
        else:
            nuevo_contrato['progreso'] = 0

        contratos.append(nuevo_contrato)
        guardar_datos(contratos, 'contratos.json')

        # Save new client if needed
        if request.form['cliente'] not in clientes:
            clientes.append(request.form['cliente'])
            guardar_datos(sorted(list(set(clientes))), 'clientes.json')

        # Save new category if needed
        if request.form['categoria'] not in categorias:
            categorias.append(request.form['categoria'])
            guardar_datos(sorted(list(set(categorias))), 'categorias.json')

        # Redirect to ver_contrato with the index of the newly added contract
        return redirect(url_for('ver_contrato', id=len(contratos)-1))

    return render_template('index.html',
                         empresas=EMPRESAS,
                         clientes=sorted(clientes),
                         categorias=sorted(categorias),
                         contratos=contratos)

@app.route('/eliminar_contrato/<int:id>')
@login_required
def eliminar_contrato(id):
    contratos = cargar_contratos()
    if id < len(contratos):
        contratos.pop(id)
        guardar_datos(contratos, 'contratos.json')
    return redirect(url_for('index'))

@app.route('/ver_contrato/<int:id>')
@login_required
def ver_contrato(id):
    contratos = cargar_contratos()
    if id < len(contratos):
        return render_template('ver_contrato.html', contrato=contratos[id], id=id)
    return redirect(url_for('index'))

@app.route('/editar_contrato/<int:id>', methods=['POST'])
@login_required
def editar_contrato(id):
    contratos = cargar_contratos()
    if id < len(contratos):
        contrato = {
            'año': request.form['año'],
            'empresa': request.form['empresa'],
            'cliente': request.form['cliente'],
            'contrato': request.form['contrato'],
            'valor_pesos': float(request.form['valor_pesos'] or 0),
            'valor_dolares': float(request.form['valor_dolares'] or 0),
            'descripcion': request.form['descripcion'],
            'categoria': request.form['categoria'],
            'valor_mensual': float(request.form['valor_mensual'] or 0),
            'condiciones': request.form['condiciones'],
            'fecha_inicio': request.form['fecha_inicio'],
            'fecha_vencimiento': request.form['fecha_vencimiento'],
            'valor_facturado': float(request.form['valor_facturado'] or 0),
            'valor_pendiente': float(request.form['valor_pendiente'] or 0),
            'estado': request.form['estado'],
            'numero_factura': request.form['numero_factura'],
            'numero_poliza': request.form['numero_poliza'],
            'fecha_vencimiento_poliza': request.form['fecha_vencimiento_poliza'],
            'comentario_poliza': request.form['comentario_poliza']
        }
        
        if contrato['valor_pesos'] > 0:
            contrato['progreso'] = (contrato['valor_facturado'] / contrato['valor_pesos']) * 100
        else:
            contrato['progreso'] = 0

        contratos[id] = contrato
        guardar_datos(contratos, 'contratos.json')
        
    return redirect(url_for('ver_contrato', id=id))

if __name__ == '__main__':
    app.run(debug=True)