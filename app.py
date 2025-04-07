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
            session['rol'] = user.get('rol', 'user')  # Usar 'user' como valor por defecto si no hay rol
            return redirect(url_for('index'))
        else:
            flash('Credenciales inválidas')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/', methods=['GET'])
@login_required
def index():
    return render_template('index.html')

@app.route('/registro_contratos', methods=['GET', 'POST'])
@login_required
def registro_contratos():
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
            'observaciones': request.form['observaciones'],
            'fecha_inicio': request.form['fecha_inicio'],
            'fecha_vencimiento': request.form['fecha_vencimiento'],
            'valor_facturado': float(request.form['valor_facturado'] or 0),
            'porcentaje_ejecucion': float(request.form['porcentaje_ejecucion'] or 0),
            'valor_pendiente': float(request.form['valor_pendiente'] or 0),
            'estado': request.form['estado'],
            'numero_horas': float(request.form['numero_horas'] or 0),
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

        contratos = cargar_contratos()
        contratos.append(nuevo_contrato)
        guardar_datos(contratos, 'contratos.json')
        
        # Save new client if needed
        clientes = cargar_clientes()
        if request.form['cliente'] not in clientes:
            clientes.append(request.form['cliente'])
            guardar_datos(sorted(list(set(clientes))), 'clientes.json')

        # Save new category if needed
        categorias = cargar_categorias()
        if request.form['categoria'] not in categorias:
            categorias.append(request.form['categoria'])
            guardar_datos(sorted(list(set(categorias))), 'categorias.json')

        # Redirect to lista_contratos after saving
        return redirect(url_for('lista_contratos'))
    
    clientes = cargar_clientes()
    categorias = cargar_categorias()
    
    return render_template('registro_contratos.html',
                         empresas=EMPRESAS,
                         clientes=sorted(clientes),
                         categorias=sorted(categorias))

@app.route('/lista_contratos')
@login_required
def lista_contratos():
    contratos = cargar_contratos()
    return render_template('lista_contratos.html', contratos=contratos)

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
            'observaciones': request.form['observaciones'],
            'fecha_inicio': request.form['fecha_inicio'],
            'fecha_vencimiento': request.form['fecha_vencimiento'],
            'valor_facturado': float(request.form['valor_facturado'] or 0),
            'porcentaje_ejecucion': float(request.form['porcentaje_ejecucion'] or 0),
            'valor_pendiente': float(request.form['valor_pendiente'] or 0),
            'estado': request.form['estado'],
            'numero_horas': float(request.form['numero_horas'] or 0),
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

@app.route('/estadisticas')
@login_required
def estadisticas():
    contratos = cargar_contratos()
    return render_template('estadisticas.html', contratos=contratos)

@app.route('/exportar_contratos')
@login_required
def exportar_contratos():
    contratos = cargar_contratos()
    return jsonify(contratos)

@app.route('/administracion')
@login_required
def administracion():
    if session.get('rol') != 'admin':
        flash('No tienes permisos para acceder a esta sección')
        return redirect(url_for('index'))
    
    usuarios = cargar_usuarios()
    # Asegurarse de que todos los usuarios tengan un rol
    for usuario in usuarios:
        if 'rol' not in usuario:
            usuario['rol'] = 'user'
    
    return render_template('administracion.html', usuarios=usuarios)

@app.route('/contratos_proximos')
@login_required
def contratos_proximos():
    contratos = cargar_contratos()
    hoy = datetime.now().date()
    
    # Filtrar contratos próximos a vencer
    contratos_30_dias = []
    contratos_60_dias = []
    contratos_vencidos = []
    
    for idx, contrato in enumerate(contratos):
        if not contrato.get('fecha_vencimiento'):
            continue
            
        fecha_vencimiento = datetime.strptime(contrato['fecha_vencimiento'], '%Y-%m-%d').date()
        dias_restantes = (fecha_vencimiento - hoy).days
        
        # Agregar el ID al contrato
        contrato_con_id = contrato.copy()
        contrato_con_id['id'] = idx
        
        if dias_restantes < 0:
            contrato_con_id['dias_retraso'] = abs(dias_restantes)
            contratos_vencidos.append(contrato_con_id)
        elif dias_restantes <= 30:
            contrato_con_id['dias_restantes'] = dias_restantes
            contratos_30_dias.append(contrato_con_id)
        elif dias_restantes <= 60:
            contrato_con_id['dias_restantes'] = dias_restantes
            contratos_60_dias.append(contrato_con_id)
    
    return render_template('contratos_proximos.html',
                         contratos_30_dias=contratos_30_dias,
                         contratos_60_dias=contratos_60_dias,
                         contratos_vencidos=contratos_vencidos)

if __name__ == '__main__':
    app.run(debug=True)