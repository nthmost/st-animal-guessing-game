import sqlite3

def init_db():
    conn = sqlite3.connect('animal_game.db')
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


def insert_animal(name, question_id, is_yes_answer):
    conn = sqlite3.connect('animal_game.db')
    c = conn.cursor()
    c.execute("INSERT INTO animals (name, question_id, is_yes_answer) VALUES (?, ?, ?)", (name, question_id, is_yes_answer))
    conn.commit()
    conn.close()


def insert_question(parent_id, question, yes_no):
    conn = sqlite3.connect('animal_game.db')
    c = conn.cursor()
    try:
        # Insert the new question into the database
        c.execute("INSERT INTO questions (question_text) VALUES (?)", (question,))
        new_question_id = c.lastrowid  # Retrieve the ID of the newly inserted question

        # Determine which child (yes or no) this new question will be for the parent question
        if yes_no == 'yes':
            update_column = 'yes_child_id'
        else:
            update_column = 'no_child_id'

        # Update the parent question to link to this new question based on the user's answer
        c.execute(f"UPDATE questions SET {update_column} = ? WHERE id = ?", (new_question_id, parent_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()
    
    return new_question_id


def ask_question(question):
    print(question)
    return input("Answer (y for yes, n for no, ? for not sure): ").strip().lower()

def get_root_question():
    conn = sqlite3.connect('animal_game.db')
    c = conn.cursor()
    c.execute("SELECT id, question_text FROM questions WHERE parent_id IS NULL")
    root = c.fetchone()
    conn.close()
    return root

def get_next_node(question_id, yes_no):
    conn = sqlite3.connect('animal_game.db')
    c = conn.cursor()
    column = 'yes_child_id' if yes_no == 'y' else 'no_child_id'
    c.execute(f"SELECT id, question_text FROM questions WHERE id = (SELECT {column} FROM questions WHERE id = ?)", (question_id,))
    next_node = c.fetchone()
    conn.close()
    return next_node

def fetch_possible_animals(question_id, yes_no):
    conn = sqlite3.connect('animal_game.db')
    c = conn.cursor()
    c.execute("SELECT name FROM animals WHERE question_id = ? AND is_yes_answer = ?", (question_id, 1 if yes_no == 'y' else 0))
    animals = c.fetchall()
    conn.close()
    return [animal[0] for animal in animals]

def main():
    init_db()
    print("Think of an animal, and I'll try to guess it!")
    root = get_root_question()
    current_question_id, question_text = root

    while True:
        answer = ask_question(question_text)
        if answer not in ("y", "n"):  # handle uncertain or incorrect responses
            print("Let's try a simpler question!")
            continue

        next_node = get_next_node(current_question_id, answer)
        if next_node:
            current_question_id, question_text = next_node
        else:
            possible_animals = fetch_possible_animals(current_question_id, answer)
            if possible_animals:
                print(f"Is your animal one of these? {', '.join(possible_animals)}")
                break
            else:
                new_animal = input("I'm out of guesses! What was your animal? ")
                new_question = input(f"Please provide a question that would identify a {new_animal} as opposed to the other animals: ")
                yes_no = ask_question(f"Would the answer to '{new_question}' for a {new_animal} be yes or no?")

                # Assuming the function to insert the new question returns the ID of the new question
                new_question_id = insert_question(current_question_id, new_question, yes_no)
                insert_animal(new_animal, new_question_id, yes_no == 'yes')

                print("Thank you for helping me learn!")
                break

if __name__ == "__main__":
    main()

