import streamlit as st
import io
from fpdf import FPDF
import random
from openai import OpenAI
import hashlib

# ----------- Setup OpenAI client -----------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ----------- Page config -----------
st.set_page_config(page_title="WanderWrite AI", page_icon="📘", layout="centered")

# ----------- Custom CSS including floating menu and buttons -----------
st.markdown("""
<style>
    body {
        background-color: var(--bg-color);
        color: var(--text-color);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stButton>button {
        background: linear-gradient(90deg, #004aad, #002c75);
        color: white;
        border-radius: 5px;
        height: 40px;
        width: 100%;
        font-size: 16px;
        font-weight: bold;
        margin: 5px 0;
    }
    .stTextInput>div>input, .stTextArea>div>textarea {
        border: 2px solid #004aad;
        border-radius: 5px;
        padding: 10px;
        font-size: 14px;
        color: var(--text-color);
        background-color: var(--input-bg);
    }
    h1, h2, h3 {
        color: #002244;
    }
    /* Floating menu container */
    #floating-menu {
        position: fixed;
        top: 100px;
        right: 20px;
        width: 180px;
        background: #003366;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 0 10px #00000080;
        z-index: 1000;
    }
    #floating-menu button {
        margin: 8px 0;
        background: linear-gradient(90deg, #004aad, #002c75);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px;
        font-size: 15px;
        width: 100%;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# ----------- Theme Variables -----------
if "theme" not in st.session_state:
    st.session_state.theme = "light"

def set_theme():
    if st.session_state.theme == "light":
        st.markdown("""
            <style>
                :root {
                    --bg-color: #e8f0fe;
                    --text-color: #003366;
                    --input-bg: white;
                }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
                :root {
                    --bg-color: #121212;
                    --text-color: #e0e0e0;
                    --input-bg: #333333;
                }
            </style>
        """, unsafe_allow_html=True)

set_theme()

# ----------- Simple user authentication -----------
if "users" not in st.session_state:
    st.session_state.users = {}
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_ui():
    st.title("🔐 Welcome to WanderWrite AI")
    option = st.radio("Select an option", ["Login", "Register"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if option == "Register":
        if st.button("Register"):
            if username in st.session_state.users:
                st.warning("Username already exists.")
            else:
                st.session_state.users[username] = hash_password(password)
                st.success("Registration successful. Please log in.")
                st.rerun()  # Preferred for latest versions

    else:
        if st.button("Login"):
            if username in st.session_state.users and st.session_state.users[username] == hash_password(password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("Login successful!")
                st.rerun()  # Preferred for latest versions

            else:
                st.error("Invalid username or password.")

# ----------- Login gate -----------
if not st.session_state.authenticated:
    login_ui()
    st.stop()

# ----------- Initialize session state -----------
if "book_guides" not in st.session_state:
    st.session_state.book_guides = []
if "city" not in st.session_state:
    st.session_state.city = ""
if "facts" not in st.session_state:
    st.session_state.facts = ""

# ----------- Random cities -----------
random_cities = [
    {"city": "Salta", "facts": "Located in northwestern Argentina, known for colonial architecture and scenic mountains."},
    {"city": "Luang Prabang", "facts": "UNESCO World Heritage site in Laos with Buddhist temples and French colonial buildings."},
    {"city": "Matera", "facts": "Ancient cave city in southern Italy, famous for stone houses called 'Sassi'."},
    {"city": "Ouarzazate", "facts": "Known as the 'door to the desert' in Morocco, and filming location for many movies."},
    {"city": "Bergen", "facts": "A coastal city in Norway known for fjords, colorful wooden houses, and rainy weather."}
]

# ----------- Page Management -----------
def logout():
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.rerun()  # Preferred for latest versions

def home_page():
    st.title("📘 WanderWrite AI")
    st.write("Turn real cities into vivid adventure-style travel guides!")

def generate_guide_page():
    city_input = st.text_input("Enter a city name", value=st.session_state.city)
    facts_input = st.text_area("Paste some facts about this city", value=st.session_state.facts)

    if st.button("🎲 Surprise Me with a City"):
        selection = random.choice(random_cities)
        st.session_state.city = selection["city"]
        st.session_state.facts = selection["facts"]
        st.rerun()  # Preferred for latest versions

    if city_input != st.session_state.city:
        st.session_state.city = city_input
    if facts_input != st.session_state.facts:
        st.session_state.facts = facts_input

    city = st.session_state.city
    facts = st.session_state.facts

    if st.button("✍️ Generate Travel Guide"):
        if not city.strip() or not facts.strip():
            st.warning("Please enter a city and some facts first.")
        else:
            with st.spinner("Crafting your adventure..."):
                prompt = f"""
                Write a short adventure-style travel guide for the city of {city}.
                Include:
                - A creative intro
                - 3 highlights to explore
                - A cultural fun fact
                - Travel tips (best time, how to get there)
                Make it vivid and immersive.
                Facts: {facts}
                """
                try:
                    response = client.chat.completions.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.8
                    )
                    guide = response.choices[0].message.content

                    st.markdown("### ✨ Your Travel Guide")
                    st.write(guide)

                    if st.button("➕ Add this guide to my Book"):
                        st.session_state.book_guides.append({"city": city, "guide": guide})
                        st.success(f"Added '{city}' to your book!")

                    class PDF(FPDF):
                        def __init__(self):
                            super().__init__()
                            self.add_page()
                            self.set_auto_page_break(auto=True, margin=15)
                            self.set_font("Arial", size=12)

                        def add_text(self, text):
                            for line in text.split('\n'):
                                self.multi_cell(0, 10, line)

                    txt_file = io.BytesIO()
                    txt_file.write(guide.encode('utf-8'))
                    txt_file.seek(0)

                    pdf = PDF()
                    pdf.add_text(guide)
                    pdf_bytes = pdf.output(dest='S').encode('latin1', 'ignore')
                    pdf_file = io.BytesIO(pdf_bytes)

                    st.download_button("⬇️ Download as TXT", txt_file, file_name=f"{city}_guide.txt", mime="text/plain")
                    st.download_button("⬇️ Download as PDF", pdf_file, file_name=f"{city}_guide.pdf", mime="application/pdf")

                except Exception as e:
                    st.error(f"Something went wrong: {e}")

def my_book_page():
    st.header("📚 Your Travel Guide Book")
    if st.session_state.book_guides:
        st.write(f"You have {len(st.session_state.book_guides)} guides saved.")

        for i, entry in enumerate(st.session_state.book_guides):
            st.markdown(f"### {i+1}. {entry['city']}")
            st.write(entry['guide'][:300] + "...")

        if st.button("📥 Download Book as TXT"):
            book_text = ""
            for entry in st.session_state.book_guides:
                book_text += f"---\nCity: {entry['city']}\n\n{entry['guide']}\n\n"

            book_file = io.BytesIO()
            book_file.write(book_text.encode("utf-8"))
            book_file.seek(0)

            st.download_button("⬇️ Download TXT Book", book_file, file_name="WanderWrite_Book.txt", mime="text/plain")

        if st.button("📥 Download Book as PDF"):
            class PDF(FPDF):
                def __init__(self):
                    super().__init__()
                    self.set_auto_page_break(auto=True, margin=15)

                def add_text(self, text):
                    for line in text.split('\n'):
                        self.multi_cell(0, 10, line)

            pdf = PDF()
            for entry in st.session_state.book_guides:
                pdf.add_page()
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, f"City: {entry['city']}", ln=True)
                pdf.set_font("Arial", size=12)
                pdf.add_text(entry['guide'])

            pdf_bytes = pdf.output(dest='S').encode('latin1', 'ignore')
            pdf_file = io.BytesIO(pdf_bytes)

            st.download_button("⬇️ Download PDF Book", pdf_file, file_name="WanderWrite_Book.pdf", mime="application/pdf")
    else:
        st.info("Your book is empty. Generate and add some guides first!")

def user_settings_page():
    st.header("⚙️ User Settings")
    st.write(f"Username: **{st.session_state.username}**")

    st.write("Change Password:")
    current_password = st.text_input("Current Password", type="password")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm New Password", type="password")

    if st.button("Update Password"):
        if not current_password or not new_password or not confirm_password:
            st.warning("Please fill in all password fields.")
        elif hash_password(current_password) != st.session_state.users.get(st.session_state.username):
            st.error("Current password is incorrect.")
        elif new_password != confirm_password:
            st.error("New passwords do not match.")
        else:
            st.session_state.users[st.session_state.username] = hash_password(new_password)
            st.success("Password updated successfully!")

# ----------- Floating menu (right side) -----------

def floating_menu():
    st.markdown("""
    <div id="floating-menu">
        <button onclick="window.location.href='#home'">🏠 Home</button>
        <button onclick="window.location.href='#generate'">✍️ Generate Guide</button>
        <button onclick="window.location.href='#book'">📚 My Book</button>
        <button onclick="window.location.href='#settings'">⚙️ Settings</button>
        <button onclick="window.location.href='#logout'">🚪 Logout</button>
    </div>
    """, unsafe_allow_html=True)

# ----------- Main logic -----------

# Map the page selection to function calls
page_functions = {
    "Home": home_page,
    "Generate Guide": generate_guide_page,
    "My Book": my_book_page,
    "User Settings": user_settings_page,
    "Logout": logout
}

# Use a session_state key for current page
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# Sidebar or floating menu to select page
# We replace sidebar with floating menu buttons

# Since Streamlit cannot handle JS onclick properly for navigation,
# We will use normal buttons instead:

with st.sidebar:
    st.title(f"👋 Hello, {st.session_state.username}")
    if st.button("🏠 Home"):
        st.session_state.current_page = "Home"
    if st.button("✍️ Generate Guide"):
        st.session_state.current_page = "Generate Guide"
    if st.button("📚 My Book"):
        st.session_state.current_page = "My Book"
    if st.button("⚙️ User Settings"):
        st.session_state.current_page = "User Settings"
    if st.button("🚪 Logout"):
        logout()

# Render the page
page_functions[st.session_state.current_page]()

# Theme toggle in the footer
st.markdown("---")
theme_toggle = st.checkbox("🌙 Dark Mode", value=(st.session_state.theme == "dark"))
if theme_toggle and st.session_state.theme != "dark":
    st.session_state.theme = "dark"
   st.rerun()  # Preferred for latest versions
elif not theme_toggle and st.session_state.theme != "light":
    st.session_state.theme = "light"
    sst.rerun()  # Preferred for latest versions
