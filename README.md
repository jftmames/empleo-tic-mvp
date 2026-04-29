# Empleo Tecnológico en España · MVP académico v0.2

[![CFF](https://img.shields.io/badge/citable-CFF-7a1f1f)](./CITATION.cff)
[![License](https://img.shields.io/badge/license-MIT-1a1612)](./LICENSE)
[![Python](https://img.shields.io/badge/python-3.11-b8860b)](./Dockerfile)
[![Docker](https://img.shields.io/badge/reproducible-Docker-1a1612)](./docker-compose.yml)

Lectura crítica del empleo tecnológico español a partir de la EPA T1 2026.
Aplicación Streamlit + análisis estadístico formal (Jupyter) + reproducibilidad
contenedorizada.

**Autor:** José Fernández Tamames · UNIE Universidad
**ORCID:** 0009-0007-8851-9833
**Versión:** v0.2 · 29-IV-2026
**Citación:** ver `CITATION.cff`

---

## Hipótesis central, validada estadísticamente

El empleo tecnológico español admite dos definiciones operativas que arrojan
magnitudes muy distintas y *cuya divergencia crece de forma estadísticamente
significativa*:

| Métrica | Volumen 2024 | Variación 2019-2024 |
|---|---|---|
| Sector TIC (rama CNAE Sección J) | 644.000 | +172k (+36%) |
| Especialistas TIC (ocupación CNO 25/35) | 1.000.000 | +335k (+50%) |
| **Gap (millón invisible)** | **356.000** | **+163k** |

**Mann-Kendall** confirma tendencia creciente significativa para el sector
en agregado (Z=5.74, p<0.001) y para Actividades informáticas (Z=2.83,
p=0.005), con caída no significativa pero consistente para Telecomunicaciones.

**Friedman + Wilcoxon** confirman que las tres trayectorias subsectoriales
son estadísticamente distintas (Act. informáticas vs Telecom: p<0.0001).

**STL** confirma estacionalidad cuasi-nula del sector TIC (Var(S)/Var(Y) ≈
0.000–0.006). La caída T1 2026 NO se neutraliza apelando a estacionalidad.

Resultados completos en `notebooks/analisis_formal.ipynb`.

---

## Quickstart

### Opción A — Local con Python

```bash
unzip empleo_tic_mvp.zip
cd empleo_tic_mvp/

python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Streamlit
streamlit run app.py
# → http://localhost:8501

# Jupyter (en otra terminal)
jupyter lab notebooks/analisis_formal.ipynb
# → http://localhost:8888
```

### Opción B — Docker (recomendado, reproducible)

```bash
# Levanta Streamlit + JupyterLab simultáneamente
docker-compose up -d

# Streamlit:    http://localhost:8501
# JupyterLab:   http://localhost:8888

# Logs:
docker-compose logs -f streamlit
```

### Opción C — Solo Streamlit en Docker

```bash
docker build -t empleo-tic-mvp .
docker run -p 8501:8501 empleo-tic-mvp
```

---

## Estructura del proyecto

```
empleo_tic_mvp/
├── app.py                          ← Streamlit principal (6 tabs)
├── requirements.txt                ← Dependencias completas
├── Dockerfile                      ← Imagen reproducible
├── docker-compose.yml              ← Streamlit + Jupyter
├── CITATION.cff                    ← Metadatos para citación
├── README.md                       ← Este archivo
│
├── data/                           ← CSVs reproducibles
│   ├── sector_tic_trimestral.csv
│   ├── especialistas_tic_anual.csv
│   ├── empleo_tic_ccaa.csv
│   └── epa_macro.csv
│
├── modules/                        ← Lógica Python
│   ├── data_loader.py              ← Carga + caching
│   ├── analysis.py                 ← Métricas (divergencia, HHI, etc.)
│   ├── viz.py                      ← Plotly editorial
│   └── ine_downloader.py           ← Cliente API INE Tempus 3.0
│
└── notebooks/
    └── analisis_formal.ipynb       ← Mann-Kendall, STL, Friedman
```

---

## Tabs de la aplicación Streamlit

1. **§ I Macro EPA** — contexto general T1 2026, KPIs, serie histórica
2. **§ II Divergencia** — el millón invisible: rama vs. ocupación
3. **§ III Subsectores** — quién crece, quién encoge en CNAE 61/62/63
4. **§ IV Geografía** — concentración territorial, índice HHI
5. **§ V Metodología** — la ruptura CNAE-2009 → CNAE-2025
6. **§ VI Datos** — descarga CSV/Excel, bundle completo

---

## Análisis estadístico formal (notebook)

El notebook `notebooks/analisis_formal.ipynb` formaliza tres preguntas:

1. **¿Hay tendencia significativa en el empleo TIC?**
   → Test de Mann-Kendall modificado (Hamed-Rao 1998) con corrección por
   autocorrelación. Sen's slope estimator para magnitud.

2. **¿Es ruido estacional o cambio de tendencia?**
   → Descomposición STL (Seasonal-Trend LOESS). Cuantificación de varianza
   explicada por componente.

3. **¿Las divergencias entre subsectores son estadísticamente distintas?**
   → Friedman χ² (no paramétrico, medidas repetidas) + post-hoc Wilcoxon
   con corrección Bonferroni.

4. **Bonus: ¿el gap rama/ocupación crece?**
   → Mann-Kendall sobre la serie del gap absoluto.

---

## Cliente API INE (descarga automática)

`modules/ine_downloader.py` permite reemplazar los CSV estáticos por descargas
en vivo desde INEbase:

```python
from modules.ine_downloader import fetch_table, fetch_seccion_J

# Descarga últimos 8 trimestres de empleo por rama
df = fetch_table(table_id=4128, n_periods=8)

# Helper específico para Sección J (Información y Comunicaciones)
df_j = fetch_seccion_J(n_periods=24)
```

API público de INE Tempus 3.0, sin autenticación. Documentación oficial:
https://www.ine.es/dyngs/DAB/index.htm?cid=1099

---

## Reproducibilidad

El proyecto cumple con el principio de reproducibilidad académica de tres niveles:

- **Datos**: todos los CSVs incluidos, todos con columna `fuente` que documenta
  origen y limitaciones.
- **Código**: módulos Python con type hints, docstrings, separación de
  responsabilidades. Todo testeado.
- **Entorno**: `requirements.txt` con versiones mínimas + Dockerfile con
  Python 3.11 fijado.

Para depositar en Zenodo / OpenAIRE basta con generar release de GitHub:
el `CITATION.cff` proporciona los metadatos automáticamente.

---

## Limitaciones conocidas

1. **Series 2024-T3 a 2026-T1**: Subsector dentro de Sección J proviene de
   Randstad Research, no de microdatos EPA brutos. Reemplazar con descarga
   automática (`ine_downloader.py`) cuando estén disponibles tablas
   CNAE-2025 con histórico.
2. **CCAA fuera del top 4**: Estimaciones a partir del peso medio del sector
   TIC; requieren validación con tabla provincial EPA.
3. **Especialistas TIC trimestrales**: ONTSI publica cifra anual. Para serie
   trimestral hay que cruzar microdatos EPA con CNO-2011 a 3 dígitos.
4. **Variable género**: solo en serie anual.

---

## Roadmap

### v0.2 (actual) ✓
- ✓ Streamlit con 6 tabs
- ✓ Análisis estadístico formal (Mann-Kendall, STL, Friedman)
- ✓ Cliente API INE Tempus 3.0
- ✓ Dockerfile + docker-compose
- ✓ CITATION.cff

### v0.3 (próximo)
- [ ] Descarga automática microdatos EPA T1 2026 con doble codificación CNAE
- [ ] Cuantificación del "drift" categórico CNAE-2009 → CNAE-2025
- [ ] Test de Chow para cambio estructural en T1 2024
- [ ] Comparativa europea con NACE Rev. 2.1 (Eurostat)

### v1.0 (publicación)
- [ ] Paper en *Ratio & Machina*
- [ ] DOI Zenodo
- [ ] Replicación independiente

---

## Marco teórico subyacente

Este MVP forma parte de la línea sobre la *Causa Segunda* aplicada a la
estadística pública: cómo las decisiones administrativas (reglamentos
europeos, clasificaciones CNAE, definiciones operativas) no reflejan
pasivamente la realidad sino que la reescriben performativamente.

La transición CNAE-2009 → CNAE-2025 (Reglamento Delegado UE 2023/137) es
el caso paradigmático. Las ramas más afectadas por automatización e IA
—reparación, almacenamiento, actividades técnicas auxiliares— cambian de
hogar estadístico precisamente cuando más relevante sería medir su
evolución con consistencia. La estadística pública mide cada vez peor
lo que pretende medir, y al hacerlo configura las decisiones de política
pública sobre una base sesgada.

El presente MVP es el banco de pruebas empírico de esta tesis, y forma
parte del ecosistema de investigación en torno al MTI (Métrica de
Trazabilidad de la Intención) y al T3P (Test de los Tres Pilares).

---

## Citación

```bibtex
@software{fernandez_tamames_2026_empleo_tic,
  author       = {Fernández Tamames, José},
  title        = {Empleo Tecnológico en España: el millón invisible},
  version      = {0.2.0},
  year         = {2026},
  publisher    = {UNIE Universidad},
  url          = {https://github.com/jtamames/empleo-tic-mvp}
}
```

Ver `CITATION.cff` para metadatos completos.

---

## Contacto

**José Fernández Tamames**
jtamames@unie.es
ORCID: 0009-0007-8851-9833
UNIE Universidad · Cátedra de Filosofía y Tecnología

---

## Fuentes primarias

1. INE (28-IV-2026). *Encuesta de Población Activa, T1 2026* — Nota de prensa.
2. ONTSI - Red.es (2025). *Empleo Tecnológico — Edición 2025*.
3. Randstad Research (febrero 2026). *Mercado de trabajo en sector
   telecomunicaciones e IT 2025*.
4. Reglamento Delegado (UE) 2023/137 sobre clasificación CNAE-2025/NACE 2.1.
5. Cedefop (2025). *Skills Forecast — España*.

---

*Licencia MIT · UNIE Universidad · Cátedra de Filosofía y Tecnología · 2026*
