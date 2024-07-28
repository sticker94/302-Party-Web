import os
from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from replit import web
import sqlite3
import uuid
import requests

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')  # Set this in your Replit secrets

DATABASE = 'wise_old_man.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Fetch group data from Wise Old Man API
def get_group_data(group_id):
    response = requests.get(f"https://api.wiseoldman.net/v2/groups/{group_id}")
    if response.status_code == 200:
        return response.json()
    return None

@app.route('/')
def index():
    if 'user_name' not in session:
        return redirect(url_for('login'))
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

        # Store members in the database
        with get_db() as conn:
            for member in members:
                conn.execute('REPLACE INTO members (username, rank, points, given_points) VALUES (?, ?, ?, ?)',
                             (member['username'], member['rank'], member['points'], member['given_points']))

        # Fetch members from the database with optional filtering and sorting
        query = 'SELECT * FROM members WHERE 1=1'
        if search_query:
            query += f" AND username LIKE '%{search_query}%'"
        if filter_rank:
            query += f" AND rank = '{filter_rank}'"
        query += f" ORDER BY {sort_by}"
        with get_db() as conn:
            members = conn.execute(query).fetchall()

        # Calculate total and remaining points for the user if logged in
        user_total_points = 0
        user_remaining_points = 0
        if 'user_name' in session:
            with get_db() as conn:
                user_info = conn.execute('SELECT rank, given_points FROM members WHERE username = ?', (session['user_name'],)).fetchone()
                if user_info:
                    rank, given_points = user_info
                    total_points_info = conn.execute('SELECT total_points FROM config WHERE rank = ?', (rank,)).fetchone()
                    if total_points_info:
                        user_total_points = total_points_info[0]
                        user_remaining_points = user_total_points - given_points

        return render_template('index.html', group=group_data, members=members, search=search_query, sort=sort_by, rank=filter_rank, total_points=user_total_points, remaining_points=user_remaining_points)
    else:
        return render_template('error.html', message="Group not found"), 404

@app.route('/login')
def login():
    web.auth.login()

@app.route('/logout')
def logout():
    web.auth.deauthenticate()
    session.clear()  # Clear the session
    return redirect(url_for('index'))

@app.route('/callback')
def callback():
    # Replit authentication should manage the session
    return redirect(url_for('index'))

@app.route('/config', methods=['GET', 'POST'])
def config():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        rank = request.form['rank']
        total_points = int(request.form['total_points'])
        with get_db() as conn:
            conn.execute('REPLACE INTO config (rank, total_points) VALUES (?, ?)', (rank, total_points))
    return render_template('config.html')

@app.route('/player_config', methods=['GET', 'POST'])
def player_config():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        username = session['user_name']
        token = request.form['token']
        with get_db() as conn:
            conn.execute('REPLACE INTO members (username, token) VALUES (?, ?)', (username, token))
    return render_template('player_config.html')

@app.route('/assign_points', methods=['POST'])
def assign_points():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    username = request.form['username']
    points = int(request.form['points'])
    with get_db() as conn:
        conn.execute('UPDATE members SET points = points + ? WHERE username = ?', (points, username))
        if 'user_name' in session:
            conn.execute('UPDATE members SET given_points = given_points + ? WHERE username = ?', (points, session['user_name']))
    return redirect(url_for('index'))

def generate_token():
    return str(uuid.uuid4()).replace('-', '')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
