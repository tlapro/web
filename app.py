from datetime import date
import sqlite3
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required

# Configure application
app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def get_db_connection():
    conn = sqlite3.connect('bdd.db')
    conn.row_factory = sqlite3.Row
    return conn

# Función para obtener datos de la base de datos
def obtener_datos_alimento(nombre):
    print(f"Buscando datos para: {nombre}")  # Comprobamos que esta línea se ejecute
    conn = sqlite3.connect('bdd.db')
    cursor = conn.cursor()
    cursor.execute('SELECT caloriasmin, caloriasmax, proteinasmin, proteinasmax, carbosmin, carbosmax, grasasmin, grasasmax, peso FROM comidas WHERE nombre = ?', (nombre,))
    resultado = cursor.fetchone()
    print(f"Resultado para {nombre}: {resultado}")  # Debugging
    conn.close()
    return resultado

def obtener_datos_alimento(nombre):
    print(f"Buscando datos para: {nombre}")  # Comprobamos que esta línea se ejecute
    conn = sqlite3.connect('bdd.db')
    cursor = conn.cursor()
    cursor.execute('SELECT caloriasmin, caloriasmax, proteinasmin, proteinasmax, carbosmin, carbosmax, grasasmin, grasasmax, peso FROM comidas WHERE nombre = ?', (nombre,))
    resultado = cursor.fetchone()
    print(f"Resultado para {nombre}: {resultado}")  # Debugging
    conn.close()
    return resultado

def calcular_comida(comida_peso_dict):
    resultados = {
        'totales': {
            'calorias_min_total': 0,
            'calorias_max_total': 0,
            'proteinas_min_total': 0,
            'proteinas_max_total': 0,
            'carbos_min_total': 0,
            'carbos_max_total': 0,
            'grasas_min_total': 0,
            'grasas_max_total': 0,
            'avg_calorias': 0,
            'avg_proteinas': 0,
            'avg_carbos': 0,
            'avg_grasas': 0,
        },
        'individuales': {
            'desayuno': {'calorias_min': 0, 'calorias_max': 0, 'proteinas_min': 0, 'proteinas_max': 0, 'carbos_min': 0, 'carbos_max': 0, 'grasas_min': 0, 'grasas_max': 0},
            'almuerzo': {'calorias_min': 0, 'calorias_max': 0, 'proteinas_min': 0, 'proteinas_max': 0, 'carbos_min': 0, 'carbos_max': 0, 'grasas_min': 0, 'grasas_max': 0},
            'merienda': {'calorias_min': 0, 'calorias_max': 0, 'proteinas_min': 0, 'proteinas_max': 0, 'carbos_min': 0, 'carbos_max': 0, 'grasas_min': 0, 'grasas_max': 0},
            'cena': {'calorias_min': 0, 'calorias_max': 0, 'proteinas_min': 0, 'proteinas_max': 0, 'carbos_min': 0, 'carbos_max': 0, 'grasas_min': 0, 'grasas_max': 0},
            'extra': {'calorias_min': 0, 'calorias_max': 0, 'proteinas_min': 0, 'proteinas_max': 0, 'carbos_min': 0, 'carbos_max': 0, 'grasas_min': 0, 'grasas_max': 0},
        }
    }

    for tipo_comida in ['desayuno', 'almuerzo', 'merienda', 'cena', 'extra']:
        alimentos = comida_peso_dict.get(f'{tipo_comida}[]', [])
        pesos = comida_peso_dict.get('peso[]', [])

        print(f"Procesando {tipo_comida}: Alimentos: {alimentos}, Pesos: {pesos}")  # Verificar que los datos lleguen correctamente

        for i, alimento in enumerate(alimentos):
            # Asegurar que haya un peso correspondiente
            if i < len(pesos):  
                 # Limpiar el peso para eliminar espacios en blanco
                peso = pesos[i].strip() 
                if not peso:
                    print(f"Peso vacío para el alimento: {alimento}")
                     # Saltar si el peso está vacío
                    continue 

                try:
                     # Intenta convertir el peso a float
                    peso = float(peso) 
                except ValueError:
                    print(f"Error al convertir el peso '{peso}' para el alimento: {alimento}.")
                    # Saltar este alimento si el peso no es válido
                    continue  

                datos_alimento = obtener_datos_alimento(alimento)
                
                if datos_alimento:
                    calorias_min, calorias_max, proteinas_min, proteinas_max, carbos_min, carbos_max, grasas_min, grasas_max, peso_base = datos_alimento
                    factor = peso / peso_base  # Factor de ajuste por peso
                    resultados['individuales'][tipo_comida]['calorias_min'] += calorias_min * factor
                    resultados['individuales'][tipo_comida]['calorias_max'] += calorias_max * factor
                    resultados['individuales'][tipo_comida]['proteinas_min'] += proteinas_min * factor
                    resultados['individuales'][tipo_comida]['proteinas_max'] += proteinas_max * factor
                    resultados['individuales'][tipo_comida]['carbos_min'] += carbos_min * factor
                    resultados['individuales'][tipo_comida]['carbos_max'] += carbos_max * factor
                    resultados['individuales'][tipo_comida]['grasas_min'] += grasas_min * factor
                    resultados['individuales'][tipo_comida]['grasas_max'] += grasas_max * factor

                    # Sumar a los totales
                    resultados['totales']['calorias_min_total'] += calorias_min * factor
                    resultados['totales']['calorias_max_total'] += calorias_max * factor
                    resultados['totales']['proteinas_min_total'] += proteinas_min * factor
                    resultados['totales']['proteinas_max_total'] += proteinas_max * factor
                    resultados['totales']['carbos_min_total'] += carbos_min * factor
                    resultados['totales']['carbos_max_total'] += carbos_max * factor
                    resultados['totales']['grasas_min_total'] += grasas_min * factor
                    resultados['totales']['grasas_max_total'] += grasas_max * factor
                    resultados['totales']['avg_calorias'] = (resultados['totales']['calorias_min_total'] + resultados['totales']['calorias_max_total']) / 2
                    resultados['totales']['avg_proteinas'] = (resultados['totales']['proteinas_min_total'] + resultados['totales']['proteinas_max_total']) / 2
                    resultados['totales']['avg_carbos'] = (resultados['totales']['carbos_min_total'] + resultados['totales']['carbos_max_total']) / 2
                    resultados['totales']['avg_grasas'] =  (resultados['totales']['grasas_min_total'] +  resultados['totales']['grasas_max_total']) / 2
                else:
                    print(f"No se encontraron datos en la base para el alimento: {alimento}")  # Error de búsqueda en la base de datos
            else:
                print(f"No hay un peso asociado para el alimento: {alimento}")

    return resultados


@app.route("/", methods=["GET", "POST"])
def index():
    if "user_id" not in session:
        return redirect("/login")
    
    user_id = session["user_id"]

    if request.method == "POST":
        comida_peso_dict = request.form.to_dict(flat=False)
        print("Datos del formulario:", comida_peso_dict)  # Debugging
        resultados = calcular_comida(comida_peso_dict)
        return render_template('index.html', resultados=resultados)
    
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    if request.method == "POST":
        # Validar si se proporcionó un nombre de usuario
        if not request.form.get("username"):
            flash("Usuario inválido.")
            return redirect("/login")

        # Validar si se proporcionó una contraseña
        elif not request.form.get("password"):
            flash("Contraseña inválida.")
            return redirect("/login")

        # Conexión a la base de datos
        conn = get_db_connection()

        # Consultar la base de datos para el nombre de usuario
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND is_active = 1", 
            (request.form.get("username"),)
        ).fetchone()
        conn.close()

        # Verificar que el nombre de usuario existe y la contraseña es correcta
        if user is None or not check_password_hash(user["hash"], request.form.get("password")):
            flash("Usuario y/o contraseña incorrectos.")
            return redirect("/login")

        # Recordar qué usuario ha iniciado sesión
        session["user_id"] = user["id"]

        # Redirigir al usuario a la página principal
        return redirect("/")

    # Si el usuario accede a la ruta mediante GET
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Validar si se proporcionó un nombre de usuario
        if not request.form.get("username"):
            flash("Usuario inválido.")
            return redirect("/register")


        # Validar si se proporcionó una contraseña
        elif not request.form.get("password"):
            flash("Contraseña inválida.")
            return redirect("/register")

        # Validar si las contraseñas coinciden
        elif not request.form.get("confirmation") or request.form.get("password") != request.form.get("confirmation"):
            flash("Las contraseñas no coinciden.")
            return redirect("/register")

        # Encriptar la contraseña
        enc_password = generate_password_hash(request.form.get("password"))

        # Conexión a la base de datos
        conn = get_db_connection()
        try:
            # Intentar introducir el nuevo usuario en la base de datos
            conn.execute("INSERT INTO users (username, hash) VALUES(?, ?)",
                         (request.form.get("username"), enc_password))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            flash("El usuario ya existe.")
            return redirect("/register")
        
        # Obtener el usuario registrado
        user = conn.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),)).fetchone()
        conn.close()

        # Iniciar sesión con el usuario recién registrado
        session["user_id"] = user["id"]
        flash("Registro completado!")
        return redirect("/")

    # Mostrar el formulario de registro si el método es GET
    return render_template("register.html")

@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/login")

@app.route("/add", methods=['GET', 'POST'])
def add():
    if request.method == "POST":
        name = request.form.get('nombre')
        categoria = request.form.get('categoria')
        tipo = request.form.get('tipo')
        peso = request.form.get('peso')
        caloriesmin = request.form.get("caloriasmin")
        caloriesmax = request.form.get("caloriasmax")
        proteinsmin = request.form.get("proteinasmin")
        proteinsmax = request.form.get("proteinasmax")
        carbosmin = request.form.get("carbosmin")
        carbosmax = request.form.get("carbosmax")
        grasasmin = request.form.get("grasasmin")
        grasasmax = request.form.get("grasasmax")

        if not name or not categoria or not tipo or not peso  or not caloriesmin or not caloriesmax or not proteinsmin or not proteinsmax or not carbosmin or not carbosmax or not grasasmin or not grasasmax:
            return "Error: Todos los campos son obligatorios", 400
        
        try:
            conn = sqlite3.connect("bdd.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO comidas (nombre, categoria, tipo, peso, caloriasmin, caloriasmax, proteinasmin, proteinasmax, carbosmin, carbosmax, grasasmin, grasasmax) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                           (name, categoria, tipo, peso, caloriesmin, caloriesmax, proteinsmin, proteinsmax, carbosmin, carbosmax, grasasmin, grasasmax))
            conn.commit()
        except sqlite3.Error as e:
            print("Error al insertar en la base de datos:", e)
            return "Error en la base de datos", 500
        finally:
            conn.close()
        if tipo == 'comida':
            flash("¡Comida agregada correctamente!")
        elif tipo == 'bebida':
            flash("Bebida agregada correctamente!")
        return render_template("add.html")
    
    return render_template("add.html")

@app.route("/bdd", methods=['GET'])
def bdd():
    conn = sqlite3.connect("bdd.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, tipo, categoria, peso, caloriasmin, caloriasmax, proteinasmin, proteinasmax, carbosmin, carbosmax, grasasmin, grasasmax FROM comidas")
    comidas = cursor.fetchall()
    conn.close()
    return render_template("bdd.html", comidas=comidas)

@app.route('/autocomplete')
def autocomplete():
    query = request.args.get('q') + '%'
    conn = sqlite3.connect('bdd.db')
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM comidas WHERE nombre LIKE ?", (query,))
    results = cursor.fetchall()
    conn.close()
    suggestions = [item[0] for item in results]
    return jsonify(suggestions)

@app.route('/get-weight')
def get_weight():
    food = request.args.get('food')
    # Realiza la consulta en la base de datos para obtener el peso
    conn = sqlite3.connect('bdd.db')
    cursor = conn.cursor()
    cursor.execute("SELECT peso FROM comidas WHERE nombre = ?", (food,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return jsonify({'weight': result[0]})
    return jsonify({'weight': None})


@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if request.method == 'POST':
        user_id = session.get("user_id")  # Obtén el ID del usuario de la sesión
        nombre = request.form.get('nombre', '').strip()
        edad = request.form.get('edad', '').strip()
        altura = request.form.get('altura', '').replace(',', '.').strip()
        peso = request.form.get('peso', '').replace(',', '.').strip()
        genero = request.form.get('genero', '').strip()
        actividad = request.form.get('actividad', '').strip()
        objetivo = request.form.get('objetivo', '').strip()

        # Validación: Asegúrate de que los campos obligatorios no estén vacíos
        if not nombre or not edad or not altura or not peso or not genero or not actividad or not objetivo:
            flash("Por favor, completa todos los campos requeridos.")
            return redirect("/perfil")

        try:
            edad = int(edad)  # Convierte edad a entero
            altura = float(altura)  # Convierte altura a flotante
            peso = float(peso)  # Convierte peso a flotante
        except ValueError:
            flash("Por favor, ingresa valores numéricos válidos para edad, altura y peso.")
            return redirect("/perfil")
        
        # Llama a la función de cálculo
        calorias_min, calorias_max, proteinas_min, proteinas_max, carbos_min, carbos_max, grasas_min, grasas_max = calcular_necesidades(edad, altura, peso, genero, actividad, objetivo)

        # Conecta con la base de datos y verifica si el perfil ya existe
        conn = sqlite3.connect('bdd.db')
        cursor = conn.cursor()

        # Verifica si ya existe un perfil para este usuario
        cursor.execute('SELECT id FROM perfil WHERE id = ?', (user_id,))
        existing_profile = cursor.fetchone()

        if existing_profile:
            # Si el perfil existe, actualiza los datos
            cursor.execute('''
                UPDATE perfil
                SET nombre = ?, edad = ?, altura = ?, peso = ?, genero = ?, actividad = ?, objetivo = ?
                WHERE id = ?
            ''', (nombre, edad, altura, peso, genero, actividad, objetivo, user_id))
        else:
            # Si no existe, inserta un nuevo registro
            cursor.execute('''
                INSERT INTO perfil (id, nombre, edad, altura, peso, genero, actividad, objetivo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, nombre, edad, altura, peso, genero, actividad, objetivo))

        # Verifica si ya existen datos de necesidades nutricionales para este usuario
        cursor.execute('SELECT user_id FROM necesidades_nutricionales WHERE user_id = ?', (user_id,))
        existing_needs = cursor.fetchone()

        if existing_needs:
            # Si existen, actualiza los datos en la tabla `necesidades_nutricionales`
            cursor.execute('''
                UPDATE necesidades_nutricionales
                SET calorias_min = ?, calorias_max = ?, proteinas_min = ?, proteinas_max = ?, carbos_min = ?, carbos_max = ?, grasas_min = ?, grasas_max = ?
                WHERE user_id = ?
            ''', (calorias_min, calorias_max, proteinas_min, proteinas_max, carbos_min, carbos_max, grasas_min, grasas_max, user_id))
        else:
            # Si no existen, inserta un nuevo registro en la tabla `necesidades_nutricionales`
            cursor.execute('''
                INSERT INTO necesidades_nutricionales (user_id, calorias_min, calorias_max, proteinas_min, proteinas_max, carbos_min, carbos_max, grasas_min, grasas_max)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, calorias_min, calorias_max, proteinas_min, proteinas_max, carbos_min, carbos_max, grasas_min, grasas_max))

        conn.commit()
        conn.close()

        flash("¡Datos ingresados con éxito!")
        return redirect("/perfil")

    user_id = session.get("user_id")  # Obtén el ID del usuario de la sesión

    # Conecta a la base de datos para verificar si hay un perfil existente
    conn = sqlite3.connect('bdd.db')
    cursor = conn.cursor()
    cursor.execute('SELECT nombre, edad, altura, peso, genero, actividad, objetivo FROM perfil WHERE id = ?', (user_id,))
    profile_data = cursor.fetchone()
    cursor.execute('SELECT calorias_min, calorias_max, proteinas_min, proteinas_max, carbos_min, carbos_max, grasas_min, grasas_max FROM necesidades_nutricionales WHERE user_id = ?', (user_id,))
    necesidades_data = cursor.fetchone()
    conn.close()
    return render_template('perfil.html', profile_data=profile_data, necesidades_data=necesidades_data)

def calcular_necesidades(edad, altura, peso, genero, actividad, objetivo):
    # TMB (Tasa Metabólica Basal) según la fórmula de Harris-Benedict
    if genero == 'hombre':
        tmb = 88.362 + (13.397 * peso) + (4.799 * altura) - (5.677 * edad)
    else:
        tmb = 447.593 + (9.247 * peso) + (3.098 * altura) - (4.330 * edad)

    factores_act = {
        'sedentario': 1.2,
        'ligera': 1.375,
        'moderada': 1.55,
        'alta': 1.725,
        'muy-alta': 1.9
    }
    if actividad in factores_act:
        tmb *= factores_act[actividad]

    # Cálculo de macros
    if objetivo == 'bajar':
        calorias_minimas = round(tmb - 500)
        calorias_maximas = round(tmb - 250)
    elif objetivo == 'mantener':
        calorias_minimas = round(tmb)
        calorias_maximas = round(tmb)
    elif objetivo == 'ganar':
        calorias_minimas = round(tmb + 250)
        calorias_maximas = round(tmb + 500)
    else:
        calorias_minimas = calorias_maximas = tmb

    # Cálculo de proteínas (esto no cambia, ya que es independiente del objetivo en la mayoría de las recomendaciones)
    # Inicialmente, establecemos un valor por defecto para las proteínas mínimas y máximas.
    proteinas_minimas = round(peso * 1.2)
    proteinas_maximas = round(peso * 1.5)

    # Dependiendo del objetivo, ajustamos las proteínas máximas.
    if objetivo == 'bajar':
        # Para bajar de peso, mantenemos las proteínas mínimas y máximas en los valores por defecto.
        proteinas_maximas = round(peso * 1.5)
    elif objetivo == 'mantener':
        # Para mantener el peso, usamos las proteínas mínimas y máximas ya establecidas.
        proteinas_maximas = round(peso * 1.5)
    elif objetivo == 'ganar':
        # Para ganar masa muscular, aumentamos las proteínas.
        proteinas_minimas = round(peso * 1.6)
        proteinas_maximas = round(peso * 2.2)
    
    # Cálculo de carbohidratos y grasas
    # Aproximadamente 45-65% de las calorías deben provenir de carbohidratos y 20-35% de grasas
    carbos_min = round(0.45 * calorias_minimas / 4)
    carbos_max = round(0.65 * calorias_maximas / 4)
    grasas_min = round(0.2 * calorias_minimas / 9)
    grasas_max = round(0.35 * calorias_maximas / 9)

    return calorias_minimas, calorias_maximas, proteinas_minimas, proteinas_maximas, carbos_min, carbos_max, grasas_min, grasas_max

@app.route('/guardar-medicion', methods=['POST'])
def guardar_medicion():
    # Obtener el user_id de la sesión
    user_id = session.get("user_id")
    if user_id:
        # Obtener los datos del formulario
        calorias = request.form.get('caloriasprom')
        proteinas = request.form.get('proteinasprom')
        carbohidratos = request.form.get('carbohidratosprom')
        grasas = request.form.get('grasasprom')
        fecha_actual = date.today().strftime('%d-%m-%Y')
        dia_semana = date.today().strftime('%A')

        if not calorias or not proteinas or not carbohidratos or not grasas:
            flash("Faltan datos para ser guardados.")
            return redirect("/")

        # Conectar a la base de datos y guardar los datos
        conn = sqlite3.connect('bdd.db')
        cursor = conn.cursor()

        cursor.execute('SELECT fecha FROM historial WHERE fecha = ? AND user_id = ?', (fecha_actual, user_id))
        medicion_existente = cursor.fetchone()

        if medicion_existente:
            cursor.execute('''
                UPDATE historial
                SET calorias_promedio = ?, proteinas_promedio = ?, carbohidratos_promedio = ?, grasas_promedio = ?
                WHERE user_id = ? AND fecha = ?
            ''', (calorias, proteinas, carbohidratos, grasas, user_id, fecha_actual))
        else:
            cursor.execute('''
                INSERT INTO historial (user_id, fecha, dia_semana, calorias_promedio, proteinas_promedio, carbohidratos_promedio, grasas_promedio)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, fecha_actual, dia_semana, calorias, proteinas, carbohidratos, grasas))

        conn.commit()
        conn.close()

        flash("Medición guardada con éxito.")
        return redirect('/historial')
    return redirect('/')

@app.route('/historial', methods=['GET'])
def historial():
    user_id = session.get("user_id")
    if not user_id:
        flash("No estás autenticado.")
        return redirect("/")

    conn = sqlite3.connect("bdd.db")
    cursor = conn.cursor()
    cursor.execute("SELECT fecha, dia_semana, calorias_promedio, proteinas_promedio, carbohidratos_promedio, grasas_promedio FROM historial WHERE user_id = ?", (user_id,))
    historial = cursor.fetchall()
    conn.close()
    
    if not historial:
        flash("No has guardado mediciones aún")
        return redirect("/")

    return render_template("historial.html", historial=historial)

@app.route("/config")
@login_required
def config():
    return render_template("config.html")


