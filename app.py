from flask import Flask, render_template, request, redirect, url_for, jsonify
import pymysql
import requests
import random
import string
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')

DATABASE = {
    'host': os.getenv('RM_DB_HOST'),
    'user': os.getenv('RM_DB_USER'),
    'password': os.getenv('RM_DB_PASS'),
    'database': os.getenv('RM_DB_NAME')
}

def get_db():
    try:
        conn = pymysql.connect(
            host=DATABASE['host'],
            port=3306,  # Ensure you specify the MySQL port
            user=DATABASE['user'],
            password=DATABASE['password'],
            database=DATABASE['database'],
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    return None

def init_db():
    conn = get_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                rank VARCHAR(255),
                points INT,
                given_points INT,
                UNIQUE(username)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS characters (
                id INT AUTO_INCREMENT PRIMARY KEY,
                character_name VARCHAR(255) NOT NULL,
                replit_user_id VARCHAR(255) NOT NULL,
                replit_user_name VARCHAR(255) NOT NULL,
                verification_key VARCHAR(255),
                verified BOOLEAN,
                UNIQUE(character_name, replit_user_id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                id INT AUTO_INCREMENT PRIMARY KEY,
                rank VARCHAR(255),
                total_points INT,
                UNIQUE(rank)
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()

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

        conn = get_db()
        if conn:
            cursor = conn.cursor()
            for member in members:
                cursor.execute('INSERT INTO members (username, rank, points, given_points) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE rank=%s, points=%s, given_points=%s',
                               (member['username'], member['rank'], member['points'], member['given_points'], member['rank'], member['points'], member['given_points']))
            conn.commit()
            cursor.close()
            conn.close()

        query = 'SELECT * FROM members WHERE 1=1'
        if search_query:
            query += f" AND username LIKE '%{search_query}%'"
        if filter_rank:
            query += f" AND rank = '{filter_rank}'"
        query += f" ORDER BY {sort_by}"

        conn = get_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute(query)
            members = cursor.fetchall()
            cursor.close()
            conn.close()

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
        conn = get_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO config (rank, total_points) VALUES (%s, %s) ON DUPLICATE KEY UPDATE total_points=%s', (rank, total_points, total_points))
            conn.commit()
            cursor.close()
            conn.close()
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
        conn = get_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM characters WHERE character_name = %s AND replit_user_id = %s', (character_name, replit_user_id))
            existing_character = cursor.fetchone()
            if not existing_character:
                cursor.execute('INSERT INTO characters (character_name, replit_user_id, replit_user_name, verification_key, verified) VALUES (%s, %s, %s, %s, %s)',
                               (character_name, replit_user_id, replit_user_name, verification_key, False))
                message = "Character added successfully."
            else:
                message = "Character already exists."
            conn.commit()
            cursor.execute('SELECT * FROM characters WHERE replit_user_id = %s', (replit_user_id,))
            characters = cursor.fetchall()
            cursor.close()
            conn.close()
        return render_template('player_config.html', message=message, replit_user_name=replit_user_name, token=verification_key, characters=characters)

    conn = get_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM characters WHERE replit_user_id = %s', (replit_user_id,))
        characters = cursor.fetchall()
        cursor.close()
        conn.close()
    return render_template('player_config.html', replit_user_name=replit_user_name, characters=characters)

@app.route('/assign_points', methods=['POST'])
def assign_points():
    replit_user_name = request.headers.get('X-Replit-User-Name')
    if not replit_user_name:
        return redirect(url_for('index'))

    username = request.form['username']
    points = int(request.form['points'])
    conn = get_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE members SET points = points + %s WHERE username = %s', (points, username))
        conn.commit()
        cursor.close()
        conn.close()
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

@app.route('/verify_character', methods=['POST'])
def verify_character():
    data = request.json
    character_name = data.get('character_name')
    verification_key = data.get('verification_key')

    conn = get_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM characters WHERE character_name = %s AND verification_key = %s',
                       (character_name, verification_key))
        character = cursor.fetchone()
        if character:
            cursor.execute('UPDATE characters SET verified = %s WHERE character_name = %s AND verification_key = %s',
                           (True, character_name, verification_key))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({"status": "success", "message": "Character verified."}), 200
        else:
            cursor.close()
            conn.close()
            return jsonify({"status": "failure", "message": "Verification failed."}), 400

if __name__ == '__main__':
    init_db()  # Initialize the database when the app starts
    app.run(host='0.0.0.0', port=3000, debug=True)
