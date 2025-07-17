import plotly.graph_objects as go


def prepare_figure_for_export(
    fig: go.Figure,
    *,
    title_size: int = 24,
    label_size: int = 20,
    tick_size: int = 18,
    legend_size: int = 18,
    width: int = 1600,
    height: int = 900,
    scale: int = 2,
    colorway=None
):
    """
    Optimiert ein Plotly-Figure-Objekt für Export (z. B. für PowerPoint) und gibt ein PNG-Byte-Objekt zurück.
    Gibt None zurück, wenn der Export fehlschlägt (z.B. auf Streamlit Cloud ohne Chromium).
    """
    fig.update_layout(
        font=dict(size=label_size, color="black"),
        title_font=dict(size=title_size, color="black"),
        legend=dict(font=dict(size=legend_size, color="black")),
        xaxis=dict(
            tickfont=dict(size=tick_size, color="black"),
            title_font=dict(size=label_size, color="black"),
            tickangle=-30
        ),
        yaxis=dict(
            tickfont=dict(size=tick_size, color="black"),
            title_font=dict(size=label_size, color="black")
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=80, b=140, r=120)
    )

    if colorway:
        fig.update_layout(colorway=colorway)

    try:
        return fig.to_image(format="png", width=width, height=height, scale=scale)
    except Exception as e:
        print(f"PNG export failed: {e}")
        return None
