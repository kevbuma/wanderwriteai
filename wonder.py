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

# Theme setting
if "theme" not in st.session_state:
    st.session_state.theme = "light"

if st.session_state.theme == "dark":
    background = "#1E1E1E"
    foreground = "#FFFFFF"
    button_bg = "#004aad"
else:
    background = "#e8f0fe"
    foreground = "#003366"
    button_bg = "#004aad"

# Custom CSS
st.markdown(f"""
<style>
    body {{
        background-color: {background};
        color: {foreground};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    .stButton>button {{
        background-color: {button_bg};
        color: white;
        border-radius: 5px;
        height: 40px;
        width: 100%;
        font-size: 16px;
        font-weight: bold;
    }}
    .stTextInput>div>input, .stTextArea>div>textarea {{
        border: 2px solid {button_bg};
        border-radius: 5px;
        padding: 10px;
        font-size: 14px;
        color: {foreground};
        background-color: white;
    }}
    h1, h2, h3 {{
        color: {foreground};
    }}
</style>
""", unsafe_allow_html=True)

# ----------- Simple user authentication -----------
if "users" not in st.session_state:
    st.session_state.users = {}
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "profile_pic" not in st.session_state:
    st.session_state.profile_pic = None
if "book" not in st.session_state:
    st.session_state.book = []

# Hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Registration and Login UI
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
                st.session_state.users[username] = {
                    "password": hash_password(password),
                    "profile_pic": None
                }
                st.success("Registration successful. Please log in.")
                st.rerun()
    else:
        if st.button("Login"):
            user = st.session_state.users.get(username)
            if user and user["password"] == hash_password(password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.profile_pic = user["profile_pic"]
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password.")

# Login gate
if not st.session_state.authenticated:
    login_ui()
    st.stop()

# ----------- Sidebar navigation -----------
st.sidebar.title(f"👋 Hello, {st.session_state.username}")
if st.session_state.profile_pic:
    st.sidebar.image(st.session_state.profile_pic, width=100)

page = st.sidebar.radio("Navigation", ["Home", "Generate Guide", "Surprise Me", "My Book", "User Settings", "Logout"])

if page == "Logout":
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.rerun()

# ----------- Home Page -----------
if page == "Home":
    st.title("🏝️ WanderWrite AI")
    st.write("Welcome to WanderWrite AI, your intelligent travel storytelling assistant.")
    st.subheader("📘 Sample Travel Guide Template")
    st.markdown("""
### Example: Tokyo Travel Guide

#### Welcome to Tokyo
Experience the bustling energy of Japan's capital with this immersive travel plan.

#### Top Attractions
- Shibuya Crossing
- Tokyo Tower
- Asakusa Temple

#### Local Foods
- Sushi
- Ramen
- Okonomiyaki

#### Hidden Gems
- Yanaka District
- Oedo Antique Market

#### Final Tips
Stay safe, learn basic Japanese phrases, and don’t miss out on the vending machines!
""")

# ----------- Generate Guide Page -----------
if page == "Generate Guide":
    st.header("✈️ Generate a City Travel Guide")
    city = st.text_input("Enter a City")
    city_summary = st.text_area("Optional: Write a short city summary")
    if st.button("Generate Guide") and city:
        with st.spinner("Generating guide..."):
            prompt = f"Write an adventure-style travel guide for the city: {city}. Include local highlights, food, hidden gems, and cultural experiences."
            if city_summary:
                prompt += f"\n\nCity Summary: {city_summary}"
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a travel guide author."},
                        {"role": "user", "content": prompt}
                    ]
                )
                guide = response.choices[0].message.content
                st.text_area("Your Travel Guide", guide, height=300)

                if st.button("Add to Book"):
                    st.session_state.book.append({"city": city, "guide": guide})
                    st.success("Guide added to your book.")
            except Exception as e:
                st.error(f"Something went wrong: {e}")

# ----------- Surprise Me Page -----------
if page == "Surprise Me":
    st.header("🎲 Surprise Me with a Random City Guide")
    random_city = random.choice(["Barcelona", "Tokyo", "Istanbul", "Nairobi", "Buenos Aires", "Lisbon", "Oslo"])
    st.write(f"Randomly selected city: **{random_city}**")
    if st.button("Generate Surprise Guide"):
        with st.spinner("Generating guide..."):
            prompt = f"Write a fun, adventure-themed travel guide for the city: {random_city}. Include local highlights, food, hidden gems, and unique cultural experiences."
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a travel guide author."},
                        {"role": "user", "content": prompt}
                    ]
                )
                guide = response.choices[0].message.content
                st.text_area("Your Surprise Travel Guide", guide, height=300)

                if st.button("Add to Book"):
                    st.session_state.book.append({"city": random_city, "guide": guide})
                    st.success("Guide added to your book.")
            except Exception as e:
                st.error(f"Something went wrong: {e}")

# ----------- My Book Page -----------
if page == "My Book":
    st.header("📘 My Book")
    if not st.session_state.book:
        st.info("No guides added yet.")
    else:
        for entry in st.session_state.book:
            st.subheader(entry["city"])
            st.write(entry["guide"])

        export_format = st.selectbox("Choose Export Format", ["PDF", "TXT"])
        if st.button("Download My Book"):
            if export_format == "PDF":
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                for entry in st.session_state.book:
                    pdf.multi_cell(0, 10, f"{entry['city']}\n{entry['guide']}\n\n")
                pdf_output = io.BytesIO()
                pdf.output(pdf_output)
                st.download_button("Download PDF", data=pdf_output.getvalue(), file_name="my_book.pdf", mime="application/pdf")
            else:
                txt_output = ""
                for entry in st.session_state.book:
                    txt_output += f"{entry['city']}\n{entry['guide']}\n\n"
                st.download_button("Download TXT", data=txt_output.encode("utf-8"), file_name="my_book.txt", mime="text/plain")

# ----------- User Settings Page -----------
if page == "User Settings":
    st.header("⚙️ User Settings")

    uploaded_pic = st.file_uploader("Upload Profile Picture", type=["jpg", "png"])
    if uploaded_pic:
        st.session_state.profile_pic = uploaded_pic
        st.session_state.users[st.session_state.username]["profile_pic"] = uploaded_pic
        st.success("Profile picture updated.")

    new_username = st.text_input("Change Username", value=st.session_state.username)
    if st.button("Update Username") and new_username != st.session_state.username:
        if new_username in st.session_state.users:
            st.warning("Username already taken.")
        else:
            st.session_state.users[new_username] = st.session_state.users.pop(st.session_state.username)
            st.session_state.username = new_username
            st.success("Username updated.")
            st.rerun()

    new_password = st.text_input("Change Password", type="password")
    if st.button("Update Password") and new_password:
        st.session_state.users[st.session_state.username]["password"] = hash_password(new_password)
        st.success("Password updated.")

    theme_option = st.radio("Theme Mode", ["light", "dark"], index=0 if st.session_state.theme == "light" else 1)
    if theme_option != st.session_state.theme:
        st.session_state.theme = theme_option
        st.success("Theme updated. Refreshing...")
        st.rerun()
