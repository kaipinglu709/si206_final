import requests
import sqlite3
import matplotlib.pyplot as plt
import os

# Configuration
CLIENT_ID = 'universityofmichiganstudentproject-afccb3ec49222b05056ff11d00c2f2e71219697512280846431'  # Replace with your actual client ID
CLIENT_SECRET = 'aMwGIH9BK9HxO4ujxC0FdNzoLc80hvWdtfjfDQwk'  # Ensure this is securely handled
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kroger_project_database.db')

# Get OAuth2 token
def get_kroger_token():
    token_url = "https://api.kroger.com/v1/connect/oauth2/token"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
        # Removed 'scope': 'product.compact' if not required
    }
    response = requests.post(token_url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print("Failed to fetch token:", response.json())
        return None


# Kroger API interaction
def get_kroger_data():
    token = get_kroger_token()
    if not token:
        return []
    
    headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}
    location_url = 'https://api.kroger.com/v1/locations?filter.chain=Kroger'
    response = requests.get(location_url, headers=headers)
    if response.status_code == 200:
        return response.json()['data']
    else:
        print("Failed to fetch data:", response.status_code, response.json())
        return []

# Database management
def setup_database():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS kroger_stores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    store_id TEXT,
                    store_name TEXT,
                    state TEXT
                )
            ''')
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")


def insert_kroger_data(stores):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        for store in stores:
            c.execute('''
                INSERT INTO kroger_stores (store_id, store_name, state) 
                VALUES (?, ?, ?)
            ''', (store['locationId'], store['name'], store['address']['state']))
        conn.commit()

# Data processing
def count_stores_by_state():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT state, COUNT(*) FROM kroger_stores GROUP BY state')
        results = c.fetchall()
        return dict(results)

# Visualization
def visualize_data(data):
    states = list(data.keys())
    counts = list(data.values())

    plt.figure(figsize=(12, 6))
    plt.bar(states, counts, color='green')
    plt.xlabel('State')
    plt.ylabel('Number of Stores')
    plt.title('Number of Kroger Stores by State')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()

# Main execution logic
if __name__ == '__main__':
    setup_database()
    kroger_data = get_kroger_data()
    if kroger_data:  # Check if data is not empty
        insert_kroger_data(kroger_data)
        store_counts = count_stores_by_state()
        visualize_data(store_counts)
    else:
        print("No data retrieved from API")
