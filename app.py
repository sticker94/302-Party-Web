from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_from_directory
from flask_cors import CORS
from flask_caching import Cache
import mysql.connector
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')

# Setup caching configuration
cache = Cache(app, config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 600})  # Cache timeout set to 10 minutes

# Database configuration
DATABASE = {
    'host': os.getenv('RM_DB_HOST'),
    'user': os.getenv('RM_DB_USER'),
    'password': os.getenv('RM_DB_PASS'),
    'database': os.getenv('RM_DB_NAME')
}

#API_KEY for GE Tracker
API_KEY = os.getenv('API_KEY')

# Discord OAuth2 Configuration
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI')
DISCORD_GUILD_ID = os.getenv('DISCORD_GUILD_ID')
DISCORD_REQUIRED_ROLE_ID = os.getenv('DISCORD_REQUIRED_ROLE_ID')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
OAUTH2_ENABLED = os.getenv('OAUTH2_ENABLED', 'true').lower() == 'true'

# Utility Functions
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

def exchange_code_for_token(code):
    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_URI,
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post('https://discord.com/api/oauth2/token', data=data, headers=headers)
    return response.json()

def get_user_info(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get('https://discord.com/api/users/@me', headers=headers)
    return response.json()

def get_user_roles(access_token, guild_id):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(f'https://discord.com/api/users/@me/guilds/{guild_id}/member', headers=headers)
    if response.status_code == 200:
        return response.json().get('roles', [])
    return []

def has_required_role(access_token):
    roles = get_user_roles(access_token, DISCORD_GUILD_ID)
    return DISCORD_REQUIRED_ROLE_ID in roles

# Routes for OAuth2 and Main Pages
@app.route('/login')
def login():
    return redirect(f'https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&redirect_uri={DISCORD_REDIRECT_URI}&response_type=code&scope=identify%20guilds')

# Serve the React app from the build folder
@app.route('/')
@app.route('/<path:path>')
def serve_react(path=None):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')
@app.route('/api/members', methods=['GET'])
def get_members():
    if OAUTH2_ENABLED and not session.get('authenticated'):
        return jsonify({'error': 'Not authenticated'}), 401

    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'username')
    filter_rank = request.args.get('rank', '')
    members, ranks, error_message = [], [], None

    # Query for ranks and members
    try:
        conn = get_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT DISTINCT rank FROM members ORDER BY rank')
            ranks = cursor.fetchall()

            query = 'SELECT * FROM members WHERE 1=1'
            if search_query:
                query += f" AND username LIKE '%{search_query}%'"
            if filter_rank:
                query += f" AND rank = '{filter_rank}'"
            query += f" ORDER BY {sort_by}"

            cursor.execute(query)
            members = cursor.fetchall()
            cursor.close()
            conn.close()
    except mysql.connector.Error as e:
        error_message = "Error fetching data from the database."
        print(f"Database Error: {e}")
        return jsonify({'error': error_message}), 500

    return jsonify({
        'members': members,
        'ranks': ranks
    })

# Assign Points Route
@app.route('/api/assign_points', methods=['POST'])
def assign_points():
    if OAUTH2_ENABLED and not session.get('authenticated'):
        return redirect('/login')

    replit_user_id = session.get('replit_user_id', None)
    replit_user_name = session.get('replit_user_name', None)

    if not replit_user_name:
        return redirect(url_for('index'))

    username = request.form['username']
    points = int(request.form['points'])

    try:
        conn = get_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('UPDATE members SET points = points + %s WHERE username = %s', (points, username))
            cursor.execute('''
                UPDATE members m
                JOIN characters ch ON m.username = ch.character_name
                SET m.given_points = m.given_points + %s
                WHERE ch.replit_user_id = %s
            ''', (points, replit_user_id))

            # Get the highest verified character name for the user
            cursor.execute('''
            SELECT ch.character_name
            FROM characters ch
            JOIN members m ON ch.character_name = m.username
            JOIN config c ON m.rank = c.rank
            WHERE ch.replit_user_id = %s AND ch.verified = 1
            ORDER BY c.rank_order ASC
            LIMIT 1
            ''', (replit_user_id,))
            character_result = cursor.fetchone()
            character_name = character_result['character_name'] if character_result else replit_user_name

            conn.commit()
            cursor.close()
            conn.close()

            # Send Discord webhook notification
            message = f"{character_name} assigned {points} points to {username}."
            send_discord_webhook(message)

    except mysql.connector.Error as e:
        print(f"Database Error: {e}")
    pass
@app.route('/api/crafting_smithing/blast_furnace', methods=['GET'])
def get_blast_furnace():
    """Fetch Blast Furnace data from the external API"""
    data = get_api_data('/api/blast-furnace')

    if data:
        return jsonify(data)
    else:
        return jsonify({"error": "Unable to fetch Blast Furnace data"}), 500

@app.route('/api/crafting_smithing/cooking_brewing', methods=['GET'])
def get_cooking_brewing():
    # Fetch data for cooking/brewing
    data = {
        "name": "Cooking/Brewing",
        "items": [
            {"name": "Wine", "profit": 100},
            {"name": "Beer", "profit": 75}
        ]
    }
    return jsonify(data)

# Utility Functions
def get_api_data(api_endpoint, input_params=None):
    """Fetch data from the external API."""
    headers = {
        'Authorization': f'Bearer {API_KEY}',  # Use Bearer token for authentication
        'Accept': 'application/x.getracker.v2.1+json',
        'User-Agent': '302 Party (Sticker94 / Discord: doaight)',  # Add a user-agent header to match what Postman sends
        'Content-Type': 'application/json'  # Include Content-Type if required
    }
    url = f'https://www.ge-tracker.com{api_endpoint}'

    try:
        # Make GET request to the API with optional input params
        response = requests.get(url, headers=headers, params=input_params)

        # Check if request was successful
        response.raise_for_status()

        # Return the JSON data
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return None

@app.route('/api/item_price/<string:item_name>', methods=['GET'])
def get_item_price(item_name):
    """Fetch the latest price for any item based on the item name."""

    # Fetch the item data using the item name
    item_data = get_api_data(f'/api/items/search/{item_name}')

    if item_data is None or 'data' not in item_data:
        return jsonify({"error": f"Failed to fetch data for item: {item_name}"}), 500

    # Extract relevant data from the fetched item info
    item_price = item_data['data'][0]['buying'] if item_data and 'data' in item_data else 0

    return jsonify({
        "item": item_name,
        "price": item_price,
        "url": item_data['data'][0]['url']  # Provide the URL if needed
    })


# Routes for crafting and smithing

@app.route('/api/crafting_smithing/tan_leather', methods=['GET'])
def get_tan_leather():
    """Fetch tan leather data from the external API"""
    data = get_api_data('/api/tan-leather')

    if data:
        return jsonify(data)
    else:
        return jsonify({"error": "Unable to fetch Tan Leather data"}), 500
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def send_discord_webhook(message):
    data = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code != 204:
        print(f"Failed to send webhook: {response.status_code} - {response.text}")

def get_group_data(group_id):
    response = requests.get(f"https://api.wiseoldman.net/v2/groups/{group_id}")
    if response.status_code == 200:
        return response.json()
    return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001, debug=True)
