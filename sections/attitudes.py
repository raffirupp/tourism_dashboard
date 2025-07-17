import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sections.utils import prepare_figure_for_export
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans


def render(_):
    st.title("Attitudes towards vacations")

    # Daten laden
    df = pd.read_csv("data/Cleaned_Tourism_Attitudes.csv")

    country_map = {
        "Total": "All Countries", "SG": "Singapore", "UK": "United Kingdom",
        "US": "United States", "CN": "China", "KR": "South Korea",
        "UAE": "United Arab Emirates", "BR": "Brazil", "FR": "France",
        "DE": "Germany", "AU": "Australia"
    }
    df["Country_clean"] = df["Country"].map(country_map)

    short_labels = {
        "A": "Vacation as joy",
        "B": "Vacation as stress",
        "C": "Active vacations",
        "D": "Relaxed vacations",
        "E": "Risk-taking",
        "F": "Familiar places",
        "G": "Eco-conscious",
        "H": "Luxury travel"
    }

    # Radar Chart
    st.subheader("Compare agreement across countries")

    available_countries = df["Country"].unique()
    country_options = [country_map[c] for c in available_countries if c in country_map]
    selected_countries = st.multiselect(
        "Select countries to compare:",
        options=country_options,
        default=["All Countries"]
    )

    df_unique = df.drop_duplicates(subset=["Country_clean", "Statement_Code"])
    radar_df = df_unique.pivot(index="Country_clean", columns="Statement_Code", values="Agreement")

    statements = df_unique[["Statement_Code", "Statement_Text"]].drop_duplicates().sort_values("Statement_Code")
    codes = statements["Statement_Code"].tolist()
    theta = [f"{short_labels[c]} ({c})" for c in codes]

    fig = go.Figure()
    color_sequence = px.colors.qualitative.Set2

    for i, country in enumerate(selected_countries):
        if country in radar_df.index:
            values = radar_df.loc[country, codes].values
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=theta,
                fill='toself',
                name=country,
                line=dict(color=color_sequence[i % len(color_sequence)])
            ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title="Agreement with vacation statements by country",
        height=650
    )
    st.plotly_chart(fig, use_container_width=True)

    radar_png = prepare_figure_for_export(fig)
    if radar_png:
        st.download_button(
            label="⬇️ Download Radar Chart (PNG)",
            data=radar_png,
            file_name="radar_vacation_attitudes.png",
            mime="image/png"
        )
    else:
        st.info("PNG export not available in this environment. Please use the interactive chart above.")

    # Country Comparison Barplot
    st.subheader("Compare a single statement across countries")

    statement_options = df_unique[["Statement_Code", "Statement_Text"]].drop_duplicates()
    label_map = {
        f"{short_labels[row['Statement_Code']]} ({row['Statement_Code']})": row["Statement_Code"]
        for _, row in statement_options.iterrows()
    }

    selection = st.selectbox("Select a statement:", list(label_map.keys()))
    selected_code = label_map[selection]

    filtered = df[df["Statement_Code"] == selected_code].copy()
    filtered = filtered.sort_values(by="Agreement", ascending=False)

    fig_bar = px.bar(
        filtered,
        x="Country_clean",
        y="Agreement",
        color="Country_clean",
        color_discrete_sequence=px.colors.qualitative.Prism,
        title=f"Agreement with: {selection}"
    )
    fig_bar.update_layout(showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

    # Cluster Analysis
    st.subheader("🌍 Country Clusters Based on Vacation Attitudes")

    df_clu = df.drop_duplicates(subset=["Country", "Statement_Code"])
    df_matrix = df_clu.pivot(index="Country", columns="Statement_Code", values="Agreement").dropna()
    df_matrix = df_matrix[~df_matrix.index.str.contains("Cluster|Total|nan", case=False)]

    scaler = StandardScaler()
    scaled = scaler.fit_transform(df_matrix)

    pca = PCA(n_components=2)
    pca_data = pca.fit_transform(scaled)

    kmeans = KMeans(n_clusters=3, n_init=10, random_state=42)
    clusters = kmeans.fit_predict(scaled)

    df_cluster = pd.DataFrame(pca_data, columns=["PC1", "PC2"])
    df_cluster["Country"] = df_matrix.index
    df_cluster["Cluster"] = clusters.astype(str)

    fig_cluster = px.scatter(
        df_cluster,
        x="PC1",
        y="PC2",
        color="Cluster",
        text="Country",
        title="Clusters of Countries Based on Vacation Attitudes",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_cluster.update_traces(
        textposition="top center",
        marker=dict(size=20, line=dict(width=2, color="black"))
    )
    st.plotly_chart(fig_cluster, use_container_width=True)

    cluster_png = prepare_figure_for_export(fig_cluster)
    if cluster_png:
        st.download_button(
            label="⬇️ Download Cluster Chart (PNG)",
            data=cluster_png,
            file_name="cluster_scatter_vacation_attitudes.png",
            mime="image/png"
        )
    else:
        st.info("PNG export not available in this environment. Please use the interactive chart above.")

    # Clusterzentren
    original_centers = pd.DataFrame(
        scaler.inverse_transform(kmeans.cluster_centers_),
        columns=df_matrix.columns
    )
    original_centers.rename(columns=short_labels, inplace=True)
    original_centers.index.name = "Cluster"

    st.markdown("### 🔍 Cluster Characteristics (Average Agreement per Statement)")
    st.dataframe(original_centers.style.highlight_max(axis=0, color="lightgreen"))

    # Cluster Profiles Radar
    st.subheader("📊 Cluster Profiles (Radar View)")

    categories = list(original_centers.columns)
    radar_fig = go.Figure()

    for i, row in original_centers.iterrows():
        radar_fig.add_trace(go.Scatterpolar(
            r=row.values,
            theta=categories,
            fill='toself',
            name=f'Cluster {i}',
            line=dict(width=2)
        ))

    radar_fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title="Average Agreement by Cluster (Radar View)",
        showlegend=True,
        height=600
    )
    st.plotly_chart(radar_fig, use_container_width=True)

    radar_cluster_png = prepare_figure_for_export(radar_fig)
    if radar_cluster_png:
        st.download_button(
            label="⬇️ Download Cluster Radar Chart (PNG)",
            data=radar_cluster_png,
            file_name="cluster_radar_vacation_attitudes.png",
            mime="image/png"
        )
    else:
        st.info("PNG export not available in this environment. Please use the interactive chart above.")

    # Method Note
    st.markdown("""
    ### 📘 Methodological Note

    Clustering was based on z-score normalized agreement profiles. PCA was used for 2D visualization.
    """)
