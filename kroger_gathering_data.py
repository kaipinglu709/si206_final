import requests
import sqlite3
import os

# Configuration
CLIENT_ID = 'universityofmichiganstudentproject-afccb3ec49222b05056ff11d00c2f2e71219697512280846431'
CLIENT_SECRET = 'aMwGIH9BK9HxO4ujxC0FdNzoLc80hvWdtfjfDQwk'
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')

def get_kroger_token():
    token_url = "https://api.kroger.com/v1/connect/oauth2/token"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    response = requests.post(token_url, headers=headers, data=data)
    return response.json()['access_token'] if response.status_code == 200 else None

def get_kroger_data():
    token = get_kroger_token()
    if token:
        headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}
        location_url = 'https://api.kroger.com/v1/locations?filter.chain=Kroger'
        response = requests.get(location_url, headers=headers)
        return response.json()['data'] if response.status_code == 200 else []
    else:
        return []

def setup_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS kroger_stores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store_id TEXT UNIQUE,
            store_name TEXT,
            state TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_kroger_data(stores):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for store in stores:
        # Check if the store already exists in the database
        c.execute("SELECT 1 FROM kroger_stores WHERE store_id = ?", (store['locationId'],))
        if c.fetchone() is None:
            c.execute('''
                INSERT INTO kroger_stores (store_id, store_name, state) VALUES (?, ?, ?)
            ''', (store['locationId'], store['name'], store['address']['state']))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    setup_database()
    kroger_data = get_kroger_data()
    if kroger_data:
        insert_kroger_data(kroger_data)
    else:
        print("No data retrieved from API")
