import sqlite3
import json
from flask import Flask, request, session, jsonify, render_template, g, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Configuration de l'application
app = Flask(__name__, instance_relative_config=True)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['DATABASE'] = os.path.join(app.instance_path, 'database.db')
# Définir le dossier pour les cours en PDF
app.config['COURSE_FOLDER'] = os.path.join(app.root_path, 'courses_pdf')


# S'assurer que le dossier 'instance' et 'courses_pdf' existent
try:
    os.makedirs(app.instance_path)
    os.makedirs(app.config['COURSE_FOLDER'], exist_ok=True)
except OSError:
    pass

# --- Gestion de la base de données ---

def get_db():
    """Ouvre une nouvelle connexion à la base de données si aucune n'existe pour le contexte actuel."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Ferme la connexion à la base de données."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialise la base de données en créant les tables."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('init-db')
def init_db_command():
    """Commande en ligne pour initialiser la base de données."""
    init_db()
    print('Base de données initialisée.')

app.teardown_appcontext(close_db)

# --- Routes principales ---

@app.route('/')
def index():
    """Sert la page principale de l'application (Single Page Application)."""
    return render_template('index.html')

# --- API pour l'authentification ---

@app.route('/api/register', methods=['POST'])
def register():
    """API pour l'inscription d'un nouvel utilisateur."""
    data = request.get_json()
    full_name = data.get('fullName')
    email = data.get('email')
    nickname = data.get('nickname')
    password = data.get('password')

    if not all([full_name, email, nickname, password]):
        return jsonify({'success': False, 'message': 'Tous les champs sont requis.'}), 400

    db = get_db()
    # Vérifier si le pseudo ou l'email existe déjà
    if db.execute('SELECT id FROM user WHERE nickname = ? OR email = ?', (nickname, email)).fetchone():
        return jsonify({'success': False, 'message': 'Ce pseudo ou cet email est déjà utilisé.'}), 409

    # Hacher le mot de passe et insérer le nouvel utilisateur
    hashed_password = generate_password_hash(password)
    db.execute(
        'INSERT INTO user (full_name, email, nickname, password) VALUES (?, ?, ?, ?)',
        (full_name, email, nickname, hashed_password)
    )
    db.commit()

    return jsonify({'success': True, 'message': 'Inscription réussie ! Vous pouvez maintenant vous connecter.'})

@app.route('/api/login', methods=['POST'])
def login():
    """API pour la connexion d'un utilisateur."""
    data = request.get_json()
    nickname = data.get('nickname')
    password = data.get('password')

    db = get_db()
    user = db.execute('SELECT * FROM user WHERE nickname = ?', (nickname,)).fetchone()

    if user and check_password_hash(user['password'], password):
        # Enregistrer l'utilisateur dans la session
        session.clear()
        session['user_id'] = user['id']
        session['user_nickname'] = user['nickname']
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Pseudo ou mot de passe incorrect.'}), 401

@app.route('/api/logout')
def logout():
    """Déconnexion de l'utilisateur."""
    session.clear()
    return jsonify({'success': True})

@app.route('/api/check_session')
def check_session():
    """Vérifie si un utilisateur est connecté."""
    if 'user_id' in session:
        return jsonify({'logged_in': True})
    return jsonify({'logged_in': False})

# --- API pour les données de l'application ---

def get_user_data():
    """Récupère les données complètes de l'utilisateur connecté."""
    if 'user_id' not in session:
        return None
    
    user_id = session['user_id']
    db = get_db()
    user = db.execute('SELECT id, full_name, email, nickname FROM user WHERE id = ?', (user_id,)).fetchone()
    
    if not user:
        return None

    progress_data = db.execute('SELECT subject, score FROM progress WHERE user_id = ?', (user_id,)).fetchall()
    progress = {item['subject']: item['score'] for item in progress_data}

    return {
        'id': user['id'],
        'fullName': user['full_name'],
        'email': user['email'],
        'nickname': user['nickname'],
        'progress': progress
    }

def get_all_courses_info():
    """Charge les informations de base de tous les cours depuis le JSON."""
    with open('quizzes.json', 'r', encoding='utf-8') as f:
        quizzes = json.load(f)
    
    courses_info = {
        subject: {
            "title": data.get("title", "Sans titre"),
            "description": data.get("description", ""),
            "emoji": data.get("emoji", "❓"),
            "professor": data.get("professor", "N/A"),
            "pdf_link": data.get("pdf_link")
        } for subject, data in quizzes.items()
    }
    return courses_info

@app.route('/api/data')
def get_app_data():
    """Fournit les données initiales à l'application (utilisateur et cours)."""
    if 'user_id' not in session:
        return jsonify({'error': 'Non autorisé'}), 401

    user_info = get_user_data()
    courses_info = get_all_courses_info()

    return jsonify({
        'user': user_info,
        'courses': courses_info
    })

@app.route('/api/courses')
def get_courses():
    """Fournit la liste des cours publiquement pour la page d'accueil."""
    try:
        courses_info = get_all_courses_info()
        return jsonify(courses_info)
    except FileNotFoundError:
        return jsonify({'error': 'Fichier de quiz non trouvé'}), 500

# --- ROUTE POUR SERVIR LES PDF ---
@app.route('/courses/<path:filename>')
def serve_course_pdf(filename):
    """Sert un fichier PDF depuis le dossier des cours."""
    return send_from_directory(app.config['COURSE_FOLDER'], filename)


@app.route('/api/quiz/<subject>')
def get_quiz(subject):
    """Fournit les questions pour un quiz spécifique."""
    if 'user_id' not in session:
        return jsonify({'error': 'Non autorisé'}), 401
    
    try:
        with open('quizzes.json', 'r', encoding='utf-8') as f:
            quizzes = json.load(f)
        if subject in quizzes:
            return jsonify(quizzes[subject]["questions"])
        else:
            return jsonify({'error': 'Quiz non trouvé'}), 404
    except FileNotFoundError:
        return jsonify({'error': 'Fichier de quiz non trouvé'}), 500

@app.route('/api/progress', methods=['POST'])
def update_progress():
    """Met à jour la progression d'un utilisateur pour un quiz."""
    if 'user_id' not in session:
        return jsonify({'error': 'Non autorisé'}), 401

    data = request.get_json()
    subject = data.get('subject')
    score = data.get('score')
    user_id = session['user_id']

    db = get_db()
    # Vérifier s'il existe déjà une entrée pour ce quiz
    existing = db.execute('SELECT id, score FROM progress WHERE user_id = ? AND subject = ?', (user_id, subject)).fetchone()

    if existing:
        # Mettre à jour le score s'il est meilleur
        if score > existing['score']:
            db.execute('UPDATE progress SET score = ? WHERE id = ?', (score, existing['id']))
    else:
        # Insérer une nouvelle entrée
        db.execute('INSERT INTO progress (user_id, subject, score) VALUES (?, ?, ?)', (user_id, subject, score))
    
    db.commit()
    return jsonify({'success': True})

if __name__ == '__main__':
    # Ne pas utiliser en production
    app.run(debug=True)
