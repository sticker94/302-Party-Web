from flask import Flask, render_template, request, redirect, url_for, jsonify
import mysql.connector
import requests
import random
import string
import os
import time
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

# Load environment variables from .env file
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
        conn = mysql.connector.connect(
            host=DATABASE['host'],
            port=3306,
            user=DATABASE['user'],
            password=DATABASE['password'],
            database=DATABASE['database']
        )
        return conn
    except mysql.connector.Error as e:
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
                rank_order INT,
                UNIQUE(rank)
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
        update_config_with_ranks()

def update_config_with_ranks():
    conn = get_db()
    if conn:
        cursor = conn.cursor()
        for rank in rank_mapping.values():
            cursor.execute('INSERT INTO config (rank, total_points, rank_order) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE rank=%s',
                           (rank, 0, 0, rank))
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

def fetch_wom_ranks():
    response = requests.get('https://api.wiseoldman.net/v2/groups/type-definitions')
    if response.status_code == 200:
        return response.json().get('roleDefinitions', [])
    return []

def map_wom_ranks(wom_ranks):
    rank_mapping = {}
    for rank in wom_ranks:
        rank_mapping[rank['id']] = rank['name']
    return rank_mapping

wom_ranks = fetch_wom_ranks()
rank_mapping = map_wom_ranks(wom_ranks)

def update_player_data():
    while True:
        try:
            group_id = 6117
            group_data = get_group_data(group_id)
            if group_data:
                memberships = group_data.get('memberships', [])
                members = [{'username': member['player']['username'],
                            'rank': rank_mapping.get(member.get('roleId', -1), 'Unknown'),
                            'points': 0,
                            'given_points': 0} for member in memberships]
                conn = get_db()
                if conn:
                    cursor = conn.cursor()
                    for member in members:
                        print(f"Inserting/updating member: {member['username']}")
                        cursor.execute('INSERT INTO members (username, rank, points, given_points) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE rank=%s',
                                       (member['username'], member['rank'], member['points'], member['given_points'], member['rank']))
                    conn.commit()
                    cursor.close()
                    conn.close()
            time.sleep(600)  # Sleep for 10 minutes
        except mysql.connector.Error as e:
            print(f"Database Error (UPDATE): {e}")
            time.sleep(600)  # Sleep for 10 minutes even if there's an error

def reset_points_weekly():
    while True:
        try:
            conn = get_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE members SET points = 0, given_points = 0')
                conn.commit()
                cursor.close()
                conn.close()
            time.sleep(604800)  # Sleep for 1 week
        except mysql.connector.Error as e:
            print(f"Database Error (RESET): {e}")
            time.sleep(604800)  # Sleep for 1 week even if there's an error

@app.route('/')
def index():
    replit_user_id = request.headers.get('X-Replit-User-Id')
    replit_user_name = request.headers.get('X-Replit-User-Name')

    group_id = 6117
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'username')
    filter_rank = request.args.get('rank', '')

    error_message = None
    members = []
    ranks = []

    total_points = 0
    points_available = 0

    query = 'SELECT DISTINCT rank FROM members ORDER BY rank'
    try:
        conn = get_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            ranks = cursor.fetchall()
            cursor.close()
            conn.close()
            print(f"Fetched ranks: {ranks}")
    except mysql.connector.Error as e:
        print(f"Database Error (SELECT RANKS): {e}")
        error_message = "Error fetching ranks from the database."

    query = 'SELECT * FROM members WHERE 1=1'
    if search_query:
        query += f" AND username LIKE '%{search_query}%'"
    if filter_rank:
        query += f" AND rank = '{filter_rank}'"
    query += f" ORDER BY {sort_by}"

    try:
        conn = get_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            print(f"Executing query: {query}")
            cursor.execute(query)
            members = cursor.fetchall()

            # Calculate total_points and points_available for the logged-in user
            if replit_user_id:
                cursor.execute('''
                    SELECT c.rank, c.total_points, m.given_points
                    FROM characters ch
                    JOIN members m ON ch.character_name = m.username
                    JOIN config c ON m.rank = c.rank
                    WHERE ch.replit_user_id = %s
                    ORDER BY c.rank_order ASC
                    LIMIT 1
                ''', (replit_user_id,))
                result = cursor.fetchone()
                if result:
                    total_points = result['total_points']
                    points_available = total_points - result['given_points']

            cursor.close()
            conn.close()
            print(f"Fetched members: {members}")
    except mysql.connector.Error as e:
        print(f"Database Error (SELECT MEMBERS): {e}")
        error_message = "Error fetching members from the database."

    return render_template('index.html', members=members, search=search_query, sort=sort_by, rank=filter_rank, ranks=ranks, replit_user_name=replit_user_name, error_message=error_message, total_points=total_points, points_available=points_available)

@app.route('/config', methods=['GET', 'POST'])
def config():
    replit_user_name = request.headers.get('X-Replit-User-Name')
    if not replit_user_name:
        return redirect(url_for('index'))

    configs = []

    if request.method == 'POST':
        try:
            conn = get_db()
            if conn:
                cursor = conn.cursor()
                for rank, total_points in zip(request.form.getlist('rank'), request.form.getlist('total_points')):
                    cursor.execute('INSERT INTO config (rank, total_points) VALUES (%s, %s) ON DUPLICATE KEY UPDATE total_points=%s',
                                   (rank, total_points, total_points))
                conn.commit()
                cursor.close()
                conn.close()
        except mysql.connector.Error as e:
            print(f"Database Error: {e}")

    try:
        conn = get_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM config ORDER BY rank_order')
            configs = cursor.fetchall()
            cursor.close()
            conn.close()
    except mysql.connector.Error as e:
        print(f"Database Error: {e}")

    return render_template('config.html', replit_user_name=replit_user_name, configs=configs)

@app.route('/player_config', methods=['GET', 'POST'])
def player_config():
    replit_user_id = request.headers.get('X-Replit-User-Id')
    replit_user_name = request.headers.get('X-Replit-User-Name')
    if not replit_user_name:
        return redirect(url_for('index'))

    message = None
    token = None
    characters = []

    if request.method == 'POST':
        character_name = request.form['character_name']
        verification_key = generate_verification_key()
        try:
            conn = get_db()
            if conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute('SELECT * FROM characters WHERE character_name = %s', (character_name,))
                existing_character = cursor.fetchone()
                if existing_character is not None and isinstance(existing_character, dict):
                    if existing_character['replit_user_id'] == replit_user_id:
                        message = "Character already exists and belongs to you."
                        token = existing_character['verification_key']
                    else:
                        message = "Character already claimed by another user."
                else:
                    cursor.execute('INSERT INTO characters (character_name, replit_user_id, replit_user_name, verification_key, verified) VALUES (%s, %s, %s, %s, %s)',
                                   (character_name, replit_user_id, replit_user_name, verification_key, False))
                    conn.commit()
                    message = "Character added successfully."
                    token = verification_key
                cursor.execute('SELECT * FROM characters WHERE replit_user_id = %s', (replit_user_id,))
                characters = cursor.fetchall()
                cursor.close()
                conn.close()
        except mysql.connector.Error as e:
            print(f"Database Error: {e}")
            message = "An error occurred. Please try again later."
    else:
        try:
            conn = get_db()
            if conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute('SELECT * FROM characters WHERE replit_user_id = %s', (replit_user_id,))
                characters = cursor.fetchall()
                cursor.close()
                conn.close()
        except mysql.connector.Error as e:
            print(f"Database Error: {e}")

    return render_template('player_config.html', message=message, replit_user_name=replit_user_name, token=token, characters=characters)

@app.route('/assign_points', methods=['POST'])
def assign_points():
    replit_user_id = request.headers.get('X-Replit-User-Id')
    replit_user_name = request.headers.get('X-Replit-User-Name')
    if not replit_user_name:
        return redirect(url_for('index'))

    username = request.form['username']
    points = int(request.form['points'])
    try:
        conn = get_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE members SET points = points + %s WHERE username = %s', (points, username))
            cursor.execute('''
                UPDATE members m
                JOIN characters ch ON m.username = ch.character_name
                SET m.given_points = m.given_points + %s
                WHERE ch.replit_user_id = %s
            ''', (points, replit_user_id))
            conn.commit()
            cursor.close()
            conn.close()
    except mysql.connector.Error as e:
        print(f"Database Error: {e}")
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

@app.route('/verify_character', methods=['POST'])
def verify_character():
    data = request.json
    character_name = data.get('character_name')
    verification_key = data.get('verification_key')

    try:
        conn = get_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
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
    except mysql.connector.Error as e:
        print(f"Database Error: {e}")
        return jsonify({"status": "failure", "message": "An error occurred. Please try again later."}), 500

def refresh_members():
    group_id = 6117
    group_data = get_group_data(group_id)
    if group_data:
        memberships = group_data.get('memberships', [])
        rank_order = 1  # Initialize rank_order

        for member in memberships[:5]:  # Inspect only the first 5 members for brevity
            print(f"Member data: {member}")
            role = member.get('role', 'Unknown')
            print(f"Processing member: {member['player']['username']}, role: {role}")

        members = [{'username': member['player']['username'],
                    'rank': member.get('role', 'Unknown'),
                    'points': 0,
                    'given_points': 0} for member in memberships]

        try:
            conn = get_db()
            if conn:
                cursor = conn.cursor()
                for member in members:
                    rank = member['rank']
                    print(f"Inserting/updating member: {member['username']} with rank {rank} and order {rank_order}")
                    cursor.execute('INSERT INTO members (username, rank, points, given_points) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE rank=%s',
                                   (member['username'], member['rank'], member['points'], member['given_points'], member['rank']))
                    cursor.execute('INSERT INTO config (rank, rank_order) VALUES (%s, %s) ON DUPLICATE KEY UPDATE rank_order=%s',
                                   (rank, rank_order, rank_order))
                    rank_order += 1
                conn.commit()
                cursor.close()
                conn.close()
        except mysql.connector.Error as e:
            print(f"Database Error (INSERT/UPDATE): {e}")

if __name__ == '__main__':
    init_db()
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=refresh_members, trigger="interval", minutes=10)
    scheduler.start()
    refresh_members()  # Initial load
    app.run(host='0.0.0.0', port=3000, debug=True)
