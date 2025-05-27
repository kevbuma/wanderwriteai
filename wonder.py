import streamlit as st
import io
from fpdf import FPDF
import random
from openai import OpenAI
import hashlib

# ----------- Setup OpenAI client -----------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ----------- Page config and styling -----------
st.set_page_config(page_title="WanderWrite AI", page_icon="📘", layout="centered")

# Custom CSS for gradient buttons and floating menu
st.markdown("""
<style>
    body {
        background-color: #e8f0fe;
        color: #003366;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stButton>button {
        background: linear-gradient(90deg, #003366 0%, #004aad 100%);
        color: white;
        border-radius: 5px;
        height: 40px;
        width: 100%;
        font-size: 16px;
        font-weight: bold;
        border: none;
    }
    .stTextInput>div>input, .stTextArea>div>textarea {
        border: 2px solid #004aad;
        border-radius: 5px;
        padding: 10px;
        font-size: 14px;
        color: #003366;
        background-color: white;
    }
    h1, h2, h3 {
        color: #002244;
    }
    /* Floating menu styles */
    .floating-menu {
        position: fixed;
        top: 100px;
        left: 20px;
        width: 180px;
        background: #004aad;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        z-index: 1000;
    }
    .floating-menu button {
        margin: 6px 0;
    }
</style>
""", unsafe_allow_html=True)

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
                st.rerun()
    else:
        if st.button("Login"):
            if username in st.session_state.users and st.session_state.users[username] == hash_password(password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("Login successful!")
                st.rerun()

            else:
                st.error("Invalid username or password.")

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
if "page" not in st.session_state:
    st.session_state.page = "Home"

# ----------- Floating menu with buttons -----------

def set_page(page_name):
    st.session_state.page = page_name

st.markdown('<div class="floating-menu">', unsafe_allow_html=True)
if st.button("🏠 Home"):
    set_page("Home")
if st.button("📝 Generate Guide"):
    set_page("Generate Guide")
if st.button("📚 My Book"):
    set_page("My Book")
if st.button("⚙️ Settings"):
    set_page("Settings")
if st.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.experimental_rerun()
st.markdown('</div>', unsafe_allow_html=True)

page = st.session_state.page

# ----------- Random cities -----------
random_cities = [
    {"city": "Salta", "facts": "Located in northwestern Argentina, known for colonial architecture and scenic mountains."},
    {"city": "Luang Prabang", "facts": "UNESCO World Heritage site in Laos with Buddhist temples and French colonial buildings."},
    {"city": "Matera", "facts": "Ancient cave city in southern Italy, famous for stone houses called 'Sassi'."},
    {"city": "Ouarzazate", "facts": "Known as the 'door to the desert' in Morocco, and filming location for many movies."},
    {"city": "Bergen", "facts": "A coastal city in Norway known for fjords, colorful wooden houses, and rainy weather."}
]

# ----------- Utility to clean text for PDF -----------
def clean_text(text):
    replacements = {
        '\u2018': "'",  # left single quote
        '\u2019': "'",  # right single quote
        '\u201c': '"',  # left double quote
        '\u201d': '"',  # right double quote
        '\u2013': '-',  # en dash
        '\u2014': '-',  # em dash
        '\u2026': '...', # ellipsis
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

# ----------- Pages -----------

if page == "Home":
    st.title("📘 WanderWrite AI")
    st.write("Turn real cities into vivid adventure-style travel guides!")

elif page == "Generate Guide":
    city_input = st.text_input("Enter a city name", value=st.session_state.city)
    facts_input = st.text_area("Paste some facts about this city", value=st.session_state.facts)

    if st.button("🎲 Surprise Me with a City"):
        selection = random.choice(random_cities)
        st.session_state.city = selection["city"]
        st.session_state.facts = selection["facts"]
        st.rerun()

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
                        # Save to session_state book_guides correctly
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

                    # Clean guide text before PDF
                    cleaned_guide = clean_text(guide)

                    txt_file = io.BytesIO()
                    txt_file.write(guide.encode('utf-8'))
                    txt_file.seek(0)

                    pdf = PDF()
                    pdf.add_text(cleaned_guide)
                    pdf_bytes = pdf.output(dest='S').encode('latin1', errors='replace')
                    pdf_file = io.BytesIO(pdf_bytes)

                    st.download_button("⬇️ Download as TXT", txt_file, file_name=f"{city}_guide.txt", mime="text/plain")
                    st.download_button("⬇️ Download as PDF", pdf_file, file_name=f"{city}_guide.pdf", mime="application/pdf")

                except Exception as e:
                    st.error(f"Something went wrong: {e}")

elif page == "My Book":
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
                cleaned_guide = clean_text(entry['guide'])
                pdf.add_text(cleaned_guide)

            pdf_bytes = pdf.output(dest='S').encode('latin1', errors='replace')
            pdf_file = io.BytesIO(pdf_bytes)

            st.download_button("⬇️ Download PDF Book", pdf_file, file_name="WanderWrite_Book.pdf", mime="application/pdf")
    else:
        st.info("Your book is empty. Generate and add some guides first!")

elif page == "Settings":
    st.title("⚙️ User Settings")
    st.write(f"Username: **{st.session_state.username}**")

    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.rerun()
