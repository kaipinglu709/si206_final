import sqlite3
import matplotlib.pyplot as plt
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
POPULATION_DATA = {
    'AL': 5024279, 'AK': 733391, 'AZ': 7151502, 'AR': 3011524, 'CA': 39538223, 
    'CO': 5773714, 'CT': 3605944, 'DE': 989948, 'FL': 21538187, 'GA': 10711908, 
    'HI': 1455271, 'ID': 1839106, 'IL': 12812508, 'IN': 6785528, 'IA': 3190369, 
    'KS': 2937880, 'KY': 4505836, 'LA': 4657757, 'ME': 1362359, 'MD': 6177224, 
    'MA': 7029917, 'MI': 10077331, 'MN': 5706494, 'MS': 2961279, 'MO': 6154913, 
    'MT': 1084225, 'NE': 1961504, 'NV': 3104614, 'NH': 1377529, 'NJ': 9288994, 
    'NM': 2117522, 'NY': 20201249, 'NC': 10439388, 'ND': 779094, 'OH': 11799448, 
    'OK': 3959353, 'OR': 4237256, 'PA': 13002700, 'RI': 1097379, 'SC': 5118425, 
    'SD': 886667, 'TN': 6910840, 'TX': 29145505, 'UT': 3271616, 'VT': 643077, 
    'VA': 8631393, 'WA': 7705281, 'WV': 1793716, 'WI': 5893718, 'WY': 576851
}

def count_stores_by_state():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT state, COUNT(*) FROM kroger_stores GROUP BY state')
    results = c.fetchall()
    store_per_capita = {}
    for state, count in results:
        if state in POPULATION_DATA:
            # Now using 100000 as the multiplier for per 100,000 people calculation
            store_per_capita[state] = (count / POPULATION_DATA[state]) * 100000
    conn.close()
    return store_per_capita

def visualize_data(data):
    states = list(data.keys())
    values = list(data.values())
    plt.figure(figsize=(12, 6))
    plt.bar(states, values, color='blue')
    plt.xlabel('State')
    plt.ylabel('Stores per 100,000 people')
    plt.title('Number of Kroger Stores per 100,000 People by State')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    calculated_data = count_stores_by_state()
    visualize_data(calculated_data)
