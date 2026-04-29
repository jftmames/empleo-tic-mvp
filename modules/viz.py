"""
viz.py — Componentes de visualización con paleta editorial-académica.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Paleta editorial coherente con el dashboard HTML
PALETA = {
    "ink": "#1a1612",
    "ink_soft": "#4a4239",
    "paper": "#f4f1ea",
    "accent": "#7a1f1f",
    "accent_soft": "#a84747",
    "gold": "#b8860b",
    "green": "#4a6c3f",
}

LAYOUT_BASE = dict(
    paper_bgcolor=PALETA["paper"],
    plot_bgcolor=PALETA["paper"],
    font=dict(family="Inter, sans-serif", size=12, color=PALETA["ink"]),
    title_font=dict(family="Cormorant Garamond, serif", size=20, color=PALETA["ink"]),
    margin=dict(l=60, r=20, t=60, b=50),
    hovermode="x unified",
    xaxis=dict(showgrid=False, linecolor=PALETA["ink"], linewidth=1),
    yaxis=dict(gridcolor="rgba(26,22,18,0.1)", linecolor=PALETA["ink"], linewidth=1),
)


def serie_sector_tic(df: pd.DataFrame) -> go.Figure:
    """Serie trimestral del sector TIC con desglose por subsector."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["fecha"], y=df["actividades_informaticas"],
        name="Actividades informáticas (62)", mode="lines+markers",
        line=dict(color=PALETA["ink"], width=2.5),
        marker=dict(size=5),
    ))
    fig.add_trace(go.Scatter(
        x=df["fecha"], y=df["telecomunicaciones"],
        name="Telecomunicaciones (61)", mode="lines+markers",
        line=dict(color=PALETA["accent"], width=2.5),
        marker=dict(size=5),
    ))
    fig.add_trace(go.Scatter(
        x=df["fecha"], y=df["servicios_informacion"],
        name="Servicios de información (63)", mode="lines+markers",
        line=dict(color=PALETA["gold"], width=2.5),
        marker=dict(size=5),
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        title="Empleo en sector TIC por subsector · CNAE 2009 (Sección J)",
        yaxis_title="Miles de ocupados",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        height=440,
    )
    return fig


def divergencia_metricas(rama: float, ocupacion: float) -> go.Figure:
    """Visualiza la divergencia rama vs. ocupación como barras horizontales."""
    diff = ocupacion - rama
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=["Especialistas TIC<br>(por ocupación · CNO)", "Sector TIC<br>(por rama · CNAE J)"],
        x=[ocupacion, rama],
        orientation="h",
        marker=dict(
            color=[PALETA["accent"], PALETA["gold"]],
            line=dict(color=PALETA["ink"], width=1.5),
        ),
        text=[f"{ocupacion:.0f}k", f"{rama:.0f}k"],
        textposition="outside",
        textfont=dict(family="JetBrains Mono", size=14, color=PALETA["ink"]),
    ))

    layout = dict(LAYOUT_BASE)
    layout["xaxis"] = dict(showgrid=True, gridcolor="rgba(26,22,18,0.1)",
                            linecolor=PALETA["ink"], title="Miles de personas")
    layout["yaxis"] = dict(showgrid=False, linecolor=PALETA["ink"])
    fig.update_layout(
        **layout,
        title=f"La divergencia: el millón invisible · diferencia ≈ {diff:.0f}k",
        height=320,
        showlegend=False,
    )
    return fig


def comparacion_subsectores(df_comp: pd.DataFrame) -> go.Figure:
    """Variación interanual por subsector."""
    colores = [PALETA["green"] if v >= 0 else PALETA["accent"] for v in df_comp["variacion_pct"]]
    fig = go.Figure(go.Bar(
        x=df_comp["variacion_pct"],
        y=df_comp["subsector"],
        orientation="h",
        marker=dict(color=colores, line=dict(color=PALETA["ink"], width=1.5)),
        text=[f"{v:+.1f}%" for v in df_comp["variacion_pct"]],
        textposition="outside",
        textfont=dict(family="JetBrains Mono", size=14, color=PALETA["ink"]),
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        title="Variación interanual por subsector",
        xaxis_title="% interanual",
        height=320,
        showlegend=False,
    )
    return fig


def mapa_concentracion(df_ccaa: pd.DataFrame) -> go.Figure:
    """Barras de concentración geográfica."""
    fig = go.Figure(go.Bar(
        x=df_ccaa["empleo_tic_miles"],
        y=df_ccaa["ccaa"],
        orientation="h",
        marker=dict(
            color=df_ccaa["pct_sobre_empleo_ccaa"],
            colorscale=[[0, PALETA["paper"]], [0.5, PALETA["gold"]], [1, PALETA["accent"]]],
            colorbar=dict(title="% sobre empleo<br>de la CCAA"),
            line=dict(color=PALETA["ink"], width=1),
        ),
        text=[f"{v:.0f}k" for v in df_ccaa["empleo_tic_miles"]],
        textposition="outside",
        textfont=dict(family="JetBrains Mono", size=11, color=PALETA["ink"]),
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        title="Empleo TIC por Comunidad Autónoma",
        xaxis_title="Miles de ocupados en sector TIC",
        height=560,
        yaxis=dict(autorange="reversed", showgrid=False, linecolor=PALETA["ink"]),
    )
    return fig


def serie_especialistas(df: pd.DataFrame) -> go.Figure:
    """Evolución anual de especialistas TIC y tasa de feminización."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["año"], y=df["especialistas_tic_miles"],
        name="Total especialistas TIC",
        marker=dict(color=PALETA["accent"], line=dict(color=PALETA["ink"], width=1)),
        text=[f"{v:.0f}k" for v in df["especialistas_tic_miles"]],
        textposition="outside",
        yaxis="y",
    ))
    fig.add_trace(go.Scatter(
        x=df["año"], y=df["pct_mujeres"],
        name="% mujeres",
        line=dict(color=PALETA["green"], width=3),
        marker=dict(size=10),
        yaxis="y2",
    ))
    fig.update_layout(
        **{k: v for k, v in LAYOUT_BASE.items() if k != "yaxis"},
        title="Especialistas TIC · serie anual ONTSI",
        yaxis=dict(title="Miles de especialistas", side="left", showgrid=True,
                   gridcolor="rgba(26,22,18,0.1)"),
        yaxis2=dict(title="% mujeres", overlaying="y", side="right",
                    range=[15, 25], showgrid=False),
        legend=dict(orientation="h", y=1.08, x=0),
        height=420,
    )
    return fig


def macro_epa(df_macro: pd.DataFrame) -> go.Figure:
    """Series macro EPA para contexto."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_macro["fecha"], y=df_macro["ocupados_total_miles"] / 1000,
        name="Ocupados (millones)", mode="lines+markers",
        line=dict(color=PALETA["ink"], width=3),
        marker=dict(size=7),
        yaxis="y",
    ))
    fig.add_trace(go.Scatter(
        x=df_macro["fecha"], y=df_macro["tasa_paro"],
        name="Tasa de paro (%)", mode="lines+markers",
        line=dict(color=PALETA["accent"], width=2.5, dash="dot"),
        marker=dict(size=6),
        yaxis="y2",
    ))
    fig.update_layout(
        **{k: v for k, v in LAYOUT_BASE.items() if k != "yaxis"},
        title="Contexto macro · EPA España",
        yaxis=dict(title="Ocupados (millones)", side="left", showgrid=True,
                   gridcolor="rgba(26,22,18,0.1)"),
        yaxis2=dict(title="Tasa de paro (%)", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", y=1.08, x=0),
        height=380,
    )
    return fig
