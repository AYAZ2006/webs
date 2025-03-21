from nicegui import ui
import sqlite3
import os

# ✅ Get PORT dynamically (Render uses this env variable)
PORT = int(os.getenv("PORT", 8080))

# ✅ Database Setup
DB_PATH = "chat.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                    sender TEXT, receiver TEXT, avatar TEXT, text TEXT)''')
conn.commit()

messages = []  # Holds messages in memory

def load_messages():
    """Load messages from the database at startup"""
    global messages
    cursor.execute("SELECT sender, receiver, avatar, text FROM messages")
    messages = cursor.fetchall()

load_messages()  # Load messages when the app starts

# ✅ Chat UI Column (Declared Globally)
chat_column = ui.column()

@ui.refreshable
def chat_messages(own_id, receiver_id):
    """Show only messages between the two users"""
    chat_column.clear()  # ✅ Ensure old messages are removed
    with chat_column:
        for sender, receiver, avatar, text in messages:
            if (sender == own_id and receiver == receiver_id) or (sender == receiver_id and receiver == own_id):
                ui.chat_message(avatar=avatar, text=text, sent=sender == own_id)

@ui.page('/')
def index():
    user = ""  # ✅ Define user inside function scope
    receiver = ""
    avatar = ""

    def start_chat():
        """Save username and receiver, then show chat UI"""
        nonlocal user, receiver, avatar  # ✅ Use `nonlocal` to update outer function variables
        user = username.value.strip()
        receiver = receiver_name.value.strip()

        if not user or not receiver:
            ui.notify("Enter both usernames!", color="red")
            return

        avatar = f'https://robohash.org/{user}?bgset=bg2'  # Fixed user avatar
        chat_messages.refresh(user, receiver)  # ✅ Refresh chat for the two users

    def send():
        """Send message and store in database"""
        if text.value.strip():
            messages.append((user, receiver, avatar, text.value))
            cursor.execute("INSERT INTO messages (sender, receiver, avatar, text) VALUES (?, ?, ?, ?)", 
                           (user, receiver, avatar, text.value))
            conn.commit()
            text.value = ''  # Clear input
            chat_messages.refresh(user, receiver)  # ✅ Refresh messages after sending

    # Input fields for usernames
    ui.label("Enter your Username:")
    username = ui.input(placeholder="Your username")

    ui.label("Chat with (Receiver):")
    receiver_name = ui.input(placeholder="Receiver's username")

    ui.button("Start Chat", on_click=start_chat)  # ✅ Corrected on_click

    # ✅ Chat area (Global `chat_column` is used)
    with chat_column:
        ui.label("Chat messages will appear here.")

    with ui.footer().classes('bg-white p-2'):
        text = ui.input(placeholder='Type a message...') \
            .props('rounded outlined') \
            .on('keydown.enter', send)

# ✅ Render Fix: Allow Multiprocessing
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(host="0.0.0.0", port=PORT, title="Chat App", dark=True)
