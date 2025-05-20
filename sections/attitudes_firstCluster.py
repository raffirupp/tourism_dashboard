import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go



def render(_):
    st.title("Attitudes towards vacations")

    # ------------------------------
    # 1. Daten einlesen
    # ------------------------------
    df = pd.read_csv("data/Cleaned_Tourism_Attitudes.csv")

    # Länder lesbar machen
    country_map = {
        "Total": "All Countries", "SG": "Singapore", "UK": "United Kingdom",
        "US": "United States", "CN": "China", "KR": "South Korea",
        "UAE": "United Arab Emirates", "BR": "Brazil", "FR": "France",
        "DE": "Germany", "AU": "Australia"
    }
    df["Country_clean"] = df["Country"].map(country_map)

    # Abkürzungen für Statements (neu)
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

    # ------------------------------
    # 2. Radar Chart mit Multi-Select
    # ------------------------------
    st.subheader("Compare agreement across countries")

    available_countries = df["Country"].unique()
    country_options = [country_map[c] for c in available_countries if c in country_map]
    default_selection = ["All Countries"]

    selected_countries = st.multiselect(
        "Select countries to compare:",
        options=country_options,
        default=default_selection
    )

    # Duplikate entfernen
    df_unique = df.drop_duplicates(subset=["Country_clean", "Statement_Code"])
    radar_df = df_unique.pivot(index="Country_clean", columns="Statement_Code", values="Agreement")

    statements = df_unique[["Statement_Code", "Statement_Text"]].drop_duplicates().sort_values("Statement_Code")
    codes = statements["Statement_Code"].tolist()
    theta = [f"{short_labels[c]} ({c})" for c in codes]

    fig = go.Figure()
    # Farbpalette definieren
    color_sequence = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
        "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
        "#bcbd22", "#17becf"
    ]

    # Zeichne Radar-Spuren mit zugewiesenen Farben
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
        height=650,
        showlegend=True,
        legend_orientation="h",
        legend=dict(x=0.5, y=-0.2, xanchor='center')
    )
    st.plotly_chart(fig, use_container_width=True)

    # ------------------------------
    # 3. Country Comparison (Dropdown)
    # ------------------------------
    st.subheader("Compare a single statement across countries")

    # Duplikate vermeiden
    df_nodup = df.drop_duplicates(subset=["Country_clean", "Statement_Code"])

    # Dropdown mit sauberen Labels (kein doppeltes (F) (F))
    statement_options = df_nodup[["Statement_Code", "Statement_Text"]].drop_duplicates()
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

    # ------------------------------
    # 4. Legende unten anzeigen
    # ------------------------------
    st.markdown("""
    <div style='font-size: 0.85em; margin-top: 2em'>
    **Legend**  
    - **A**: I love going on vacations, it is one of the things I look forward to the most  
    - **B**: Vacations are stressful for me  
    - **C**: I like to be physically active during vacations  
    - **D**: For me, relaxing is the most important part of vacations  
    - **E**: I enjoy taking risks or trying new things during vacations  
    - **F**: I prefer familiar places over new destinations  
    - **G**: Environmental impact is important to me when planning vacations  
    - **H**: I enjoy luxury and comfort when traveling  
    </div>
    """, unsafe_allow_html=True)

    # --- 5. Country Clusters Based on Vacation Attitudes ---
    st.subheader("🌍 Country Clusters Based on Vacation Attitudes")

    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    from sklearn.cluster import KMeans

    # Daten vorbereiten
    df_clu = df.drop_duplicates(subset=["Country", "Statement_Code"])
    df_matrix = df_clu.pivot(index="Country", columns="Statement_Code", values="Agreement").dropna()

    # Länder filtern (nur echte Länder)
    df_matrix = df_matrix[~df_matrix.index.str.contains("Cluster|Total|nan", case=False)]

    # Standardisierung
    scaler = StandardScaler()
    scaled = scaler.fit_transform(df_matrix)

    # PCA zur Visualisierung
    pca = PCA(n_components=2)
    pca_data = pca.fit_transform(scaled)

    # KMeans Clustering (k=3)
    kmeans = KMeans(n_clusters=3, n_init=10, random_state=42)
    clusters = kmeans.fit_predict(scaled)

    # DataFrame für Scatterplot
    df_cluster = pd.DataFrame(pca_data, columns=["PC1", "PC2"])
    df_cluster["Country"] = df_matrix.index
    df_cluster["Cluster"] = clusters.astype(str)

    # Visualisierung
    fig = px.scatter(
        df_cluster, x="PC1", y="PC2", color="Cluster", text="Country",
        title="Clusters of Countries Based on Vacation Attitudes",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(height=600, legend_title_text="Cluster")
    st.plotly_chart(fig, use_container_width=True)

    # Clusterzentren auf Originalskala
    original_centers = pd.DataFrame(
        scaler.inverse_transform(kmeans.cluster_centers_),
        columns=df_matrix.columns
    )

    # Klartext-Labels
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
    original_centers.rename(columns=short_labels, inplace=True)
    original_centers.index.name = "Cluster"

    st.markdown("### 🔍 Cluster Characteristics (Average Agreement per Statement)")
    st.dataframe(original_centers.style.highlight_max(axis=0, color="lightgreen"))

    # --- 6. Cluster Radar & Interpretation ---
    st.subheader("📊 Cluster Profiles (Radar View)")


    # Clusterzentren in Originalskala verwenden
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

    # Erklärung zur Methode
    st.markdown("""
    ### 📘 Methodological Note

    To ensure fair clustering across countries, we first applied **z-score normalization** to each country's answers.  
    This avoids countries with generally higher agreement levels (e.g., those consistently rating all statements highly) from dominating the cluster assignment.

    Clustering was then performed on these standardized profiles using **KMeans (k=3)**, followed by **PCA** to allow 2D visualization.

    The radar chart above shows the **mean agreement levels** for each cluster — highlighting typical attitude patterns.
    """)

    # PCA-Loadings (einklappbar)
    with st.expander("🔍 View PCA Loadings (Variable Influence on PC1/PC2)"):
        st.dataframe(loadings.round(3).style.highlight_max(axis=0))



