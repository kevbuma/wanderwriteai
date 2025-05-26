import streamlit as st
import openai

# Set your OpenAI key here
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="WanderWrite AI", layout="centered")

st.title("📘 WanderWrite AI")
st.subheader("Turn real cities into adventure-style travel guides!")

city = st.text_input("Enter a city name")
facts = st.text_area("What do you know about this city? (Paste info from RandomCity.net, Wikipedia, etc.)")

if st.button("✍️ Generate Travel Guide"):
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
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )
        guide = response.choices[0].message.content
        st.markdown("### ✨ Your Travel Guide")
        st.write(guide)
