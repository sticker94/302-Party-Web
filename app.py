from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import requests
import random
import string
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')

DATABASE = 'wise_old_man.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                rank TEXT,
                points INTEGER,
                given_points INTEGER
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY,
                character_name TEXT NOT NULL,
                replit_user_id TEXT NOT NULL,
                replit_user_name TEXT NOT NULL,
                verification_key TEXT,
                verified BOOLEAN
            )
        ''')

def get_group_data(group_id):
    response = requests.get(f"https://api.wiseoldman.net/v2/groups/{group_id}")
    if response.status_code == 200:
        return response.json()
    return None

def generate_verification_key(length=6):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for i in range(length))

@app.route('/')
def index():
    replit_user_id = request.headers.get('X-Replit-User-Id')
    replit_user_name = request.headers.get('X-Replit-User-Name')

    group_id = 6117
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'username')
    filter_rank = request.args.get('rank', '')

    group_data = get_group_data(group_id)
    if group_data:
        memberships = group_data.get('memberships', [])
        members = [{'username': member['player']['username'],
                    'rank': member['role'],
                    'points': 0,
                    'given_points': 0} for member in memberships]

        with get_db() as conn:
            for member in members:
                conn.execute('INSERT OR REPLACE INTO members (username, rank, points, given_points) VALUES (?, ?, ?, ?)',
                             (member['username'], member['rank'], member['points'], member['given_points']))

        query = 'SELECT * FROM members WHERE 1=1'
        if search_query:
            query += f" AND username LIKE '%{search_query}%'"
        if filter_rank:
            query += f" AND rank = '{filter_rank}'"
        query += f" ORDER BY {sort_by}"
        with get_db() as conn:
            members = conn.execute(query).fetchall()

        return render_template('index.html', group=group_data, members=members, search=search_query, sort=sort_by, rank=filter_rank, replit_user_name=replit_user_name)
    else:
        return render_template('error.html', message="Group not found"), 404

@app.route('/config', methods=['GET', 'POST'])
def config():
    replit_user_name = request.headers.get('X-Replit-User-Name')
    if not replit_user_name:
        return redirect(url_for('index'))

    if request.method == 'POST':
        rank = request.form['rank']
        total_points = int(request.form['total_points'])
        with get_db() as conn:
            conn.execute('REPLACE INTO config (rank, total_points) VALUES (?, ?)', (rank, total_points))
    return render_template('config.html', replit_user_name=replit_user_name)

@app.route('/player_config', methods=['GET', 'POST'])
def player_config():
    replit_user_id = request.headers.get('X-Replit-User-Id')
    replit_user_name = request.headers.get('X-Replit-User-Name')
    if not replit_user_name:
        return redirect(url_for('index'))

    if request.method == 'POST':
        character_name = request.form['character_name']
        verification_key = generate_verification_key()
        with get_db() as conn:
            existing_character = conn.execute('SELECT * FROM characters WHERE character_name = ? AND replit_user_id = ?',
                                              (character_name, replit_user_id)).fetchone()
            if not existing_character:
                conn.execute('INSERT INTO characters (character_name, replit_user_id, replit_user_name, verification_key, verified) VALUES (?, ?, ?, ?, ?)',
                             (character_name, replit_user_id, replit_user_name, verification_key, False))
                message = "Character added successfully."
            else:
                message = "Character already exists."

            characters = conn.execute('SELECT * FROM characters WHERE replit_user_id = ?', (replit_user_id,)).fetchall()

        return render_template('player_config.html', message=message, replit_user_name=replit_user_name, token=verification_key, characters=characters)

    with get_db() as conn:
        characters = conn.execute('SELECT * FROM characters WHERE replit_user_id = ?', (replit_user_id,)).fetchall()
    return render_template('player_config.html', replit_user_name=replit_user_name, characters=characters)

@app.route('/assign_points', methods=['POST'])
def assign_points():
    replit_user_name = request.headers.get('X-Replit-User-Name')
    if not replit_user_name:
        return redirect(url_for('index'))

    username = request.form['username']
    points = int(request.form['points'])
    with get_db() as conn:
        conn.execute('UPDATE members SET points = points + ? WHERE username = ?', (points, username))
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

@app.route('/verify_character', methods=['POST'])
def verify_character():
    data = request.json
    character_name = data.get('character_name')
    verification_key = data.get('verification_key')

    with get_db() as conn:
        character = conn.execute('SELECT * FROM characters WHERE character_name = ? AND verification_key = ?',
                                 (character_name, verification_key)).fetchone()
        if character:
            conn.execute('UPDATE characters SET verified = ? WHERE character_name = ? AND verification_key = ?',
                         (True, character_name, verification_key))
            return jsonify({"status": "success", "message": "Character verified."}), 200
        else:
            return jsonify({"status": "failure", "message": "Verification failed."}), 400

if __name__ == '__main__':
    init_db()  # Initialize the database when the app starts
    app.run(host='0.0.0.0', port=3000, debug=True)
