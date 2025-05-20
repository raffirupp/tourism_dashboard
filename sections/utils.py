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
    colorway: list[str] | None = None
) -> bytes:
    """
    Optimiert ein Plotly-Figure-Objekt für Export (z. B. für PowerPoint) und gibt ein PNG-Byte-Objekt zurück.

    Parameter:
    - fig: Plotly-Figure
    - title_size, label_size, tick_size, legend_size: Schriftgrößen in px
    - width, height: Pixelmaße des Bildes
    - scale: Skalierungsfaktor für hohe Auflösung
    - colorway: Optionales Farbset für alle Spuren

    Rückgabe:
    - PNG als Byte-Objekt
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

    return fig.to_image(format="png", width=width, height=height, scale=scale)
