from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import random
import requests
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Auth0 Configuration
AUTH0_CLIENT_ID = os.getenv('AUTH0_CLIENT_ID')
AUTH0_CLIENT_SECRET = os.getenv('AUTH0_CLIENT_SECRET')
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_CALLBACK_URL = 'http://localhost:5000/callback'

# Initialize OAuth
oauth = OAuth(app)
auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=f'https://{AUTH0_DOMAIN}',
    access_token_url=f'https://{AUTH0_DOMAIN}/oauth/token',
    authorize_url=f'https://{AUTH0_DOMAIN}/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)

# Database configuration
DATABASE = 'wise_old_man.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

# Create tables if they don't exist
def init_db():
    with get_db() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS members (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        rank TEXT,
                        points INTEGER DEFAULT 0,
                        given_points INTEGER DEFAULT 0)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        auth0_id TEXT UNIQUE,
                        email TEXT UNIQUE,
                        name TEXT,
                        verified BOOLEAN DEFAULT FALSE,
                        token TEXT)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS config (
                        rank TEXT UNIQUE,
                        total_points INTEGER)''')

# Initialize database
init_db()

def generate_token():
    """Generates a unique token in the format ###-###-###"""
    return f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(100, 999)}"

def get_group_data(group_id):
    response = requests.get(f"https://api.wiseoldman.net/v2/groups/{group_id}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching group data: {response.status_code}")
        return None

@app.route('/')
def index():
    group_id = 6117
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'username')
    filter_rank = request.args.get('rank', '')

    group_data = get_group_data(group_id)
    if group_data:
        memberships = group_data.get('memberships', [])
        members = [(member['player']['id'],    # Unique ID
                    member['player']['username'],  # Username
                    member['role'],  # Role as rank
                    0)  # Placeholder for points
                   for member in memberships]

        # Store members in the database
        with get_db() as conn:
            for member in members:
                conn.execute('REPLACE INTO members (username, rank, points, given_points) VALUES (?, ?, ?, ?)',
                             (member[1], member[2], member[3], member[3]))  # Storing username, rank, points, given_points

        # Fetch members from the database with optional filtering and sorting
        query = 'SELECT * FROM members WHERE 1=1'
        if search_query:
            query += f" AND username LIKE '%{search_query}%'"
        if filter_rank:
            query += f" AND rank = '{filter_rank}'"
        query += f" ORDER BY {sort_by}"
        with get_db() as conn:
            members = conn.execute(query).fetchall()

        # Extract unique ranks from the members data
        unique_ranks = sorted(set(member[2] for member in members), key=lambda x: x.lower())

        # Calculate total and remaining points for the user if logged in
        user_total_points = 0
        user_remaining_points = 0
        if 'profile' in session:
            with get_db() as conn:
                user_info = conn.execute('SELECT rank, given_points FROM members WHERE username = ?', (session['username'],)).fetchone()
                if user_info:
                    rank, given_points = user_info
                    total_points_info = conn.execute('SELECT total_points FROM config WHERE rank = ?', (rank,)).fetchone()
                    if total_points_info:
                        user_total_points = total_points_info[0]
                        user_remaining_points = user_total_points - given_points

        return render_template('index.html', group=group_data, members=members, search=search_query, sort=sort_by, filter_rank=filter_rank, ranks=unique_ranks, total_points=user_total_points, remaining_points=user_remaining_points)
    else:
        return render_template('error.html', message="Group not found"), 404


@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL)

@app.route('/callback')
def callback():
    auth0.authorize_access_token()
    userinfo = auth0.get('userinfo').json()
    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture'],
        'email': userinfo['email']
    }
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(
        f'https://{AUTH0_DOMAIN}/v2/logout?client_id={AUTH0_CLIENT_ID}&returnTo={url_for("index", _external=True)}'
    )

@app.route('/assign_points', methods=['POST'])
def assign_points():
    if 'profile' in session and session.get('admin'):
        username = request.form['username']
        points = int(request.form['points'])
        with get_db() as conn:
            conn.execute('UPDATE members SET points = points + ? WHERE username = ?', (points, username))
            conn.execute('UPDATE members SET given_points = given_points + ? WHERE username = ?', (points, session['profile']['name']))
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.route('/config', methods=['GET', 'POST'])
def config():
    if 'profile' in session and session.get('admin'):
        if request.method == 'POST':
            # Update the config with the provided points for each rank
            ranks = request.form.getlist('rank')
            points = request.form.getlist('points')
            with get_db() as conn:
                for rank, total_points in zip(ranks, points):
                    conn.execute('REPLACE INTO config (rank, total_points) VALUES (?, ?)', (rank, total_points))

        # Fetch the current configuration
        with get_db() as conn:
            configs = conn.execute('SELECT * FROM config').fetchall()

        return render_template('config.html', configs=configs)
    else:
        return redirect(url_for('login'))

@app.route('/player_config', methods=['GET', 'POST'])
def player_config():
    if 'profile' in session:
        if request.method == 'POST':
            character_name = request.form['character_name']
            token = generate_token()
            with get_db() as conn:
                conn.execute('REPLACE INTO members (username, token) VALUES (?, ?)', (character_name, token))
                conn.execute('UPDATE users SET verified = 0 WHERE auth0_id = ?', (session['profile']['user_id'],))
            return render_template('player_config.html', message="Character added. Please verify in RuneLite using the token provided.", token=token)

        # Fetch the current characters
        with get_db() as conn:
            characters = conn.execute('SELECT * FROM members WHERE username = ?', (session['profile']['name'],)).fetchall()

        return render_template('player_config.html', characters=characters)
    else:
        return redirect(url_for('login'))

def verify_token(username, token):
    with get_db() as conn:
        db_token = conn.execute('SELECT token FROM members WHERE username = ?', (username,)).fetchone()
        if db_token and db_token[0] == token:
            conn.execute('UPDATE users SET verified = 1 WHERE auth0_id = (SELECT auth0_id FROM users WHERE name = ?)', (username,))
            return True
    return False

if __name__ == '__main__':
    app.run(debug=True)
