import os
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import requests

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')

DATABASE = 'wise_old_man.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_group_data(group_id):
    response = requests.get(f"https://api.wiseoldman.net/v2/groups/{group_id}")
    if response.status_code == 200:
        return response.json()
    return None

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
                conn.execute('REPLACE INTO members (username, rank, points, given_points) VALUES (?, ?, ?, ?)',
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
    replit_user_name = request.headers.get('X-Replit-User-Name')
    if not replit_user_name:
        return redirect(url_for('index'))

    if request.method == 'POST':
        character_name = request.form['character_name']
        # Logic to handle character configuration
        message = "Character added successfully"  # Example message
        # Possibly generate and display a verification token here
        return render_template('player_config.html', message=message, replit_user_name=replit_user_name)
    return render_template('player_config.html', replit_user_name=replit_user_name)

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
    # Replit handles the deauthentication via their script
    # If you want to clear any additional session data, you can do so here
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
