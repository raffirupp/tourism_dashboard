import streamlit as st
import pandas as pd

import hashlib

PASSWORD = "KantarVacation"

def check_password():
    def password_entered():
        if st.session_state["password"] == PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("🔒 Please enter a password:", type="password", on_change=password_entered, key="password")
        st.stop()
    elif not st.session_state["password_correct"]:
        st.text_input("🔒 Please enter a password:", type="password", on_change=password_entered, key="password")
        st.error("😕 Wrong password")
        st.stop()

check_password()  


def local_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# CSS aktivieren
local_css("styles.css")


menu_options = {
    "0. Introduction": "📘 Introduction",
    "1. Socio-demographics & distribution": "👥 Socio-demographics",
    "2. Attitudes towards vacations": "🧠 Vacation Attitudes",
    "2a. Differences and Similarities": "📊 Differences and Similarities",  # 👈 NEU
    "3. Last Vacation": "🏖️ Last Vacation",
    "4. Descriptions and Rating": "🗣️ Vacation Descriptions",
    "5. To be added": "🔧 Coming Soon"
}

menu = st.sidebar.radio(
    label="",
    options=list(menu_options.keys()),
    format_func=lambda x: menu_options[x]
)

st.sidebar.markdown("---")
st.sidebar.markdown("ℹ️ *Tourism Survey 2025 Dashboard*")

# Force reload button
if "reload_data" not in st.session_state:
    st.session_state.reload_data = False

if st.sidebar.button("🔄 Force Reload"):
    st.session_state.reload_data = True

# Load Excel data (used for sociodemographics and possibly others)
@st.cache_data(show_spinner=True)
def load_data():
    return pd.read_excel("data/DATA_TourismCommunity2025_Countries.xlsx", sheet_name=None, header=None)

if st.session_state.reload_data:
    st.cache_data.clear()
    st.session_state.reload_data = False

# Lade relevante Sheets (optional nutzbar in anderen Sektionen)
sheets = load_data()
raw_df = sheets["Percentages"]
sociodemo_df = sheets["Sociodemographics"]
first_part_df = sheets["First Part"]

# Import core sections
from sections import sociodemographics, attitudes, Last_Holiday, descriptions_rating, differences

# Seiten-Routing
if menu.startswith("0."):
    from sections import introduction
    introduction.run()

elif menu.startswith("1."):
    sociodemographics.render(sociodemo_df)

elif menu.startswith("2."):
    attitudes.render(None)

elif menu.startswith("2a."):
    differences.render()

elif menu.startswith("3."):
    Last_Holiday.render()

elif menu.startswith("4."):
    descriptions_rating.render()  # ✅ NEU eingebunden

else:
    st.title("Coming soon...")
    st.markdown("This section will be added in a future release.")
