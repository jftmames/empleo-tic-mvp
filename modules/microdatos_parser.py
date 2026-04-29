"""
microdatos_parser.py — Parser de microdatos EPA del INE.

Los microdatos EPA se distribuyen como ZIP con TXT de campos posicionales fijos.
URL: https://www.ine.es/prodyser/microdatos.htm

Este módulo implementa:
  · Descarga del ZIP trimestral
  · Parser de campos posicionales según diseño de registro
  · Reconstrucción de series Sección J / División 62 / 61 / 63
  · Cruce CNO-2011 (ocupación) × CNAE (rama) para divergencia rama/ocupación
  · Doble codificación CNAE-2009 / CNAE-2025 desde T1 2026

Variables clave del registro EPA (diseño 2021, posiciones aprox.):
  CCAA      pos 17-18    Comunidad autónoma
  EDAD5     pos 33-34    Grupo quinquenal de edad
  SEXO1     pos 35       Sexo
  AOI       pos 41-42    Situación laboral (1-4=ocupado, 5-6=parado)
  RAMA      pos 88-92    CNAE-2025 a 4 dígitos (desde T1 2026)
  RAMA09    pos 93-97    CNAE-2009 a 4 dígitos (doble codif. 2026)
  OCUP      pos 98-100   CNO-2011 a 3 dígitos
  FACTOREL  pos 138-148  Factor de elevación a población

Para 2026 INE distribuye el campo RAMA con CNAE-2025 y RAMA09 con CNAE-2009
para mantener comparabilidad transitoria.

Autor: José Fernández Tamames · UNIE Universidad
"""

from __future__ import annotations
import io
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.request import urlopen, Request

import pandas as pd

USER_AGENT = "EmpleoTIC-MVP-Academic/1.0"


# ───────────────────────────── Esquema de campos ───────────────────────────────
@dataclass
class FieldSpec:
    """Especificación de un campo posicional del registro EPA."""
    name: str
    start: int  # 1-indexed (como en la documentación INE)
    width: int
    dtype: str = "str"

    @property
    def slice(self) -> slice:
        return slice(self.start - 1, self.start - 1 + self.width)


# Esquema simplificado (subset relevante para empleo TIC).
# El esquema real del INE tiene >100 campos.
EPA_SCHEMA_2026 = [
    FieldSpec("CCAA", start=17, width=2),
    FieldSpec("EDAD5", start=33, width=2),
    FieldSpec("SEXO1", start=35, width=1),
    FieldSpec("NAC1", start=36, width=1),  # nacionalidad
    FieldSpec("AOI", start=41, width=2),  # situación laboral
    FieldSpec("RAMA", start=88, width=5),  # CNAE-2025 (T1 2026+)
    FieldSpec("RAMA09", start=93, width=5),  # CNAE-2009 (doble codificación 2026)
    FieldSpec("OCUP", start=98, width=3),  # CNO-2011
    FieldSpec("FACTOREL", start=138, width=11, dtype="float"),
]

# CCAA codes (oficial INE)
CCAA_MAP = {
    "01": "Andalucía", "02": "Aragón", "03": "Asturias", "04": "Baleares",
    "05": "Canarias", "06": "Cantabria", "07": "Castilla y León",
    "08": "Castilla-La Mancha", "09": "Cataluña", "10": "C. Valenciana",
    "11": "Extremadura", "12": "Galicia", "13": "Madrid", "14": "Murcia",
    "15": "Navarra", "16": "País Vasco", "17": "La Rioja",
    "18": "Ceuta", "19": "Melilla",
}

# Códigos CNO-2011 que cuentan como "especialista TIC" (criterio Eurostat/ONTSI)
# Grupo 25: Profesionales en derecho, ciencias sociales, ciencias y enseñanza
#   → 251-252 incluyen profesionales TIC software
# Grupo 35: Técnicos de apoyo
#   → 351-352 incluyen técnicos TIC
CNO_TIC_CODES = {
    "251", "252", "133",  # profesionales SW, dirección TIC
    "351", "352",  # técnicos TIC
    "381", "382",  # técnicos op. y soporte
}


# ───────────────────────────── Descarga ────────────────────────────────────────
def epa_zip_url(year: int, quarter: int) -> str:
    """Genera URL del fichero EPA microdatos para un trimestre."""
    return (f"https://www.ine.es/ftp/microdatos/epa/"
            f"datos_{year}/epa_{year}t{quarter}.zip")


def download_epa_zip(year: int, quarter: int,
                     dest_dir: Path | str = "data/microdatos") -> Path:
    """
    Descarga el ZIP de microdatos EPA del trimestre indicado.
    Nota: el dominio ine.es debe estar en el allowlist; en entornos restringidos
    descargar manualmente y colocar en dest_dir.
    """
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    url = epa_zip_url(year, quarter)
    dest = dest_dir / f"epa_{year}t{quarter}.zip"

    if dest.exists():
        return dest

    req = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=120) as response:
            dest.write_bytes(response.read())
        return dest
    except Exception as e:
        raise RuntimeError(
            f"No se pudo descargar {url}. "
            f"Descarga manual desde https://www.ine.es/prodyser/microdatos.htm "
            f"y coloca el ZIP en {dest_dir}/. Error: {e}"
        )


# ───────────────────────────── Parser ──────────────────────────────────────────
def parse_epa_txt(content: bytes, schema: list[FieldSpec] = EPA_SCHEMA_2026) -> pd.DataFrame:
    """Parser de campos posicionales fijos. Devuelve DataFrame tipado."""
    text = content.decode("latin-1")  # encoding INE
    lines = [ln for ln in text.split("\n") if ln.strip()]

    rows = []
    for line in lines:
        row = {}
        for f in schema:
            raw = line[f.slice]
            if f.dtype == "float":
                row[f.name] = float(raw) if raw.strip() else None
            else:
                row[f.name] = raw.strip()
        rows.append(row)

    return pd.DataFrame(rows)


def load_epa_microdata(year: int, quarter: int,
                       dest_dir: Path | str = "data/microdatos") -> pd.DataFrame:
    """Pipeline completo: descarga (si no existe), descomprime y parsea."""
    zip_path = download_epa_zip(year, quarter, dest_dir)

    with zipfile.ZipFile(zip_path) as zf:
        # El TXT principal del trimestre suele llamarse epaXTYY.txt
        txt_name = next((n for n in zf.namelist() if n.lower().endswith(".txt")), None)
        if txt_name is None:
            raise ValueError(f"No se encontró TXT dentro de {zip_path}")
        with zf.open(txt_name) as f:
            content = f.read()

    df = parse_epa_txt(content)
    df["CCAA_nombre"] = df["CCAA"].map(CCAA_MAP)
    df["año"] = year
    df["trimestre"] = quarter

    return df


# ───────────────────────── Métricas derivadas ─────────────────────────────────
def aggregate_seccion_J(df: pd.DataFrame, cnae_version: str = "2025") -> pd.DataFrame:
    """
    Agrega ocupados por subsector dentro de Sección J (CNAE-2009)
    o equivalente en CNAE-2025 (sección K para telecom + programación).

    Filtra solo ocupados (AOI ∈ {1,2,3,4}) y aplica factor de elevación.
    """
    field = "RAMA" if cnae_version == "2025" else "RAMA09"
    ocupados = df[df["AOI"].isin(["1", "2", "3", "4", "01", "02", "03", "04"])].copy()

    if cnae_version == "2009":
        # CNAE-2009 Sección J = divisiones 58-63
        ocupados["division"] = ocupados[field].str[:2]
        seccion_j = ocupados[ocupados["division"].isin(["58", "59", "60", "61", "62", "63"])]
        labels = {
            "58": "Edición", "59": "Cinematografía/audiovisual",
            "60": "Radio y TV", "61": "Telecomunicaciones",
            "62": "Programación/consultoría", "63": "Servicios información",
        }
    else:
        # CNAE-2025: J (edición/contenidos) + K (telecom + IT)
        ocupados["division"] = ocupados[field].str[:2]
        # Telecom + programación + IT en la nueva K
        seccion_j = ocupados[ocupados["division"].isin(
            ["58", "59", "60", "61", "62", "63"]
        )]
        labels = {
            "58": "Edición", "59": "Producción audiovisual",
            "60": "Radio y TV", "61": "Telecomunicaciones",
            "62": "Programación/consultoría TI", "63": "Servicios información",
        }

    seccion_j["division_label"] = seccion_j["division"].map(labels)

    agg = seccion_j.groupby("division_label").agg(
        ocupados_estimados=("FACTOREL", "sum"),
        n_muestra=("FACTOREL", "count"),
    ).reset_index()
    agg["ocupados_miles"] = (agg["ocupados_estimados"] / 1000).round(1)

    return agg.sort_values("ocupados_miles", ascending=False)


def calcular_especialistas_tic_microdatos(df: pd.DataFrame) -> dict:
    """
    Calcula la métrica por OCUPACIÓN (no rama): especialistas TIC con
    independencia del sector donde trabajan. Replica metodología ONTSI/Eurostat.
    """
    ocupados = df[df["AOI"].isin(["1", "2", "3", "4", "01", "02", "03", "04"])].copy()

    # Especialista TIC = código CNO-2011 a 3 dígitos en CNO_TIC_CODES
    es_tic = ocupados["OCUP"].astype(str).str.zfill(3).isin(CNO_TIC_CODES)

    total_ocupados = ocupados["FACTOREL"].sum()
    especialistas = ocupados.loc[es_tic, "FACTOREL"].sum()
    mujeres_tic = ocupados.loc[es_tic & (ocupados["SEXO1"] == "6"), "FACTOREL"].sum()

    return {
        "total_ocupados_miles": round(total_ocupados / 1000, 1),
        "especialistas_tic_miles": round(especialistas / 1000, 1),
        "pct_sobre_empleo_total": round(especialistas / total_ocupados * 100, 2),
        "mujeres_tic_miles": round(mujeres_tic / 1000, 1),
        "pct_mujeres_tic": round(mujeres_tic / especialistas * 100, 1) if especialistas else 0,
        "n_muestra_ocupados": len(ocupados),
        "n_muestra_tic": int(es_tic.sum()),
    }


def calcular_divergencia_microdatos(df: pd.DataFrame) -> dict:
    """
    Cuantifica el "millón invisible" desde microdatos puros: diferencia entre
    empleo en Sección J (rama) y especialistas TIC (ocupación).
    """
    # Por rama
    j_2025 = aggregate_seccion_J(df, cnae_version="2025")
    sector_tic_rama = j_2025["ocupados_miles"].sum()

    # Por ocupación
    esp = calcular_especialistas_tic_microdatos(df)
    especialistas = esp["especialistas_tic_miles"]

    return {
        "rama_seccion_J_miles": sector_tic_rama,
        "ocupacion_especialistas_miles": especialistas,
        "gap_absoluto": especialistas - sector_tic_rama,
        "gap_pct_sobre_rama": round(
            (especialistas - sector_tic_rama) / sector_tic_rama * 100, 1
        ) if sector_tic_rama else 0,
    }


# ───────────────────────────── CLI ─────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Uso: python microdatos_parser.py <año> <trimestre>")
        print("Ej.:  python microdatos_parser.py 2026 1")
        sys.exit(1)

    year, quarter = int(sys.argv[1]), int(sys.argv[2])
    print(f"Cargando microdatos EPA {year}T{quarter}...")

    try:
        df = load_epa_microdata(year, quarter)
        print(f"✓ {len(df):,} registros cargados")
        print()
        print("Sección J por subsector (CNAE-2025):")
        print(aggregate_seccion_J(df, "2025").to_string(index=False))
        print()
        print("Especialistas TIC (por ocupación):")
        print(calcular_especialistas_tic_microdatos(df))
        print()
        print("Divergencia rama/ocupación:")
        print(calcular_divergencia_microdatos(df))
    except RuntimeError as e:
        print(f"⚠ {e}")
        print("\nLas funciones del parser están listas. Cuando descargues el ZIP")
        print("manualmente y lo coloques en data/microdatos/, vuelve a ejecutar.")
