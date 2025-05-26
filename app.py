import streamlit as st
from openai import OpenAI
import io
from fpdf import FPDF
import random

# Sample cities with sample facts (you can expand this later)
random_cities = [
    {"city": "Salta", "facts": "Located in northwestern Argentina, known for colonial architecture and scenic mountains."},
    {"city": "Luang Prabang", "facts": "UNESCO World Heritage site in Laos with Buddhist temples and French colonial buildings."},
    {"city": "Matera", "facts": "Ancient cave city in southern Italy, famous for stone houses called 'Sassi'."},
    {"city": "Ouarzazate", "facts": "Known as the 'door to the desert' in Morocco, and filming location for many movies."},
    {"city": "Bergen", "facts": "A coastal city in Norway known for fjords, colorful wooden houses, and rainy weather."}
]


# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Streamlit settings
st.set_page_config(page_title="WanderWrite AI", layout="centered")
st.title("📘 WanderWrite AI")
st.subheader("Turn real cities into adventure-style travel guides!")

# Input section
city = st.text_input("Enter a city name")
facts = st.text_area("Paste some facts about this city (from RandomCity.net, Wikipedia, etc.)")

# Generate button
if st.button("✍️ Generate Travel Guide"):
    if not city or not facts:
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

                # Display guide
                st.markdown("### ✨ Your Travel Guide")
                st.write(guide)

                # TXT download
                txt_file = io.BytesIO()
                txt_file.write(guide.encode('utf-8'))
                txt_file.seek(0)

                # PDF generation
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

            except Exception as e:
                st.error(f"Something went wrong: {e}")
