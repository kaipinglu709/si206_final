import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')

def setup_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS playlist_tracks (
        playlist_name TEXT,
        track_name TEXT,
        artist TEXT
    );
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS insert_tracker (
        id INTEGER PRIMARY KEY,
        last_inserted_index INTEGER DEFAULT 0
    );
    ''')
    # Ensure there is a row to track the position
    cursor.execute('INSERT OR IGNORE INTO insert_tracker (id, last_inserted_index) VALUES (1, 0);')
    
    conn.commit()
    cursor.close()
    conn.close()

def execute_join_and_store_results():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Retrieve the last inserted index
    cursor.execute('SELECT last_inserted_index FROM insert_tracker WHERE id = 1;')
    last_index = cursor.fetchone()[0]

    query = '''
    SELECT 
        playlists.name AS playlist_name, 
        tracks.name AS track_name, 
        tracks.artist
    FROM 
        playlists
    JOIN 
        tracks ON playlists.id = tracks.playlist_id
    '''
    cursor.execute(query)
    join_results = cursor.fetchall()

    start_index = last_index
    end_index = start_index + 25
    batch = join_results[start_index:end_index]

    cursor.executemany('''
    INSERT INTO playlist_tracks (playlist_name, track_name, artist)
    VALUES (?, ?, ?)
    ''', batch)
    conn.commit()

    # Update the last inserted index in insert_tracker
    new_last_index = min(end_index, len(join_results))
    cursor.execute('UPDATE insert_tracker SET last_inserted_index = ? WHERE id = 1;', (new_last_index,))

    conn.commit()
    cursor.close()
    conn.close()

    print(f"Inserted {len(batch)} rows into the new table 'playlist_tracks'. Last inserted index is now {new_last_index}.")

if __name__ == '__main__':
    setup_database()
    execute_join_and_store_results()
