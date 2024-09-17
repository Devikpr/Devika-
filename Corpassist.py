import streamlit as st
import requests
from datetime import datetime, timedelta
import subprocess

# Constants for Jugalbandi API
JUGALBANDI_API_QUERY = 'https://api.jugalbandi.ai/query-with-langchain-gpt3-5'
uuid_number = "4377262c-74c9-11ef-bf22-42004e494300"  # Replace with your actual UUID

# Function to query the document using the Jugalbandi API
def query_document_with_langchain_gpt3_5(uuid_number, query_string):
    try:
        response = requests.get(
            JUGALBANDI_API_QUERY,
            params={
                'query_string': query_string,
                'uuid_number': uuid_number
            },
            headers={'accept': 'application/json'}
        )

        # Check for a successful response
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed with status code {response.status_code}"}

    except Exception as e:
        return {"error": str(e)}

# Format session label for display
def format_session_label(session_id):
    session_date = datetime.strptime(session_id, "%Y-%m-%d %H:%M:%S").date()
    if session_date == datetime.today().date():
        return "Today"
    elif session_date == (datetime.today().date() - timedelta(days=1)):
        return "Yesterday"
    else:
        return session_date.strftime("%B %d, %Y")

# Streamlit interface
st.title("Corp Assist")

# Initialize session management
if 'sessions' not in st.session_state:
    st.session_state.sessions = {}
if 'current_session' not in st.session_state:
    # Create a new session for the current chat
    new_session_id = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.current_session = new_session_id
    st.session_state.sessions[new_session_id] = {'chat_history': [], 'queries': []}

# Function to start a new chat session
def start_new_chat():
    new_session_id = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.current_session = new_session_id
    st.session_state.sessions[new_session_id] = {'chat_history': [], 'queries': []}

# Sidebar layout
with st.sidebar:
    # Go back to home button
    if st.button("⬅️ Go Back Home"):
        subprocess.Popen(["streamlit", "run", "Userinterfacefinal.py"])
        st.session_state.page = "Back"
    # Display "New Chat" button
    if st.button("New Chat"):
        start_new_chat()
    
    # Display available chat sessions in a list
    st.sidebar.title("Chat History")
    for session_id in reversed(list(st.session_state.sessions.keys())):
        label = format_session_label(session_id)
        if st.sidebar.button(label, key=session_id):
            st.session_state.current_session = session_id

# Retrieve the current session's chat history
current_session_id = st.session_state.current_session
chat_history = st.session_state.sessions[current_session_id]['chat_history']
stored_queries = st.session_state.sessions[current_session_id]['queries']

# Display stored queries in the sidebar
#st.sidebar.title("Stored Queries")
for query in stored_queries:
    if st.sidebar.button(query, key=f"query_{query}"):
        st.write(f"You selected: {query}")

# Chat input
user_input = st.chat_input("Enter your query:")

if user_input:
    # Add user's message to the current chat history
    chat_history.append({"role": "user", "content": user_input})

    # Store the query
    stored_queries.append(user_input)
    
    # Get the response from the API
    query_result = query_document_with_langchain_gpt3_5(uuid_number, user_input)
    
    # Add the chatbot's response to the chat history
    if "error" in query_result:
        chat_history.append({"role": "assistant", "content": f"Error: {query_result['error']}"})
    else:
        answer = query_result.get('answer', 'No answer found')
        chat_history.append({"role": "assistant", "content": answer})

    # Update the session state with the new chat history and queries
    st.session_state.sessions[current_session_id] = {
        'chat_history': chat_history,
        'queries': stored_queries
    }

# Display chat history using st.chat_message for a ChatGPT-style UI
for message in chat_history:
    if message['role'] == 'user':
        with st.chat_message("user"):
            st.write(message['content'])
    else:
        with st.chat_message("assistant"):
            st.write(message['content'])
