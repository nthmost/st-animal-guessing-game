import sqlite3
import os

def init_test_db():
    # Create a new database connection to a test database
    conn = sqlite3.connect('test_animal_game.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS questions (
                 id INTEGER PRIMARY KEY,
                 question_text TEXT NOT NULL,
                 parent_id INTEGER,
                 yes_child_id INTEGER,
                 no_child_id INTEGER,
                 FOREIGN KEY (parent_id) REFERENCES questions (id),
                 FOREIGN KEY (yes_child_id) REFERENCES questions (id),
                 FOREIGN KEY (no_child_id) REFERENCES questions (id)
              )''')
    c.execute('''CREATE TABLE IF NOT EXISTS animals (
                 id INTEGER PRIMARY KEY,
                 name TEXT NOT NULL,
                 question_id INTEGER,
                 is_yes_answer BOOLEAN,
                 FOREIGN KEY (question_id) REFERENCES questions (id)
              )''')
    conn.commit()
    conn.close()

def test_insert_and_retrieve():
    # Initialize the test database
    init_test_db()
    
    # Connect to the test database
    conn = sqlite3.connect('test_animal_game.db')
    c = conn.cursor()
    
    # Insert test data
    c.execute("INSERT INTO questions (question_text) VALUES ('Is it larger than a breadbox?')")
    question_id = c.lastrowid
    c.execute("INSERT INTO animals (name, question_id, is_yes_answer) VALUES (?, ?, ?)", ('elephant', question_id, True))
    conn.commit()

    # Test retrieving the question
    c.execute("SELECT question_text FROM questions WHERE id = ?", (question_id,))
    assert c.fetchone()[0] == 'Is it larger than a breadbox?', "Test Failed: Question text does not match"

    # Test retrieving the animal
    c.execute("SELECT name FROM animals WHERE question_id = ? AND is_yes_answer = ?", (question_id, True))
    assert c.fetchone()[0] == 'elephant', "Test Failed: Animal name does not match"

    # Cleanup and close the connection
    conn.close()
    os.remove('test_animal_game.db')
    print("All tests passed!")

if __name__ == "__main__":
    test_insert_and_retrieve()

