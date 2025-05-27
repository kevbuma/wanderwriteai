import streamlit as st
from openai import OpenAI
import io
from fpdf import FPDF
import random

# Setup OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Page config and styling
st.set_page_config(page_title="WanderWrite AI", page_icon="📘", layout="centered")
st.markdown("""
<style>
    body {
        background-color: #e8f0fe;
        color: #003366;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stButton>button {
        background-color: #004aad;
        color: white;
        border-radius: 5px;
        height: 40px;
        width: 100%;
        font-size: 16px;
        font-weight: bold;
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
</style>
""", unsafe_allow_html=True)

# Logo display
logo_url = "https://i.imgur.com/yourlogo.png"  # Replace with your actual logo URL
st.image(logo_url, width=100)
st.title("📘 WanderWrite AI")
st.write("Turn real cities into vivid adventure-style travel guides!")

# Random cities for 'Surprise Me' button
random_cities = [
    {"city": "Salta", "facts": "Located in northwestern Argentina, known for colonial architecture and scenic mountains."},
    {"city": "Luang Prabang", "facts": "UNESCO World Heritage site in Laos with Buddhist temples and French colonial buildings."},
    {"city": "Matera", "facts": "Ancient cave city in southern Italy, famous for stone houses called 'Sassi'."},
    {"city": "Ouarzazate", "facts": "Known as the 'door to the desert' in Morocco, and filming location for many movies."},
    {"city": "Bergen", "facts": "A coastal city in Norway known for fjords, colorful wooden houses, and rainy weather."}
]

# Session state initialization
if "book_guides" not in st.session_state:
    st.session_state.book_guides = []
if "city" not in st.session_state:
    st.session_state.city = ""
if "facts" not in st.session_state:
    st.session_state.facts = ""
if "latest_guide" not in st.session_state:
    st.session_state.latest_guide = None

# Input fields and Surprise Me button
city_input = st.text_input("Enter a city name", value=st.session_state.city, key="city_input")
facts_input = st.text_area("Paste some facts about this city", value=st.session_state.facts, key="facts_input")

if st.button("🎲 Surprise Me with a City"):
    selection = random.choice(random_cities)
    st.session_state.city = selection["city"]
    st.session_state.facts = selection["facts"]
    st.experimental_rerun()  # safe here because inside button

# Update session state when user types manually
if city_input != st.session_state.city:
    st.session_state.city = city_input
if facts_input != st.session_state.facts:
    st.session_state.facts = facts_input

city = st.session_state.city
facts = st.session_state.facts

# Generate guide button and logic
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
                st.session_state.latest_guide = {"city": city, "guide": guide}
            except Exception as e:
                st.error(f"Something went wrong: {e}")

# Show the latest guide if generated
if st.session_state.latest_guide:
    guide = st.session_state.latest_guide["guide"]
    city = st.session_state.latest_guide["city"]

    st.markdown("### ✨ Your Travel Guide")
    st.write(guide)

    # Add guide to book button (outside generate button block)
    if st.button("➕ Add this guide to my Book"):
        # Avoid duplicates
        if not any(entry["city"] == city for entry in st.session_state.book_guides):
            st.session_state.book_guides.append(st.session_state.latest_guide)
            st.success(f"Added '{city}' to your book!")
        else:
            st.info(f"'{city}' is already in your book.")

    # Prepare download files
    txt_file = io.BytesIO()
    txt_file.write(guide.encode('utf-8'))
    txt_file.seek(0)

    class PDF(FPDF):
        def __init__(self):
            super().__init__()
            self.add_page()
            self.set_auto_page_break(auto=True, margin=15)
            self.set_font("Arial", size=12)

        def add_text(self, text):
            for line in text.split('\n'):
                self.multi_cell(0, 10, line)

    pdf = PDF()
    pdf.add_text(guide)
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_file = io.BytesIO(pdf_bytes)

    # Download buttons
    st.download_button("⬇️ Download as TXT", txt_file, file_name=f"{city}_guide.txt", mime="text/plain")
    st.download_button("⬇️ Download as PDF", pdf_file, file_name=f"{city}_guide.pdf", mime="application/pdf")

# Book export section
if st.session_state.book_guides:
    st.markdown("---")
    st.header("📚 Your Travel Guide Book")
    st.write(f"You have {len(st.session_state.book_guides)} guides in your book.")

    for i, entry in enumerate(st.session_state.book_guides):
        st.markdown(f"### {i+1}. {entry['city']}")
        st.write(entry['guide'][:300] + "...")  # preview

    # Export book as TXT
    book_text = ""
    for entry in st.session_state.book_guides:
        book_text += f"---\nCity: {entry['city']}\n\n{entry['guide']}\n\n"

    book_file = io.BytesIO()
    book_file.write(book_text.encode("utf-8"))
    book_file.seek(0)

    st.download_button(
        label="📥 Download Book as TXT",
        data=book_file,
        file_name="WanderWrite_Book.txt",
        mime="text/plain"
    )

    # Export book as PDF
    pdf = PDF()
    for entry in st.session_state.book_guides:
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"City: {entry['city']}", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.add_text(entry['guide'])
        pdf.ln(10)

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_file = io.BytesIO(pdf_bytes)
    st.download_button(
        label="📥 Download Book as PDF",
        data=pdf_file,
        file_name="WanderWrite_Book.pdf",
        mime="application/pdf"
    )

# Save & Share Guide Text
st.markdown("---")
st.header("💾 Save & Share Your Guides")
if st.session_state.book_guides:
    all_guides_text = "\n\n---\n\n".join([f"City: {g['city']}\n\n{g['guide']}" for g in st.session_state.book_guides])
    st.text_area("Copy all your saved guides here to share or save:", all_guides_text, height=200)
else:
    st.info("Add some guides to your book to save and share them here.")
