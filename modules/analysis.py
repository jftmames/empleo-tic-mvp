"""
analysis.py — Cálculos derivados sobre los datos cargados.

Implementa las métricas centrales del MVP:
  · variaciones trimestrales e interanuales del sector TIC
  · cálculo de la divergencia rama vs. ocupación (el "millón invisible")
  · concentración geográfica (índice de Herfindahl)
  · tasa de feminización
"""

import pandas as pd
import numpy as np


def calcular_variaciones(df: pd.DataFrame, columna: str) -> pd.DataFrame:
    """Añade columnas de variación trimestral e interanual."""
    df = df.copy().sort_values("fecha").reset_index(drop=True)
    df[f"{columna}_var_trim_pct"] = df[columna].pct_change(periods=1) * 100
    df[f"{columna}_var_anual_pct"] = df[columna].pct_change(periods=4) * 100
    df[f"{columna}_var_trim_abs"] = df[columna].diff(periods=1) * 1000  # a personas
    df[f"{columna}_var_anual_abs"] = df[columna].diff(periods=4) * 1000
    return df


def calcular_divergencia(df_sector: pd.DataFrame, df_especialistas: pd.DataFrame) -> dict:
    """
    Calcula la divergencia entre las dos métricas: rama (sector TIC) y ocupación (especialistas TIC).
    Devuelve diccionario con valores comparables del año más reciente disponible.
    """
    sector_2024 = df_sector[df_sector["año"] == 2024]["total_sector_tic"].mean()
    especialistas_2024 = df_especialistas[df_especialistas["año"] == 2024][
        "especialistas_tic_miles"
    ].iloc[0]

    return {
        "rama_sector_tic": sector_2024,
        "ocupacion_especialistas": especialistas_2024,
        "diferencia_absoluta": especialistas_2024 - sector_2024,
        "diferencia_pct": (especialistas_2024 - sector_2024) / sector_2024 * 100,
        "interpretacion": (
            "La diferencia representa profesionales tecnológicos embebidos en sectores "
            "no tecnológicos (banca, sanidad, AAPP, retail). No son el 'sector TIC' pero "
            "sí son trabajo tecnológico."
        ),
    }


def indice_herfindahl(df_ccaa: pd.DataFrame) -> dict:
    """Calcula índice HHI sobre concentración geográfica del empleo TIC."""
    s = df_ccaa["pct_sobre_total_tic"] / 100
    hhi = (s ** 2).sum() * 10000  # convención HHI 0-10000
    top4 = df_ccaa.head(4)["pct_sobre_total_tic"].sum()
    top2 = df_ccaa.head(2)["pct_sobre_total_tic"].sum()
    return {
        "hhi": round(hhi, 1),
        "top2_pct": round(top2, 1),
        "top4_pct": round(top4, 1),
        "interpretacion_hhi": (
            "alta concentración (>2500)" if hhi > 2500
            else "concentración moderada (1500-2500)" if hhi > 1500
            else "concentración baja (<1500)"
        ),
    }


def tasa_feminizacion(df_especialistas: pd.DataFrame) -> pd.DataFrame:
    """Serie temporal de tasa de feminización del empleo TIC."""
    return df_especialistas[["año", "pct_mujeres"]].copy()


def comparar_subsectores(df_sector: pd.DataFrame, año: int = 2025, trim: int = 3) -> pd.DataFrame:
    """Compara los tres subsectores en un trimestre dado vs. el mismo del año anterior."""
    actual = df_sector[(df_sector["año"] == año) & (df_sector["trim"] == trim)].iloc[0]
    anterior = df_sector[(df_sector["año"] == año - 1) & (df_sector["trim"] == trim)].iloc[0]

    subsectores = ["actividades_informaticas", "telecomunicaciones", "servicios_informacion"]
    nombres = ["Actividades informáticas (CNAE 62)", "Telecomunicaciones (CNAE 61)", "Servicios de información (CNAE 63)"]

    rows = []
    for sub, nom in zip(subsectores, nombres):
        rows.append({
            "subsector": nom,
            "ocupados_actual": actual[sub],
            "ocupados_anterior": anterior[sub],
            "variacion_abs": actual[sub] - anterior[sub],
            "variacion_pct": (actual[sub] - anterior[sub]) / anterior[sub] * 100,
        })
    return pd.DataFrame(rows)
