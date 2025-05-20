import streamlit as st
import pandas as pd
import plotly.express as px
from .utils import prepare_figure_for_export
import plotly.io as pio
pio.kaleido.scope.default_format = "png"

# Country Mapping
country_label_map = {
    "Total (A)": "All Countries",
    "SG (B)": "Singapore",
    "UK (C)": "United Kingdom",
    "US (D)": "United States",
    "CN (E)": "China",
    "KR (F)": "South Korea",
    "UAE (G)": "United Arab Emirates",
    "BR (H)": "Brazil",
    "FR (I)": "France",
    "DE (J)": "Germany",
    "AU (K)": "Australia"
}


def render(sociodemo_df):
    st.title("Socio-demographics & distribution")

    # GENDER =======================================
    st.subheader("Gender distribution – Total vs. Korea & UAE")

    gender_data = sociodemo_df.iloc[2:4, 0:12].copy()
    gender_data.columns = [
        "Gender", "Total (A)", "KR (F)", "UAE (G)", "SG (B)", "UK (C)", "US (D)",
        "CN (E)", "BR (H)", "FR (I)", "DE (J)", "AU (K)"
    ]

    for col in gender_data.columns[1:]:
        gender_data[col] = pd.to_numeric(
            gender_data[col].astype(str).str.replace("%", "").str.strip(), errors="coerce"
        )

    gender_long = gender_data.melt(id_vars="Gender", var_name="Country", value_name="Percentage")
    gender_long.dropna(subset=["Percentage"], inplace=True)
    gender_long["Country_clean"] = gender_long["Country"].map(country_label_map)
    default_visible = ["South Korea", "United Arab Emirates", "All Countries"]
    gender_long = gender_long[gender_long["Country_clean"].isin(default_visible)]

    fig_gender = px.bar(
        gender_long,
        x="Gender",
        y=gender_long["Percentage"] * 100,
        color="Country_clean",
        barmode="group",
        text=(gender_long["Percentage"] * 100).round(1).astype(str) + "%",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig_gender.update_layout(
        title_text="Gender distribution across selected countries",
        yaxis_title="%",
        xaxis_title="Gender",
        legend_title_text="Country",
        bargap=0.15,
        bargroupgap=0.05
    )
    st.plotly_chart(fig_gender, use_container_width=True)

    # ⬇️ Download Gender Chart
    gender_png = prepare_figure_for_export(fig_gender)
    st.download_button(
        label="⬇️ Download Gender Chart (PNG)",
        data=gender_png,
        file_name="gender_chart.png",
        mime="image/png"
    )

    # AGE ==========================================
    st.subheader("Age distribution – Total sample")

    age_data = sociodemo_df.iloc[10:17, [0, 1]].copy()
    age_data.columns = ["Age Group", "Total"]
    age_data["Total"] = pd.to_numeric(
        age_data["Total"].astype(str).str.replace("%", "").str.strip(), errors="coerce"
    )
    age_data.dropna(subset=["Total"], inplace=True)

    fig_age = px.bar(
        age_data,
        x="Age Group",
        y=age_data["Total"] * 100,
        text=(age_data["Total"] * 100).round(1).astype(str) + "%",
        color_discrete_sequence=["#AB63FA"]
    )
    fig_age.update_layout(
        title_text="Age distribution (Total sample)",
        yaxis_title="%",
        xaxis_title="Age group"
    )
    st.plotly_chart(fig_age, use_container_width=True)

    # ⬇️ Download Age Chart
    age_png = fig_age.to_image(format="png", width=1600, height=900, scale=2)
    st.download_button(
        label="⬇️ Download Age Chart (PNG)",
        data=age_png,
        file_name="age_chart.png",
        mime="image/png"
    )

    st.markdown("> The age and gender distribution has been checked for quota fulfilment and reflects the general population structure of each country. Exceptions are the Gender distribution of South Korea and United Arab Emirates.")
