from nicegui import ui
import sqlite3
from uuid import uuid4

# Database Setup
conn = sqlite3.connect("chat.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                    sender TEXT, receiver TEXT, avatar TEXT, text TEXT)''')
conn.commit()

messages = []  # To hold messages in memory

def load_messages():
    """Load messages from the database at startup"""
    global messages
    cursor.execute("SELECT sender, avatar, text FROM messages")
    messages = cursor.fetchall()

load_messages()  # Load messages when the app starts

@ui.refreshable
def chat_messages(own_id, receiver_id):
    """Show only messages between the two users"""
    for user_id, avatar, text in messages:
        if user_id in [own_id, receiver_id]:  # Show messages related to the users
            ui.chat_message(avatar=avatar, text=text, sent=user_id == own_id)

@ui.page('/')
def index():
    def start_chat():
        """Save username and receiver, then show chat UI"""
        global user, receiver, avatar
        user = username.value.strip()
        receiver = receiver_name.value.strip()

        if not user or not receiver:
            ui.notify("Enter both usernames!", color="red")
            return
        
        avatar = f'https://robohash.org/{user}?bgset=bg2'  # User avatar
        chat_column.clear()  # Reset chat UI
        with chat_column:
            chat_messages(user, receiver)  # Show chat for the two users

    def send():
        """Send message and store in database"""
        if text.value.strip():
            messages.append((user, avatar, text.value))
            cursor.execute("INSERT INTO messages (sender, receiver, avatar, text) VALUES (?, ?, ?, ?)", 
                           (user, receiver, avatar, text.value))
            conn.commit()
            text.value = ''  # Clear input
            chat_messages.refresh()

    # Input fields for usernames
    ui.label("Enter your Username:")
    username = ui.input(placeholder="Your username")

    ui.label("Chat with (Receiver):")
    receiver_name = ui.input(placeholder="Receiver's username")

    ui.button("Start Chat", on_click=start_chat)

    # Chat area
    chat_column = ui.column()

    with ui.footer().classes('bg-white p-2'):
        text = ui.input(placeholder='Type a message...') \
            .props('rounded outlined') \
            .on('keydown.enter', send)

ui.run()
