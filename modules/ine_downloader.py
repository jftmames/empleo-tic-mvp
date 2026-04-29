"""
ine_downloader.py — Cliente para el API JSON del INE (Tempus 3.0).

Permite descargar series de la EPA y otras operaciones estadísticas directamente
desde INEbase, evitando el manual download de CSVs. La API es pública,
sin autenticación, y devuelve JSON.

Documentación oficial:
    https://www.ine.es/dyngs/DAB/index.htm?cid=1099

Endpoints relevantes para empleo tecnológico:
    DATOS_TABLA/{tabla}                - serie completa de una tabla
    DATOS_SERIE/{cod}                  - serie individual por código
    SERIE_METADATAOPERACION/{op}       - listado de series de una operación

Tablas EPA útiles:
    4128  Ocupados por sexo y rama de actividad (CNAE-2009, deprecada T1 2026)
    65522 Ocupados por sexo y rama de actividad CNAE-2025 (vigente desde T1 2026)
    4126  Ocupados por sexo y sector económico
    3996  Tasas de paro por sexo y CCAA

Autor: José Fernández Tamames · UNIE Universidad
"""

from __future__ import annotations
import json
import time
import warnings
from pathlib import Path
from typing import Optional
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

import pandas as pd

BASE_URL = "https://servicios.ine.es/wstempus/js/ES"
USER_AGENT = "EmpleoTIC-MVP-Academic/0.2 (UNIE Universidad)"


# ───────────────────────────── Cliente bajo nivel ──────────────────────────────
def _fetch_json(endpoint: str, retries: int = 3, timeout: int = 30) -> dict | list:
    """GET al API Tempus con reintentos exponenciales."""
    url = f"{BASE_URL}/{endpoint}"
    last_error: Optional[Exception] = None

    for attempt in range(retries):
        try:
            req = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except (URLError, HTTPError, TimeoutError) as e:
            last_error = e
            wait = 2 ** attempt
            warnings.warn(f"INE API attempt {attempt+1}/{retries} failed: {e}. "
                          f"Retrying in {wait}s...")
            time.sleep(wait)

    raise RuntimeError(f"INE API unreachable after {retries} attempts: {last_error}")


# ───────────────────────────── API públicos ────────────────────────────────────
def fetch_table(table_id: int, n_periods: int = 8, detail: int = 2) -> pd.DataFrame:
    """
    Descarga una tabla completa de INEbase y la devuelve como DataFrame largo.

    Args:
        table_id:   ID de tabla INE (ej. 4128 para EPA por rama).
        n_periods:  Nº de periodos más recientes a recuperar.
        detail:     Nivel de detalle (0=metadatos, 1=básico, 2=completo).

    Returns:
        DataFrame con columnas: serie, fecha, valor, unidad, periodo_str.
    """
    endpoint = f"DATOS_TABLA/{table_id}?nult={n_periods}&det={detail}"
    raw = _fetch_json(endpoint)

    if not isinstance(raw, list):
        raise ValueError(f"Respuesta inesperada del API: {type(raw)}")

    rows = []
    for serie in raw:
        nombre = serie.get("Nombre", "")
        unidad = (serie.get("MetaData", [{}])[0]
                  .get("Variable", {}).get("Nombre", "")) if serie.get("MetaData") else ""
        for d in serie.get("Data", []):
            rows.append({
                "serie": nombre,
                "fecha": pd.Timestamp(d.get("Fecha", 0), unit="ms"),
                "valor": d.get("Valor"),
                "anyo": d.get("Anyo"),
                "periodo": d.get("FK_Periodo"),
                "unidad": unidad,
            })

    return pd.DataFrame(rows)


def fetch_serie(serie_code: str, n_periods: int = 20) -> pd.DataFrame:
    """Descarga una serie temporal individual por código."""
    endpoint = f"DATOS_SERIE/{serie_code}?nult={n_periods}"
    raw = _fetch_json(endpoint)
    data = raw.get("Data", [])
    return pd.DataFrame([{
        "fecha": pd.Timestamp(d["Fecha"], unit="ms"),
        "valor": d["Valor"],
    } for d in data])


# ───────────────────────────── Helpers semánticos ──────────────────────────────
def fetch_seccion_J(n_periods: int = 24) -> pd.DataFrame:
    """
    Descarga el empleo de la Sección J (Información y Comunicaciones) de la EPA.
    Filtra automáticamente la rama tecnológica y devuelve serie limpia.
    """
    df = fetch_table(table_id=4128, n_periods=n_periods)

    mask = df["serie"].str.contains("Información y comunicaciones", case=False, na=False)
    j_only = df[mask].copy()

    if j_only.empty:
        warnings.warn(
            "Tabla 4128 no devolvió Sección J. Posiblemente fue deprecada por CNAE-2025. "
            "Cambia a tabla 65522 cuando esté disponible o usa microdatos."
        )
        return df  # devuelve crudo para inspección

    j_only["valor_miles"] = j_only["valor"]
    return j_only.sort_values("fecha").reset_index(drop=True)


def fetch_macro_epa(n_periods: int = 12) -> pd.DataFrame:
    """Descarga macroindicadores EPA: ocupados, parados, tasa paro."""
    return fetch_table(table_id=3996, n_periods=n_periods)


def cache_to_csv(
    df: pd.DataFrame,
    cache_path: Path | str,
    expire_hours: int = 24
) -> pd.DataFrame:
    """
    Cachea un DataFrame a CSV. Si el cache existe y no ha expirado, lo lee
    en lugar de redescargar. Útil para no machacar el API del INE.
    """
    cache_path = Path(cache_path)
    if cache_path.exists():
        age_hours = (time.time() - cache_path.stat().st_mtime) / 3600
        if age_hours < expire_hours:
            return pd.read_csv(cache_path, parse_dates=["fecha"])

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(cache_path, index=False)
    return df


# ───────────────────────────── CLI testing ─────────────────────────────────────
if __name__ == "__main__":
    print("Test de conectividad con API INE Tempus...")
    try:
        df = fetch_table(table_id=4126, n_periods=4)  # ocupados por sector
        print(f"✓ {len(df)} filas descargadas")
        print(df.head(8))
    except Exception as e:
        print(f"✗ Error: {e}")
