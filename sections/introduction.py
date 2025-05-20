import streamlit as st
from PIL import Image

def run():
    st.title("🗺️ Introduction: International Tourism Survey 2025")

    # Zwei nebeneinanderliegende Kacheln
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Sample size and segments")
        st.markdown("""
        **Total sample:** n = 11.511  
        **Countries:**  
        - 🇸🇬 Singapore: n = 1.501  
        - 🇬🇧 United Kingdom: n = 1.500  
        - 🇺🇸 United States: n = 1.501  
        - 🇨🇳 China: n = 1.002  
        - 🇰🇷 South Korea: n = 1.001  
        - 🇦🇪 United Arab Emirates: n = 1.003  
        - 🇧🇷 Brazil: n = 1.000  
        - 🇫🇷 France: n = 1.002  
        - 🇩🇪 Germany: n = 1.001  
        - 🇦🇺 Australia: n = 1.000
        """)

    with col2:
        st.markdown("### 🧪 Fieldwork & methodology")
        st.markdown("""
        **Fieldwork period:**  
        November 5, 2024 – January 31, 2025  

        **Statistical testing:**  
        - Z-test with confidence levels at **95%** and **90%**  
        - Indicated in raw data as:  
          - **Uppercase letters** = significant at 95% (p < 0.05)  
          - **Lowercase letters** = significant at 90% (p < 0.10)
        - Country comparison groups: All  

        **Base:**  
        Qualified respondents only (i.e. those who passed screener conditions)
        """)


    # Flowchart graphic
    st.subheader("🧭 Survey Logic Flowchart")

    image = Image.open("data/Flow_Chart_Tourism.png")  # <- Save the PNG there
    st.image(image, caption="This Flow Chart has been created with the help of Canva AI", use_container_width=True)


    # Detailed logic (optional)
    with st.expander("🔍 View detailed question logic (expert view)"):
        st.markdown("""
        ### 1. Screening and Consent  
        - **If China:** 3-step privacy consent required  
        - **If UAE:** language selection (English/Arabic)  
        - All others: proceed directly to screener  

        ### 2. Demographics  
        - `QGender`: Gender  
        - `QAge`: If under 18 → **Screened out**  
        
        ### 3. Attitude Quality Check  
        - `HD2`: Agreement with 8 vacation statements  
        - If respondent **strongly agrees/disagrees with both sides of ≥2 pairs** → **Quality flag**, but **continues**  

        ### 4. Vacation Eligibility  
        - `QWhen`: Timing of last leisure trip with overnight stay  
            - If **"Never"** → **Screened out**  
            - If **>12 months ago** → `QWhyno` (reason for no travel)  
            - If **≤12 months ago** → continue  

        ### 5. Vacation Details  
        - `QDuration` → auto-categorized into `hVacationType`  
        - `QWhere`: Travel destination  
            - If international or both:  
                - `QNumber`: Number of countries visited  
                - `QLocations`: Specify countries visited  
                - If 1–2 nights **and** 2–5 countries → flag (`hFlagDurDest`)  

        ### 6. Main Experience Variables  
        - `QAccom`: Accommodation type  
        - `QFeat`: Activities & features (multi-select)  
        - `QWhowith`: Travel companions (multi-select)  
        - `QReasons`: Travel motivation (multi-select)  

        ### 7. Perceptions & Evaluation  
        - `QDescribe_E`: Word tags (multi-select)  
        - `QDescribe_B`: Same words rated on a 3-point scale  
        - `QRate`: Overall rating (1–10 scale)
        """)

            # Contact Section
    st.markdown("---")  # Trennlinie

    st.subheader("📬 Contact")

    st.markdown("""
    If you have any questions about this dashboard,  
    feel free to reach out:

    👉 **Raffael Ruppert**  
    📧 [raffael.ruppert@sciencespo.fr](mailto:raffael.ruppert@sciencespo.fr)  
    """)

    st.caption("This dashboard was developed using Streamlit and Plotly. ChatGPT was used for Code improvement and debugging.")
