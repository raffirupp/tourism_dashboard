import streamlit as st
import pandas as pd
import plotly.express as px
from sections.utils import prepare_figure_for_export

@st.cache_data
def load_last_vacation_data():
    df = pd.read_csv("data/Cleaned_LastVacation_FINAL_FIXED.csv")
    df = df.dropna(subset=["Percentage"])
    df = df[~df["Answer"].str.contains("Count", case=False, na=False)]
    df["Answer"] = df["Answer"].astype(str).str.strip()
    df["Percentage"] = (df["Percentage"] * 100).round(1)

    df = df.groupby(["Question_Code", "Question_Text", "Country", "Answer"], as_index=False).agg({"Percentage": "mean"})

    country_map = {
        "SG": "Singapore", "UK": "United Kingdom", "US": "United States",
        "CN": "China", "KR": "South Korea", "UAE": "United Arab Emirates",
        "BR": "Brazil", "FR": "France", "DE": "Germany", "AU": "Australia",
        "Total": "Total"
    }
    df["Country_clean"] = df["Country"].map(country_map)
    return df

def render():
    st.subheader("📊 Differences and Similarities Between Countries – Question-Level View")

    df = load_last_vacation_data()
    df_filtered = df[df["Country"] != "Total"].copy()

    df_grouped = df_filtered.groupby(["Question_Code", "Answer", "Country"], as_index=False)["Percentage"].mean()
    pivot = df_grouped.pivot(index=["Question_Code", "Answer"], columns="Country", values="Percentage")
    pivot["Range"] = pivot.max(axis=1) - pivot.min(axis=1)

    max_diff_per_question = pivot.reset_index().groupby("Question_Code").agg({"Range": "max"}).reset_index()

    question_labels = {
        "QFeat": "Visited attractions",
        "QWhere": "Travel destination",
        "QReasons": "Motivation for vacation",
        "QWhowith": "Travel companions",
        "QDescribe_E": "Description",
        "QWhyno": "Reasons against vacation",
        "QDuration": "Duration",
        "QWhen": "Last vacation timing",
        "QAccom": "Accommodation type"
    }
    max_diff_per_question["Label"] = max_diff_per_question["Question_Code"].map(question_labels)
    max_diff_per_question = max_diff_per_question[max_diff_per_question["Label"] != "Travel destination"]
    
    fig_q_diff = px.bar(
        max_diff_per_question.sort_values("Range", ascending=False),
        x="Label", y="Range",
        title="🔍 Question-Level: Greatest Differences Between Countries",
        color_discrete_sequence=px.colors.sequential.Reds,
        text="Range"
    )
    fig_q_diff.update_layout(
        margin=dict(t=60, l=60, r=80, b=120),
        yaxis_title="max. difference percentage points",
        xaxis_title="",
        xaxis_tickangle=-30,
        yaxis=dict(range=[0, 60])
    )
    st.plotly_chart(fig_q_diff, use_container_width=True)

    fig_q_diff_png = prepare_figure_for_export(fig_q_diff)
    if fig_q_diff_png:
        st.download_button(
            label="⬇️ Download Question Differences Chart (PNG)",
            data=fig_q_diff_png,
            file_name="question_differences_chart.png",
            mime="image/png"
        )
    else:
        st.info("PNG export not available in this environment. Please use the interactive chart above.")

    st.markdown("""
    ### ℹ️ What this chart shows
    We identified for each question the **maximum difference** between any two countries for a single answer option.
    """)

    st.subheader("📊 Country Differences and Similarities")

    df_grouped = df[df["Country"] != "Total"].groupby(["Question_Code", "Answer", "Country"], as_index=False)["Percentage"].mean()
    df_pivot = df_grouped.pivot_table(index=["Question_Code", "Answer"], columns="Country", values="Percentage")
    df_pivot["Range"] = df_pivot.max(axis=1) - df_pivot.min(axis=1)

    top_diff = df_pivot.sort_values("Range", ascending=False).head(15).reset_index()
    fig_diff = px.bar(
        top_diff, x="Answer", y="Range", color="Question_Code",
        title="🔍 Greatest Differences Between Countries",
        color_discrete_sequence=px.colors.sequential.Reds,
        text="Range"
    )
    fig_diff.update_layout(
        margin=dict(t=60, l=60, r=80, b=120),
        yaxis_title="max. difference percentage points",
        xaxis_title="",
        yaxis=dict(range=[0, 70])
    )
    st.plotly_chart(fig_diff, use_container_width=True)

    fig_diff_png = prepare_figure_for_export(fig_diff)
    if fig_diff_png:
        st.download_button(
            label="⬇️ Download Differences Chart (PNG)",
            data=fig_diff_png,
            file_name="differences_chart.png",
            mime="image/png"
        )
    else:
        st.info("PNG export not available in this environment. Please use the interactive chart above.")

    df_sim_filtered = df_pivot.loc[~df_pivot.index.get_level_values("Answer").isin(["Other", "None of the above"])]
    top_sim = df_sim_filtered[df_sim_filtered["Range"] > 0].sort_values("Range").head(15).reset_index()
    fig_sim = px.bar(
        top_sim, x="Answer", y="Range", color="Question_Code",
        title="🤝 Highest Similarities Between Countries",
        color_discrete_sequence=px.colors.sequential.Blues,
        text="Range"
    )
    fig_sim.update_layout(
        margin=dict(t=60, l=60, r=80, b=120),
        yaxis_title="max. difference percentage points",
        xaxis_title="",
        yaxis=dict(range=[0, 12])
    )
    st.plotly_chart(fig_sim, use_container_width=True)

    fig_sim_png = prepare_figure_for_export(fig_sim)
    if fig_sim_png:
        st.download_button(
            label="⬇️ Download Similarities Chart (PNG)",
            data=fig_sim_png,
            file_name="similarities_chart.png",
            mime="image/png"
        )
    else:
        st.info("PNG export not available in this environment. Please use the interactive chart above.")
