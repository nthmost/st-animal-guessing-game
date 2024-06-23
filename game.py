import streamlit as st
import json
import os

# Load animals.json if it exists
if os.path.exists('animals.json'):
    with open('animals.json', 'r') as file:
        animal_data = json.load(file)
else:
    animal_data = {
        "question": "Does the animal live on land?",
        "yes": {
            "question": "Is the animal big?",
            "yes": {"animal": "elephant"},
            "no": {"animal": "dog"}
        },
        "no": {
            "question": "Does the animal have scales?",
            "yes": {"animal": "shark"},
            "no": {"animal": "whale"}
        }
    }

def ask_question(node):
    if 'animal' in node:
        return f"Is it a {node['animal']}?", node['animal']
    return node['question'], None

def update_tree(node, path, new_question, new_animal, last_guess):
    if len(path) == 1:
        branch = node[path[0]]
    else:
        branch = node
        for p in path[:-1]:
            branch = branch[p]
        branch = branch[path[-1]]

    new_branch = {
        "question": new_question,
        "yes": {"animal": new_animal},
        "no": branch
    }
    if path[-1] == 'yes':
        node[path[0]]['yes'] = new_branch
    else:
        node[path[0]]['no'] = new_branch

def save_data(data):
    with open('animals.json', 'w') as file:
        json.dump(data, file)

st.title("Animal Guessing Game")

if 'path' not in st.session_state:
    st.session_state.path = []
if 'new_animal' not in st.session_state:
    st.session_state.new_animal = ""
if 'new_question' not in st.session_state:
    st.session_state.new_question = ""

current_node = animal_data
for p in st.session_state.path:
    current_node = current_node[p]

question, guessed_animal = ask_question(current_node)

st.write(question)

if guessed_animal:
    if st.button('Yes'):
        st.write(f"Yay! I guessed it right! It is a {guessed_animal}.")
        st.session_state.path = []
    if st.button('No'):
        st.session_state.new_animal = st.text_input("I give up. What is the animal you were thinking of?", key="new_animal")
        st.session_state.new_question = st.text_input(f"Please give me a yes/no question to distinguish a {guessed_animal} from a {st.session_state.new_animal}.", key="new_question")
        if st.button('Submit'):
            update_tree(animal_data, st.session_state.path, st.session_state.new_question, st.session_state.new_animal, guessed_animal)
            save_data(animal_data)
            st.session_state.path = []
else:
    if st.button('Yes'):
        st.session_state.path.append('yes')
    if st.button('No'):
        st.session_state.path.append('no')

