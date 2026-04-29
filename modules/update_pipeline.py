"""
update_pipeline.py — Orquestación de actualizaciones de fuentes públicas.

Cada fuente tiene su propia frecuencia y método de actualización. Este módulo
es el "reloj" del MVP: sabe cuándo cada dataset debería refrescarse y cómo.

CALENDARIO OFICIAL DE PUBLICACIONES:
═══════════════════════════════════════════════════════════════════════════════
  Fuente              Periodicidad    Publicación             Método
  ─────────────────────────────────────────────────────────────────────────────
  EPA (INE)           Trimestral      ~28 abril / 28 julio    API JSON Tempus
                                      / 28 octubre / 28 enero (automatizable ✓)

  ONTSI Empleo TIC    Anual           ~Q1 año siguiente       PDF, manual ✗
                                      (~marzo-abril)          (notificación auto)

  Randstad Research   Irregular       Trimestral aprox.       Web, manual ✗
                                                              (scraping ético)

  Microdatos EPA      Trimestral      Mismo día que EPA       URL fija, ZIP
                                                              (automatizable ✓)
═══════════════════════════════════════════════════════════════════════════════

CAMBIO CRÍTICO CNAE-2025 (T1 2026 en adelante):
  La antigua Sección J se divide en dos. El sector tecnológico ya no se localiza
  por una sola letra. Las tablas CNAE-2009 quedan obsoletas a partir de 2027.

Autor: José Fernández Tamames · UNIE Universidad
"""

from __future__ import annotations
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Optional

import pandas as pd

DATA_DIR = Path(__file__).parent.parent / "data"
SNAPSHOTS_DIR = DATA_DIR / "snapshots"
METADATA_FILE = DATA_DIR / "_pipeline_metadata.json"


# ───────────────────────────── Tipología de fuentes ────────────────────────────
class UpdateMethod(Enum):
    """Cómo se actualiza cada fuente."""
    API_AUTO = "API automática"
    URL_AUTO = "URL fija con parser"
    SCRAPING = "Scraping web (frágil)"
    MANUAL_PDF = "Notificación manual"


class UpdateStatus(Enum):
    FRESH = "✓ actualizado"
    DUE = "⚠ pendiente"
    OVERDUE = "⚠⚠ retrasado"
    MANUAL_PENDING = "✋ acción manual"


@dataclass
class DataSource:
    """Especificación de una fuente de datos del MVP."""
    name: str
    csv_path: Path
    method: UpdateMethod
    days_until_stale: int  # tras este lapso, la fuente se considera "due"
    next_publication_hint: str  # texto descriptivo
    automatable: bool
    notes: str = ""

    @property
    def last_modified(self) -> Optional[datetime]:
        """Devuelve la última fecha de modificación del CSV."""
        if not self.csv_path.exists():
            return None
        return datetime.fromtimestamp(self.csv_path.stat().st_mtime)

    @property
    def age_days(self) -> Optional[int]:
        """Días transcurridos desde última actualización."""
        last = self.last_modified
        if last is None:
            return None
        return (datetime.now() - last).days

    def status(self) -> UpdateStatus:
        """Estado actual de frescura."""
        age = self.age_days
        if age is None:
            return UpdateStatus.OVERDUE
        if not self.automatable and age > self.days_until_stale:
            return UpdateStatus.MANUAL_PENDING
        if age > self.days_until_stale * 1.5:
            return UpdateStatus.OVERDUE
        if age > self.days_until_stale:
            return UpdateStatus.DUE
        return UpdateStatus.FRESH


# ───────────────────────── Catálogo de fuentes ────────────────────────────────
SOURCES = {
    "epa_macro": DataSource(
        name="EPA macro (INE)",
        csv_path=DATA_DIR / "epa_macro.csv",
        method=UpdateMethod.API_AUTO,
        days_until_stale=95,  # trimestral + margen
        next_publication_hint="finales de abril, julio, octubre, enero",
        automatable=True,
        notes="API Tempus 3.0 público. Actualización via GitHub Actions.",
    ),
    "sector_tic_trimestral": DataSource(
        name="Sector TIC trimestral (rama)",
        csv_path=DATA_DIR / "sector_tic_trimestral.csv",
        method=UpdateMethod.API_AUTO,
        days_until_stale=95,
        next_publication_hint="finales de abril, julio, octubre, enero",
        automatable=True,
        notes=("ATENCIÓN: tabla 4128 (CNAE-2009) deprecada en T1 2026. "
               "Migrar a tabla CNAE-2025 cuando esté disponible. "
               "Sección J ahora dividida en J y K."),
    ),
    "especialistas_tic_anual": DataSource(
        name="Especialistas TIC anual (ONTSI)",
        csv_path=DATA_DIR / "especialistas_tic_anual.csv",
        method=UpdateMethod.MANUAL_PDF,
        days_until_stale=365,
        next_publication_hint="ONTSI publica edición anual ~marzo-abril",
        automatable=False,
        notes=("ONTSI no expone API. Requiere descargar PDF anual y "
               "extraer cifra. Pipeline notifica vencimiento."),
    ),
    "empleo_tic_ccaa": DataSource(
        name="Distribución por CCAA",
        csv_path=DATA_DIR / "empleo_tic_ccaa.csv",
        method=UpdateMethod.API_AUTO,
        days_until_stale=95,
        next_publication_hint="trimestral con EPA",
        automatable=True,
        notes="Reconstruible desde tabla EPA por CCAA y rama.",
    ),
}


# ───────────────────────── Operaciones de pipeline ────────────────────────────
def get_pipeline_status() -> pd.DataFrame:
    """Devuelve el estado de frescura de todas las fuentes como DataFrame."""
    rows = []
    for key, src in SOURCES.items():
        age = src.age_days
        rows.append({
            "fuente": src.name,
            "método": src.method.value,
            "automatizable": "Sí" if src.automatable else "No",
            "última_actualización": (src.last_modified.strftime("%Y-%m-%d %H:%M")
                                     if src.last_modified else "N/A"),
            "días_desde_última": str(age) if age is not None else "N/A",
            "estado": src.status().value,
            "próxima_publicación": src.next_publication_hint,
            "notas": src.notes,
        })
    return pd.DataFrame(rows)


def take_snapshot(label: Optional[str] = None) -> Path:
    """Captura snapshot fechado de todos los CSVs actuales para histórico."""
    SNAPSHOTS_DIR.mkdir(exist_ok=True, parents=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    label = label or "auto"
    snap_name = f"{timestamp}_{label}"
    snap_path = SNAPSHOTS_DIR / snap_name
    snap_path.mkdir(exist_ok=True)

    for src in SOURCES.values():
        if src.csv_path.exists():
            dest = snap_path / src.csv_path.name
            dest.write_bytes(src.csv_path.read_bytes())

    metadata = {
        "timestamp": timestamp,
        "label": label,
        "datetime": datetime.now().isoformat(),
        "files": [s.csv_path.name for s in SOURCES.values() if s.csv_path.exists()],
    }
    (snap_path / "metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False))

    return snap_path


def detect_changes_since_last_snapshot() -> dict:
    """Detecta diferencias entre los datos actuales y el último snapshot."""
    if not SNAPSHOTS_DIR.exists():
        return {"status": "no_snapshots"}

    snapshots = sorted([p for p in SNAPSHOTS_DIR.iterdir() if p.is_dir()])
    if not snapshots:
        return {"status": "no_snapshots"}

    last_snap = snapshots[-1]
    changes = {}

    for src in SOURCES.values():
        actual = src.csv_path
        previo = last_snap / src.csv_path.name

        if not actual.exists() or not previo.exists():
            changes[src.name] = "missing_file"
            continue

        df_actual = pd.read_csv(actual)
        df_previo = pd.read_csv(previo)

        if df_actual.shape != df_previo.shape:
            changes[src.name] = {
                "shape_change": True,
                "rows_added": len(df_actual) - len(df_previo),
                "previo_shape": df_previo.shape,
                "actual_shape": df_actual.shape,
            }
        elif not df_actual.equals(df_previo):
            changes[src.name] = "values_changed"
        else:
            changes[src.name] = "unchanged"

    return {
        "status": "compared",
        "last_snapshot": last_snap.name,
        "changes": changes,
    }


def get_publication_calendar(year: Optional[int] = None) -> pd.DataFrame:
    """Calendario de publicaciones del INE para el año dado (por defecto, actual)."""
    year = year or datetime.now().year

    # Calendario aproximado del INE (se publica el último jueves del mes correspondiente)
    epa_dates = [
        (f"T4 {year-1}", datetime(year, 1, 28), "EPA T4 año anterior"),
        (f"T1 {year}", datetime(year, 4, 28), "EPA T1"),
        (f"T2 {year}", datetime(year, 7, 28), "EPA T2"),
        (f"T3 {year}", datetime(year, 10, 28), "EPA T3"),
    ]

    rows = []
    today = datetime.now()
    for label, fecha, descripcion in epa_dates:
        days_until = (fecha - today).days
        rows.append({
            "trimestre": label,
            "fecha_publicación": fecha.strftime("%Y-%m-%d"),
            "días_hasta": f"{days_until} días" if days_until > 0 else "publicado",
            "descripción": descripcion,
            "estado": "próximo" if days_until > 0 else "publicado",
        })

    return pd.DataFrame(rows)


# ───────────────────────── Ejecución manual ───────────────────────────────────
if __name__ == "__main__":
    print("=" * 70)
    print("EMPLEO TIC MVP — Estado del pipeline de datos")
    print("=" * 70)
    print()
    print(get_pipeline_status().to_string(index=False))
    print()
    print("Calendario de publicaciones EPA:")
    print(get_publication_calendar().to_string(index=False))
    print()
    print("Detección de cambios:")
    print(json.dumps(detect_changes_since_last_snapshot(), indent=2, ensure_ascii=False))
