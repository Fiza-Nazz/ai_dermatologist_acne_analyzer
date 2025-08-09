# main.py
import os
import io
from dotenv import load_dotenv
import streamlit as st
from PIL import Image
import google.generativeai as genai
from datetime import datetime

# --- Load API Key ---
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("🚨 GEMINI_API_KEY not found! Please set it in your .env file.")
    st.stop()

genai.configure(api_key=API_KEY)

# --- Streamlit Page Config ---
st.set_page_config(page_title="💡 Acne AI Dermatologist", layout="wide")

# --- Title & Header ---
st.title("💡 Acne / Pimple AI Dermatologist")
st.markdown("**Upload a skin photo and get dermatologist-style advice instantly!** 🤖💬")
st.caption("_Not a replacement for an in-person consultation_ 🩺")

# Sidebar Info
with st.sidebar:
    st.header("ℹ About this App")
    st.write("""
    This AI Agent uses **Google Gemini Vision+Text** to analyze acne/pimple images and  
    provide **probable causes, care steps, food advice, and red flags**.  
    """)
    st.markdown("---")
    st.write("**Made with ❤️ by Fiza**")

# File Upload
uploaded = st.file_uploader("📤 Upload acne/pimple photo", type=["jpg", "jpeg", "png"])
age = st.text_input("🎯 Age (optional)")
skin_type = st.selectbox("🧴 Skin type", ["", "Oily", "Combination", "Dry", "Sensitive"])

# --- History Feature ---
if "history" not in st.session_state:
    st.session_state.history = []

if st.button("🔍 Analyze"):
    if not uploaded:
        st.warning("Please upload an image first.")
        st.stop()

    # Show Image
    image = Image.open(uploaded).convert("RGB")
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Convert to Bytes
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    image_bytes = buf.getvalue()

    # AI Prompt
    user_prompt = f"""
You are a friendly **board-certified dermatologist**. Analyze the provided acne/pimple image and respond in a clear,
structured and **engaging** way for the user.

Sections to include (use emoji for each heading):

1️⃣ **Probable Causes** — list top 3 likely reasons.  
2️⃣ **Severity** — classify as Mild / Moderate / Severe with a short reason.  
3️⃣ **Immediate Care (0-7 days)** — 5 safe daily steps + what to avoid.  
4️⃣ **2–6 Week Plan** — skincare + diet recommendations.  
5️⃣ **Foods to Eat & Avoid** — bullet list with ✅ & ❌.  
6️⃣ **Red Flags** — when to urgently see a dermatologist.  
7️⃣ **Confidence Level** — percentage & info that would improve accuracy.  
8️⃣ **Fun One-Line Summary** — make it uplifting and positive.

**Skin type:** {skin_type or 'unknown'}  
**Age:** {age or 'unknown'}  

⚠ Important: Do NOT prescribe prescription-only meds. Keep tone friendly & professional.
    """

    try:
        with st.spinner("🔬 Analyzing image with Gemini..."):
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content([
                {"mime_type": "image/jpeg", "data": image_bytes},
                user_prompt
            ])

        ai_text = response.text if hasattr(response, "text") else str(response)

        # Save to History
        st.session_state.history.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "age": age,
            "skin_type": skin_type,
            "response": ai_text
        })

        # --- Display Result in Tabs ---
        st.success("✅ Analysis Complete!")
        tabs = st.tabs(["📄 Full Report", "🗂 Summary", "📜 History"])

        with tabs[0]:
            st.markdown(ai_text)

        with tabs[1]:
            st.markdown("### Quick Summary")
            st.write("\n".join(ai_text.split("\n")[:8]))  # First few lines

        with tabs[2]:
            if st.session_state.history:
                for item in reversed(st.session_state.history):
                    st.markdown(f"**{item['time']}** — Age: {item['age']} | Skin Type: {item['skin_type']}")
                    st.markdown(item["response"])
                    st.markdown("---")
            else:
                st.write("No history yet.")

        # Download Report
        st.download_button("💾 Download Report", data=ai_text, file_name="acne_report.txt")

    except Exception as e:
        st.error(f"❌ Error: {e}")
