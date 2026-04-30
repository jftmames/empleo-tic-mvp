"""
data_loader.py — Carga de fuentes públicas para el MVP de empleo tecnológico.

Este módulo abstrae la lectura de los CSV de /data y devuelve DataFrames
limpios, listos para análisis. Pensado para ser reemplazado por una capa
de microdatos INEbase cuando el descargador de microdatos esté operativo.

Autor: José Fernández Tamames · UNIE Universidad
"""

from pathlib import Path
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).parent.parent / "data"


@st.cache_data(ttl=3600)
def load_sector_tic() -> pd.DataFrame:
    """Series trimestrales del sector TIC (rama CNAE — Sección J)."""
    df = pd.read_csv(DATA_DIR / "sector_tic_trimestral.csv")
    df["fecha"] = pd.PeriodIndex(
        df["año"].astype(str) + "Q" + df["trim"].astype(str), freq="Q"
    ).to_timestamp(how="end")
    return df


@st.cache_data(ttl=3600)
def load_especialistas_tic() -> pd.DataFrame:
    """Especialistas TIC anuales (ocupación CNO — métrica ONTSI)."""
    df = pd.read_csv(DATA_DIR / "especialistas_tic_anual.csv")
    return df


@st.cache_data(ttl=3600)
def load_ccaa() -> pd.DataFrame:
    """Distribución geográfica del empleo TIC por CCAA (T3 2025)."""
    df = pd.read_csv(DATA_DIR / "empleo_tic_ccaa.csv")
    return df.sort_values("empleo_tic_miles", ascending=False).reset_index(drop=True)


@st.cache_data(ttl=3600)
def load_epa_macro() -> pd.DataFrame:
    """Macro EPA: ocupados, parados, activos, tasas, sectores."""
    df = pd.read_csv(DATA_DIR / "epa_macro.csv")
    df["fecha"] = pd.PeriodIndex(
        df["año"].astype(str) + "Q" + df["trim"].astype(str), freq="Q"
    ).to_timestamp(how="end")
    return df


@st.cache_data(ttl=3600)
def load_adopcion_ia() -> pd.DataFrame:
    """Serie anual de adopción de IA en empresas españolas (ETICCE INE).

    Fuente clave para diálogo con informe Funcas (2026): mide la velocidad
    real de difusión tecnológica que opera como parámetro ρ en modelos de
    sustitución ocupacional.
    """
    df = pd.read_csv(DATA_DIR / "adopcion_ia_empresarial.csv")
    return df


def get_data_provenance() -> dict:
    """Devuelve metadatos de cada fuente para auditoría académica."""
    return {
        "sector_tic_trimestral": {
            "fuente_primaria": "INE EPA + Randstad Research",
            "ultima_actualizacion": "2026-02-24",
            "metodo": "Reconstrucción a partir de notas de prensa y estudios sectoriales",
            "limitaciones": "Trimestres 2025T4 y 2026T1 son estimaciones lineales pendientes de confirmar con microdatos INEbase",
            "url": "https://www.randstadresearch.es/mercado-trabajo-sector-telecomunicaciones-it/",
        },
        "especialistas_tic_anual": {
            "fuente_primaria": "ONTSI - Red.es",
            "ultima_actualizacion": "2025",
            "metodo": "Métrica por ocupación (CNO-2011) — incluye profesionales TIC en cualquier rama",
            "limitaciones": "Datos anuales; no permite análisis trimestral",
            "url": "https://www.ontsi.es/es/publicaciones/empleo-tecnologico",
        },
        "empleo_tic_ccaa": {
            "fuente_primaria": "Randstad Research a partir de EPA",
            "ultima_actualizacion": "2026-02-24",
            "metodo": "Estimación a partir de % sobre empleo total CCAA",
            "limitaciones": "Estimaciones para CCAA pequeñas; reemplazar con microdatos cuando estén disponibles",
        },
        "epa_macro": {
            "fuente_primaria": "INE EPA",
            "ultima_actualizacion": "2026-04-28",
            "metodo": "Notas de prensa trimestrales oficiales",
            "limitaciones": "Datos sectoriales en CNAE 2009 hasta T4 2025; doble codificación desde T1 2026",
            "url": "https://www.ine.es/dyngs/INEbase/operacion.htm?c=Estadistica_C&cid=1254736176918",
        },
    }
