import requests
import sqlite3
import os
import matplotlib.pyplot as plt

# Configuration
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
API_URL = "https://api.openbrewerydb.org/v1/breweries"

def setup_database():
    """ Set up the SQLite database and create the breweries_extra_credit table """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS breweries_extra_credit(
            id TEXT PRIMARY KEY,
            name TEXT,
            brewery_type TEXT,
            street TEXT,
            city TEXT,
            state TEXT,
            postal_code TEXT,
            country TEXT,
            longitude TEXT,
            latitude TEXT,
            phone TEXT,
            website_url TEXT
        );
    ''')
    conn.commit()
    conn.close()

def fetch_breweries():
    """ Fetch a list of breweries from the Open Brewery DB API """
    params = {'per_page': 200}  # Fetch 200 breweries
    response = requests.get(API_URL, params=params)
    return response.json() if response.status_code == 200 else []

def insert_breweries(breweries):
    """ Insert brewery data into the SQLite database """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for brewery in breweries:
        c.execute('''
            INSERT OR IGNORE INTO breweries_extra_credit (id, name, brewery_type, street, city, state, postal_code, 
                                            country, longitude, latitude, phone, website_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', (brewery['id'], brewery['name'], brewery['brewery_type'], brewery['street'], brewery['city'],
             brewery['state'], brewery['postal_code'], brewery['country'], brewery['longitude'],
             brewery['latitude'], brewery['phone'], brewery['website_url']))
    conn.commit()
    conn.close()

def calculate_brewery_statistics():
    """ Perform a simple calculation on the brewery data """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT state, COUNT(*) FROM breweries_extra_credit GROUP BY state')
    results = c.fetchall()
    conn.close()
    return results

def visualize_data(statistics):
    """ Visualize the number of breweries per state using a bar chart """
    states = [state for state, count in statistics]
    counts = [count for state, count in statistics]

    plt.figure(figsize=(10, 8))
    plt.bar(states, counts, color='g')
    plt.xlabel('State')
    plt.ylabel('Number of Breweries')
    plt.title('Number of Breweries Per State (200 Breweries from Open Brewery DB)')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()

def write_statistics_to_file(statistics):
    """ Write the calculated statistics to a text file """
    with open("brewery_statistics_extra_credit.txt", "w") as file:
        for state, count in statistics:
            file.write(f"State: {state}, Number of Breweries: {count}\n")

if __name__ == '__main__':
    setup_database()
    breweries = fetch_breweries()
    if breweries:
        insert_breweries(breweries)
        statistics = calculate_brewery_statistics()
        write_statistics_to_file(statistics)
        visualize_data(statistics)
        print("Brewery data fetched, stored, processed, and visualized successfully.")
    else:
        print("Failed to fetch data from the API.")
