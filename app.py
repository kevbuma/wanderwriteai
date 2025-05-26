import streamlit as st
from openai import OpenAI

# Initialize OpenAI client with secret key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Streamlit page settings
st.set_page_config(page_title="WanderWrite AI", layout="centered")

# App UI
st.title("📘 WanderWrite AI")
st.subheader("Turn real cities into adventure-style travel guides!")

# User input
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
                st.markdown("### ✨ Your Travel Guide")
                st.write(guide)
            except Exception as e:
                st.error(f"Something went wrong: {e}")
