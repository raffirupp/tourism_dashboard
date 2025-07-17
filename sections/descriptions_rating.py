import streamlit as st
import pandas as pd
import plotly.express as px

# Globale Definition der Country Map
country_map = {
    "A": "Total", "B": "Singapore", "C": "United Kingdom", "D": "United States",
    "E": "China", "F": "South Korea", "G": "United Arab Emirates",
    "H": "Brazil", "I": "France", "J": "Germany", "K": "Australia"
}


@st.cache_data
def load_description_data():
    df = pd.read_csv("data/Adjective_2_Long_Format_Final.csv")
    df["Country_clean"] = df["Country"].str.extract(r"\((.)\)").iloc[:, 0]
    df["Country_clean"] = df["Country_clean"].map(country_map)
    df["Percentage"] = (df["Percentage"] * 100).round(1)
    return df


def render():
    st.title("Descriptions and Rating")
    st.markdown("### What words would you use to describe your most recent vacation?")

    df = load_description_data()

    df_total = df[df["Country_clean"] == "Total"].copy()
    if not df_total.empty:
        df_total = df_total.sort_values("Percentage", ascending=False)
        fig = px.bar(
            df_total, x="Adjective", y="Percentage", text="Percentage",
            title="Total Sample",
            color_discrete_sequence=["#5DADE2"]
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ No data available for Total Sample.")

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

    df_rating = pd.read_csv("data/QRate_Long_Format_Clean.csv")
    df_rating["Country_clean"] = df_rating["Country"].str.extract(r"\((.)\)").iloc[:, 0]
    df_rating["Country_clean"] = df_rating["Country_clean"].map(country_map)
    df_rating["Percentage"] = (df_rating["Percentage"] * 100).round(1)
    df_rating["Rating"] = pd.to_numeric(df_rating["Rating"], errors="coerce")

    def calculate_nps(group):
        promoters = group[group["Rating"] >= 9]["Percentage"].sum()
        detractors = group[group["Rating"] <= 6]["Percentage"].sum()
        return promoters - detractors

    nps_df = df_rating.groupby("Country_clean").apply(calculate_nps).reset_index(name="NPS")
    nps_df = nps_df.sort_values("NPS", ascending=False)

    fig_nps = px.bar(
        nps_df, x="Country_clean", y="NPS", text="NPS",
        color="NPS", color_continuous_scale="Blues"
    )
    fig_nps.update_layout(showlegend=False, yaxis_title="Net Promoter Score")
    st.plotly_chart(fig_nps, use_container_width=True)

    # ----------------------------------
    # 📦 Boxplot: Ratingverteilung
    # ----------------------------------

    st.markdown("### Distribution of Vacation Ratings by Country")

    weighted_rows = []
    for _, row in df_rating.iterrows():
        n = int(row["Percentage"])
        weighted_rows.extend([{
            "Country_clean": row["Country_clean"],
            "Rating": row["Rating"]
        }] * n)

    df_weighted = pd.DataFrame(weighted_rows)

    fig_box = px.box(
        df_weighted, x="Country_clean", y="Rating",
        points="outliers", color="Country_clean"
    )
    fig_box.update_layout(showlegend=False, yaxis_title="Rating (1–10)")
    st.plotly_chart(fig_box, use_container_width=True)
