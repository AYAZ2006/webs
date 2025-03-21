from nicegui import ui
import sqlite3
import os
from uuid import uuid4

# Database Setup (Ensure it works correctly in Render)
conn = sqlite3.connect("chat.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                    sender TEXT, receiver TEXT, avatar TEXT, text TEXT)''')
conn.commit()

# Function to Load Messages from DB
def load_messages(sender, receiver):
    """Load only messages between sender and receiver."""
    cursor.execute("SELECT sender, avatar, text FROM messages WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?)", 
                   (sender, receiver, receiver, sender))
    return cursor.fetchall()

@ui.refreshable
def chat_messages(own_id, receiver_id):
    """Show messages between the two users"""
    chat_window.clear()
    msgs = load_messages(own_id, receiver_id)
    for user_id, avatar, text in msgs:
        ui.chat_message(avatar=avatar, text=text, sent=user_id == own_id, parent=chat_window)

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
        
        avatar = f'https://robohash.org/{user}?bgset=bg2'  # Generate fixed avatar
        chat_messages.refresh(user, receiver)  # Refresh chat with stored messages

    def send():
        """Send message and store in database"""
        if text.value.strip():
            cursor.execute("INSERT INTO messages (sender, receiver, avatar, text) VALUES (?, ?, ?, ?)", 
                           (user, receiver, avatar, text.value))
            conn.commit()
            text.value = ''  # Clear input
            chat_messages.refresh(user, receiver)  # Refresh chat

    # User Inputs
    ui.label("Enter your Username:")
    username = ui.input(placeholder="Your username")

    ui.label("Chat with (Receiver):")
    receiver_name = ui.input(placeholder="Receiver's username")

    ui.button("Start Chat", on_click=start_chat)

    # Chat area
    global chat_window
    chat_window = ui.column()

    # Input for messages
    with ui.footer().classes('bg-white p-2'):
        text = ui.input(placeholder='Type a message...') \
            .props('rounded outlined') \
            .on('keydown.enter', send)

# Run NiceGUI with dynamic port (for Render)
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=int(os.getenv("PORT", 8080)), host="0.0.0.0")
