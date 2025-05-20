import streamlit as st
import pandas as pd
from sections.utils import prepare_figure_for_export
import plotly.express as px
import plotly.figure_factory as ff
from scipy.cluster.hierarchy import linkage
from sklearn.preprocessing import StandardScaler
from io import BytesIO

@st.cache_data
def load_last_vacation_data():
    df = pd.read_csv("data/Cleaned_LastVacation_FINAL_FIXED.csv")
    df = df.dropna(subset=["Percentage"])
    df = df[~df["Answer"].str.contains("Count", case=False, na=False)]
    df["Answer"] = df["Answer"].astype(str).str.strip()
    df["Percentage"] = (df["Percentage"] * 100).round(1)

    df.loc[(df["Question_Code"] == "QDuration") & (df["Answer"].isin(["Short trip", "2-4 nights"])), "Answer"] = "Short trip / 2-4 nights"
    df.loc[(df["Question_Code"] == "QDuration") & (df["Answer"].isin(["Medium trip", "5-7 nights"])), "Answer"] = "Medium trip / 5-7 nights"
    df.loc[(df["Question_Code"] == "QDuration") & (df["Answer"].isin(["Long trip", "8-14 nights"])), "Answer"] = "Long trip / 8-14 nights"
    df.loc[(df["Question_Code"] == "QDuration") & (df["Answer"].isin(["Extra long trip", "15 or more nights"])), "Answer"] = "Extra long trip / 15 or more nights"
    df.loc[(df["Question_Code"] == "QDuration") & (df["Answer"].isin(["1 night", "Overnight stay"])), "Answer"] = "Overnight stay / 1 night"

    df.loc[df["Question_Code"] == "QWhere", "Answer"] = df.loc[df["Question_Code"] == "QWhere", "Answer"].replace({
        r"^Domestically.*": "Domestically, within my country",
        r"^International.*": "Internationally, outside my country",
        r"^Both domest.*": "Both domestically and internationally"
    }, regex=True)

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
    st.title("Last Vacation Insights")

    df = load_last_vacation_data()

    # Dendrogramm ganz oben anzeigen mit Plotly
    st.subheader("🌍 Hierarchical Clustering of Countries based on Vacation Behavior")

    df_clu = df[df["Country"] != "Total"].copy()
    pivot_df = df_clu.pivot_table(
        index="Country",
        columns=["Question_Code", "Answer"],
        values="Percentage",
        aggfunc="mean"
    ).fillna(0)

    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(pivot_df)
    linkage_matrix = linkage(scaled_data, method='ward')

    fig_dendro = ff.create_dendrogram(
        scaled_data,
        orientation='left',
        labels=pivot_df.index.tolist(),
        hovertext=pivot_df.index.tolist()
    )
    fig_dendro.update_layout(width=1000, height=700, margin=dict(t=50, l=250, r=50, b=50))
    st.plotly_chart(fig_dendro, use_container_width=True)

    # Export als PNG (optional)
    png_buf = BytesIO()
    fig_dendro.write_image(png_buf, format="png", width=1000, height=700, scale=2)
    st.download_button(
        label="⬇️ Download Dendrogram (PNG)",
        data=png_buf.getvalue(),
        file_name="dendrogram_vacation_clusters.png",
        mime="image/png",
        key="dl_dendro_png"
    )

    st.download_button(
        label="⬇️ Download Dendrogram (HTML)",
        data=fig_dendro.to_html(),
        file_name="dendrogram_vacation_clusters.html",
        mime="text/html",
        key="dl_dendro_html"
    )

    st.markdown("""
    ### 🔍 Interpretation of Clusters
    Based on the hierarchical clustering above, we observe grouping patterns such as:

    - **Germany** and **France** tend to cluster closely, possibly due to similar accommodation preferences and vacation durations.
    - **Brazil** stands apart, which could be due to a higher rate of domestic travel or different travel companions.
    - **United Arab Emirates** often clusters away from Western countries, potentially due to differences in travel motivations and vacation timing.

    These clusters help reveal underlying patterns in travel behavior, such as regional preferences, cultural factors, or infrastructure-driven decisions.
    """)

    st.markdown("""
    > **Note on Country Selection**  
    > For each question below, two countries are preselected for comparison based on the largest observed difference in response patterns.  
    > This approach highlights particularly contrasting travel behaviors and attitudes, helping to identify cultural or regional divergences.
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
        total_df = df_q[(df_q["Country_clean"] == "Total")].copy()

        if question == "QWhen":
            order = [
                "In the last week", "In the last month", "In the last 3 months",
                "In the last 6 months", "In the last 12 months",
                "Longer than 12 months ago", "Never"
            ]
        elif question == "QDuration":
            order = [
                "Overnight stay / 1 night", "Short trip / 2-4 nights",
                "Medium trip / 5-7 nights", "Long trip / 8-14 nights",
                "Extra long trip / 15 or more nights"
            ]
        elif question == "QWhere":
            order = [
                "Domestically, within my country",
                "Internationally, outside my country",
                "Both domestically and internationally"
            ]
        else:
            order = total_df.sort_values("Percentage", ascending=False)["Answer"].tolist()

        total_df["Answer"] = pd.Categorical(total_df["Answer"], categories=order, ordered=True)
        total_df = total_df.sort_values("Answer")

        fig_total = px.bar(
            total_df, x="Answer", y="Percentage", text="Percentage",
            title="", color_discrete_sequence=["#5DADE2"]
        )
        fig_total.update_layout(showlegend=False)
        st.plotly_chart(fig_total, use_container_width=True)

        fig_total_png = prepare_figure_for_export(
            fig_total, title_size=24, label_size=20, tick_size=18, legend_size=18,
            width=1600, height=900, scale=2
        )
        st.download_button(
            label="⬇️ Download Total Sample Chart (PNG)",
            data=fig_total_png,
            file_name=f"{question}_total_sample_chart.png",
            mime="image/png",
            key=f"dl_total_{question}"
        )

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
            compare_df = compare_df[compare_df["Answer"].isin(order)]
            compare_df["Answer"] = pd.Categorical(compare_df["Answer"], categories=order, ordered=True)
            compare_df = compare_df.sort_values(["Answer", "Country_clean"])

            fig_compare = px.bar(
                compare_df, x="Answer", y="Percentage", color="Country_clean",
                text="Percentage", barmode="group",
                color_discrete_sequence=px.colors.qualitative.Prism,
                title=""
            )
            fig_compare.update_layout(showlegend=True)
            st.plotly_chart(fig_compare, use_container_width=True)

            fig_compare_png = prepare_figure_for_export(
                fig_compare, title_size=24, label_size=20, tick_size=18, legend_size=18,
                width=1800, height=1000, scale=2
            )
            st.download_button(
                label="⬇️ Download Country Comparison Chart (PNG)",
                data=fig_compare_png,
                file_name=f"{question}_country_comparison_chart.png",
                mime="image/png",
                key=f"dl_compare_{question}"
            )

        st.markdown("---")

        if question == "QWhere":
            if st.checkbox("Show raw data for QWhere", key=f"raw_data_checkbox_{question}"):
                raw_df = pd.read_csv("data/Cleaned_LastVacation_FINAL_FIXED.csv")
                raw_qwhere = raw_df[raw_df["Question_Code"] == "QWhere"]
                st.dataframe(raw_qwhere)
