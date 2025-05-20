import streamlit as st
import pandas as pd
import plotly.express as px
from sections.utils import prepare_figure_for_export  


@st.cache_data
def load_description_data():
    df = pd.read_csv("data/Adjective_2_Long_Format_Final.csv")

    # Ländercodes extrahieren und zu Ländernamen mappen
    df["Country_clean"] = df["Country"].str.extract(r"\((.)\)").iloc[:, 0]
    country_map = {
        "A": "Total", "B": "Singapore", "C": "United Kingdom", "D": "United States",
        "E": "China", "F": "South Korea", "G": "United Arab Emirates",
        "H": "Brazil", "I": "France", "J": "Germany", "K": "Australia"
    }
    df["Country_clean"] = df["Country_clean"].map(country_map)

    # ✅ Prozentangaben richtig skalieren
    df["Percentage"] = (df["Percentage"] * 100).round(1)

    return df


def render():
    st.title("Descriptions and Rating")
    st.markdown("### What words would you use to describe your most recent vacation?")

    df = load_description_data()

    # Total Sample
    df_total = df[df["Country_clean"] == "Total"].copy()

    if df_total.empty:
        st.warning("⚠️ No data available for Total Sample.")
    else:
        df_total = df_total.sort_values("Percentage", ascending=False)
        fig = px.bar(
            df_total, x="Adjective", y="Percentage", text="Percentage",
            title="Total Sample",
            color_discrete_sequence=["#5DADE2"]
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Country Comparison
    st.markdown("### Country Comparison")

    available_countries = df["Country_clean"].dropna().unique().tolist()
    available_countries = [c for c in available_countries if c != "Total"]
    default_countries = [c for c in ["Germany", "United Arab Emirates"] if c in available_countries]

    selected_countries = st.multiselect(
        "Select countries:",
        options=sorted(available_countries),
        default=default_countries,
        key="compare_adjectives"
    )

    if selected_countries:
        compare_df = df[df["Country_clean"].isin(selected_countries)].copy()

        if not compare_df.empty:
            fig2 = px.bar(
                compare_df, x="Adjective", y="Percentage", color="Country_clean",
                text="Percentage", barmode="group",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig2.update_layout(showlegend=True)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("No comparison data available for selected countries.")


    # ----------------------------------
    # 🔢 Overall Rating & NPS Analysis
    # ----------------------------------

    st.markdown("### Overall Rating of Your Vacation")

    # Daten laden
    df_rating = pd.read_csv("data/QRate_Long_Format_Clean.csv")

    # Länderzuordnung
    df_rating["Country_clean"] = df_rating["Country"].str.extract(r"\((.)\)").iloc[:, 0]
    country_map = {
        "A": "Total", "B": "Singapore", "C": "United Kingdom", "D": "United States",
        "E": "China", "F": "South Korea", "G": "United Arab Emirates",
        "H": "Brazil", "I": "France", "J": "Germany", "K": "Australia"
    }
    df_rating["Country_clean"] = df_rating["Country_clean"].map(country_map)

    # Prozentangaben skalieren
    df_rating["Percentage"] = (df_rating["Percentage"] * 100).round(1)

    # 🎯 NPS-Berechnung
    df_rating["Rating"] = pd.to_numeric(df_rating["Rating"], errors="coerce")

    def calculate_nps(group):
        promoters = group[group["Rating"] >= 9]["Percentage"].sum()
        detractors = group[group["Rating"] <= 6]["Percentage"].sum()
        return promoters - detractors

    nps_df = df_rating.groupby("Country_clean").apply(calculate_nps).reset_index(name="NPS")
    nps_df = nps_df.sort_values("NPS", ascending=False)

    fig_nps = px.bar(nps_df, x="Country_clean", y="NPS", text="NPS",
                     color="NPS", color_continuous_scale="Blues")
    fig_nps.update_layout(showlegend=False, yaxis_title="Net Promoter Score")
    st.plotly_chart(fig_nps, use_container_width=True)

    nps_png = prepare_figure_for_export(
    fig_nps,
    title_size=26,
    label_size=22,
    tick_size=20,
    legend_size=20,
    width=1600,
    height=900,
    scale=2
    )

    st.download_button(
        label="⬇️ Download NPS Chart (PNG)",
        data=nps_png,
        file_name="nps_vacation_chart.png",
        mime="image/png",
        key="dl_nps"
    )

    # ----------------------------------
    # 📦 Boxplot: Ratingverteilung
    # ----------------------------------

    st.markdown("### Distribution of Vacation Ratings by Country")

    # Ratings duplizieren gemäß Prozentwerten (für realistische Verteilung)
    weighted_rows = []
    for _, row in df_rating.iterrows():
        n = int(row["Percentage"])  # z. B. 45 → 45 Ratings
        weighted_rows.extend([{
            "Country_clean": row["Country_clean"],
            "Rating": row["Rating"]
        }] * n)

    df_weighted = pd.DataFrame(weighted_rows)

    fig_box = px.box(df_weighted, x="Country_clean", y="Rating", points="outliers", color="Country_clean")
    fig_box.update_layout(showlegend=False, yaxis_title="Rating (1–10)")
    st.plotly_chart(fig_box, use_container_width=True)

    box_png = prepare_figure_for_export(
    fig_box,
    title_size=26,
    label_size=22,
    tick_size=20,
    legend_size=20,
    width=1800,
    height=1000,
    scale=2
    )

    st.download_button(
        label="⬇️ Download Boxplot Chart (PNG)",
        data=box_png,
        file_name="boxplot_rating_distribution.png",
        mime="image/png",
        key="dl_boxplot"
    )
