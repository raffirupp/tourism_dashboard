import streamlit as st
import pandas as pd
from sections.utils import prepare_figure_for_export
import plotly.express as px
import plotly.figure_factory as ff
from scipy.cluster.hierarchy import linkage
from sklearn.preprocessing import StandardScaler

@st.cache_data
def load_last_vacation_data():
    df = pd.read_csv("data/Cleaned_LastVacation_FINAL_FIXED.csv")
    df = df.dropna(subset=["Percentage"])
    df = df[~df["Answer"].str.contains("Count", case=False, na=False)]
    df["Answer"] = df["Answer"].astype(str).str.strip()
    df["Percentage"] = (df["Percentage"] * 100).round(1)

    country_map = {
        "SG": "Singapore", "UK": "United Kingdom", "US": "United States",
        "CN": "China", "KR": "South Korea", "UAE": "United Arab Emirates",
        "BR": "Brazil", "FR": "France", "DE": "Germany", "AU": "Australia",
        "Total": "Total"
    }
    df["Country_clean"] = df["Country"].map(country_map)
    return df

def render():
    st.title("Last Vacation Insights")

    df = load_last_vacation_data()

    # --- DENDROGRAMM ---
    st.subheader("\U0001F30D Hierarchical Clustering of Countries based on Vacation Behavior")

    df_clu = df[df["Country"] != "Total"].copy()
    pivot_df = df_clu.pivot_table(index="Country", columns=["Question_Code", "Answer"], values="Percentage", aggfunc="mean").fillna(0)

    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(pivot_df)
    linkage_matrix = linkage(scaled_data, method='ward')

    fig_dendro = ff.create_dendrogram(scaled_data, orientation='left', labels=pivot_df.index.tolist())
    fig_dendro.update_layout(width=1000, height=700)
    st.plotly_chart(fig_dendro, use_container_width=True)

    st.markdown("""
    ### \U0001F50D Interpretation of Clusters
    - **Germany** and **France** cluster closely — possibly due to similar accommodation preferences and vacation durations.
    - **Brazil** stands apart — possibly due to higher domestic travel.
    - **UAE** clusters away — potentially due to travel motivations and vacation timing.
    """)

    question_order = [
        "QWhen", "QWhyno", "QDuration", "QWhere",
        "QAccom", "QFeat", "QWhowith", "QReasons", "QDescribe_E"
    ]

    default_countries_by_question = {
        "QWhen": ["Brazil", "China"],
        "QWhyno": ["China", "South Korea"],
        "QDuration": ["France", "South Korea"],
        "QWhere": ["China", "Singapore"],
        "QAccom": ["France", "Singapore"],
        "QFeat": ["Germany", "United Arab Emirates"],
        "QWhowith": ["China", "Brazil"],
        "QReasons": ["Germany", "United Arab Emirates"],
        "QDescribe_E": ["Germany", "United Arab Emirates"]
    }

    for idx, question in enumerate(question_order, 1):
        df_q = df[df["Question_Code"] == question].copy()
        q_text = df_q["Question_Text"].iloc[0]
        st.markdown(f"### {idx}. {q_text}")

        st.markdown("**Total Sample**")
        total_df = df_q[df_q["Country_clean"] == "Total"].copy()

        total_df = total_df.sort_values("Percentage", ascending=False)

        fig_total = px.bar(total_df, x="Answer", y="Percentage", text="Percentage", color_discrete_sequence=["#5DADE2"])
        fig_total.update_layout(showlegend=False)
        st.plotly_chart(fig_total, use_container_width=True)

        st.markdown("#### Country Comparison")
        available_countries = df_q[df_q["Country"] != "Total"]["Country_clean"].dropna().unique().tolist()
        default_selection = default_countries_by_question.get(question, available_countries[:2])

        selected_countries = st.multiselect(
            label="Select countries:",
            options=sorted(available_countries),
            default=default_selection,
            key=f"compare_{question}"
        )

        if selected_countries:
            compare_df = df_q[df_q["Country_clean"].isin(selected_countries)].copy()
            fig_compare = px.bar(compare_df, x="Answer", y="Percentage", color="Country_clean", text="Percentage", barmode="group", color_discrete_sequence=px.colors.qualitative.Prism)
            fig_compare.update_layout(showlegend=True)
            st.plotly_chart(fig_compare, use_container_width=True)

        st.markdown("---")

        if question == "QWhere":
            if st.checkbox("Show raw data for QWhere", key=f"raw_data_checkbox_{question}"):
                raw_df = pd.read_csv("data/Cleaned_LastVacation_FINAL_FIXED.csv")
                raw_qwhere = raw_df[raw_df["Question_Code"] == "QWhere"]
                st.dataframe(raw_qwhere)
