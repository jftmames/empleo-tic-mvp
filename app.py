"""
═══════════════════════════════════════════════════════════════════════════════
  EMPLEO TECNOLÓGICO EN ESPAÑA — MVP académico
  Lectura crítica de la EPA T1 2026
  
  José Fernández Tamames · UNIE Universidad
  ═══════════════════════════════════════════════════════════════════════════════
  
  Ejecutar con:
      streamlit run app.py
  
  Estructura:
      data/      · CSVs con series públicas
      modules/   · loader, analysis, viz
      app.py     · esta app
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from io import BytesIO

from modules.data_loader import (
    load_sector_tic, load_especialistas_tic, load_ccaa,
    load_epa_macro, load_adopcion_ia, get_data_provenance,
)
from modules.analysis import (
    calcular_variaciones, calcular_divergencia,
    indice_herfindahl, comparar_subsectores,
)
from modules.viz import (
    serie_sector_tic, divergencia_metricas, comparacion_subsectores,
    mapa_concentracion, serie_especialistas, macro_epa,
)
from modules.update_pipeline import (
    get_pipeline_status, get_publication_calendar,
    detect_changes_since_last_snapshot, take_snapshot,
)

# ═════════════════════════════ Configuración ═════════════════════════════════
st.set_page_config(
    page_title="Empleo Tecnológico — MVP académico",
    page_icon="§",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS editorial coherente con el dashboard HTML
st.markdown("""
<style>
    .main { background-color: #f4f1ea; }
    [data-testid="stSidebar"] { background-color: #ebe6da; }
    h1, h2, h3 { font-family: 'Cormorant Garamond', Georgia, serif !important;
                 font-weight: 500 !important; color: #1a1612; }
    h1 { font-size: 2.6rem !important; letter-spacing: -0.02em; }
    h2 { font-size: 1.9rem !important; letter-spacing: -0.01em;
         border-top: 1px solid #2a241e; padding-top: 1rem; margin-top: 2rem; }
    h3 { font-size: 1.4rem !important; font-style: italic; }
    .kicker { font-family: 'JetBrains Mono', monospace; font-size: 0.7rem;
              letter-spacing: 0.2em; text-transform: uppercase; color: #7a1f1f; }
    [data-testid="stMetricValue"] { font-family: 'Cormorant Garamond', serif !important;
                                    font-size: 2rem !important; }
    .stDataFrame { font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 1px solid #2a241e; }
    .stTabs [data-baseweb="tab"] { font-family: 'JetBrains Mono', monospace;
                                   font-size: 0.75rem; letter-spacing: 0.1em;
                                   text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# ═════════════════════════════ Carga de datos ════════════════════════════════
df_sector = load_sector_tic()
df_especialistas = load_especialistas_tic()
df_ccaa = load_ccaa()
df_macro = load_epa_macro()
df_adopcion = load_adopcion_ia()

# ═════════════════════════════ Sidebar ═══════════════════════════════════════
with st.sidebar:
    st.markdown("<div class='kicker'>UNIE · Pilot vol. I</div>", unsafe_allow_html=True)
    st.markdown("# § Empleo Tec.")
    st.caption("Lectura crítica · EPA T1 2026")

    st.divider()

    st.markdown("### Filtros temporales")
    # Convertir a int nativo Python (los CSVs cargan numpy.int64, lo que rompe select_slider)
    años_disponibles = sorted(int(a) for a in set(df_macro["año"].unique()) | set(df_sector["año"].unique()))
    # Default: desde 2014 si está disponible, si no desde el primero
    año_default_inicio = 2014 if 2014 in años_disponibles else años_disponibles[0]
    año_min, año_max = st.select_slider(
        "Rango de años",
        options=años_disponibles,
        value=(año_default_inicio, años_disponibles[-1]),
        help="Rango disponible: 2008-2026 (macro EPA), 2014-2026 (sector TIC), 2011-2024 (ONTSI)",
    )

    st.markdown("### Métrica del empleo TIC")
    metrica = st.radio(
        "Definición operativa",
        ["Por rama (CNAE — sector TIC)", "Por ocupación (CNO — especialistas)"],
        help="Rama cuenta empleados de empresas tech; Ocupación cuenta profesionales tech estén donde estén.",
    )

    st.markdown("### Filtro geográfico")
    ccaa_seleccionadas = st.multiselect(
        "CCAA a destacar",
        options=df_ccaa["ccaa"].tolist(),
        default=["Madrid", "Cataluña", "C. Valenciana"],
    )

    st.divider()
    st.markdown("<div class='kicker'>Reproducibilidad</div>", unsafe_allow_html=True)
    st.caption("Datos: fuentes públicas (INE, ONTSI, Randstad). Código abierto. Listo para reemplazar CSVs por microdatos INEbase.")

# ═════════════════════════════ Header ════════════════════════════════════════
st.markdown("<div class='kicker'>Análisis · EPA T1 2026 · 28·IV·2026</div>",
            unsafe_allow_html=True)
st.markdown("# El millón *invisible*")
st.markdown("""
<p style='font-family: Cormorant Garamond, serif; font-size: 1.25rem;
font-style: italic; color: #4a4239; max-width: 720px; line-height: 1.5;'>
Lectura crítica del empleo tecnológico español a partir de la Encuesta de
Población Activa del primer trimestre de 2026. Sobre la divergencia entre
<em>rama</em> y <em>ocupación</em>, y sobre lo que la nueva CNAE-2025 hace
—y deshace— al medir.
</p>
""", unsafe_allow_html=True)

# Filtrar dataframe por año
df_sector_f = df_sector[(df_sector["año"] >= año_min) & (df_sector["año"] <= año_max)]
df_macro_f = df_macro[(df_macro["año"] >= año_min) & (df_macro["año"] <= año_max)]

# ═════════════════════════════ Tabs ══════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "I · Macro EPA", "II · Divergencia", "III · Subsectores",
    "IV · Geografía", "V · Metodología", "VI · Datos", "VII · Pipeline",
    "VIII · Diálogo Funcas"
])

# ──────────────────────────── TAB I: Macro ───────────────────────────────────
with tab1:
    st.markdown("## § I — Marco macroeconómico")

    col1, col2, col3, col4 = st.columns(4)
    último = df_macro.iloc[-1]
    anterior = df_macro.iloc[-2]
    año_atras = df_macro.iloc[-5]

    with col1:
        delta_trim = (último["ocupados_total_miles"] - anterior["ocupados_total_miles"]) * 1000
        st.metric("Ocupados totales",
                  f"{último['ocupados_total_miles']/1000:.2f} M",
                  f"{int(delta_trim):+,} trim.".replace(",", "."))
    with col2:
        delta_paro = último["tasa_paro"] - anterior["tasa_paro"]
        st.metric("Tasa de paro", f"{último['tasa_paro']:.2f}%",
                  f"{delta_paro:+.2f} pp", delta_color="inverse")
    with col3:
        delta_serv = (último["servicios_miles"] - anterior["servicios_miles"]) * 1000
        st.metric("Servicios", f"{último['servicios_miles']/1000:.2f} M",
                  f"{int(delta_serv):+,} trim.".replace(",", "."))
    with col4:
        delta_anual = (último["ocupados_total_miles"] - año_atras["ocupados_total_miles"]) * 1000
        st.metric("Empleo anual",
                  f"{int(delta_anual):+,}".replace(",", "."),
                  "vs. mismo trim. 2025")

    st.plotly_chart(macro_epa(df_macro_f), width="stretch")

    st.markdown("""
    <div style='background:#ebe6da; border-left: 3px solid #7a1f1f;
    padding: 1.5rem 1.8rem; margin: 1rem 0; font-family: Cormorant Garamond, serif;
    font-size: 1.05rem; line-height: 1.6;'>
    <strong>Lectura.</strong> El T1 2026 cierra la serie expansiva post-pandemia
    con una contracción trimestral de 170.300 ocupados, concentrada íntegramente
    en Servicios (-228.400). En desestacionalizado, sin embargo, la variación es
    de <strong>+0,43%</strong> trimestral: la contracción aparente es ruido
    estacional, no inflexión cíclica. Donde sí hay señal real es en la caída
    interanual del empleo temporal y en el descenso del trabajo por cuenta propia,
    el cajón donde habitan los autónomos tecnológicos.
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────── TAB II: Divergencia ────────────────────────────
with tab2:
    st.markdown("## § II — La divergencia *rama / ocupación*")

    div = calcular_divergencia(df_sector, df_especialistas)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sector TIC (rama CNAE)", f"{div['rama_sector_tic']:.0f}k",
                  "Empresas Sección J")
    with col2:
        st.metric("Especialistas TIC (ocupación)", f"{div['ocupacion_especialistas']:.0f}k",
                  "Profesionales CNO 25/35")
    with col3:
        st.metric("Diferencia",
                  f"{div['diferencia_absoluta']:.0f}k",
                  f"+{div['diferencia_pct']:.1f}% sobre rama",
                  delta_color="off")

    st.plotly_chart(
        divergencia_metricas(div["rama_sector_tic"], div["ocupacion_especialistas"]),
        width="stretch",
    )

    st.markdown(f"""
    <div style='background:#1a1612; color: #f4f1ea; padding: 1.8rem 2rem;
    margin: 1.5rem 0; position: relative;'>
    <h3 style='color: #f4f1ea !important; font-style: italic; margin-bottom: 0.8rem;'>
    El millón invisible</h3>
    <p style='font-size: 1rem; line-height: 1.7; color: rgba(244,241,234,0.9); max-width: 760px;'>
    {div['interpretacion']}
    </p>
    <p style='font-size: 0.95rem; line-height: 1.7; color: rgba(244,241,234,0.9);
    max-width: 760px; margin-top: 0.8rem;'>
    <strong>Implicación analítica:</strong> el "sector tech" como categoría operativa
    se está disolviendo. El empleo tecnológico es, cada vez más, una <em>función</em>
    distribuida en toda la economía, no una <em>rama</em>. Los KPIs convencionales
    de ecosistema digital están midiendo el envase, no el contenido.
    </p>
    </div>
    """, unsafe_allow_html=True)

    st.plotly_chart(serie_especialistas(df_especialistas), width="stretch")

# ──────────────────────────── TAB III: Subsectores ───────────────────────────
with tab3:
    st.markdown("## § III — Subsectores: *quién crece, quién encoge*")

    año_comp = st.selectbox("Año a comparar (vs. mismo trimestre del año anterior)",
                            [2024, 2025], index=1)
    trim_comp = st.selectbox("Trimestre", [1, 2, 3, 4], index=2)

    df_comp = comparar_subsectores(df_sector, año=año_comp, trim=trim_comp)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.plotly_chart(comparacion_subsectores(df_comp), width="stretch")
    with col2:
        st.markdown("#### Variaciones absolutas")
        for _, row in df_comp.iterrows():
            color = "#4a6c3f" if row["variacion_abs"] >= 0 else "#7a1f1f"
            st.markdown(f"""
            <div style='border-left: 3px solid {color}; padding: 0.5rem 0.8rem; margin: 0.5rem 0;'>
            <div style='font-family: JetBrains Mono, monospace; font-size: 0.7rem;
            letter-spacing: 0.1em; color: #8a8275;'>{row['subsector']}</div>
            <div style='font-family: Cormorant Garamond, serif; font-size: 1.6rem;
            color: {color};'>{row['variacion_abs']:+.1f}k</div>
            <div style='font-family: JetBrains Mono, monospace; font-size: 0.8rem;'>
            {row['variacion_pct']:+.1f}% interanual</div>
            </div>
            """, unsafe_allow_html=True)

    st.plotly_chart(serie_sector_tic(df_sector_f), width="stretch")

    st.markdown("""
    <div style='background:#ebe6da; border-left: 3px solid #b8860b;
    padding: 1.5rem 1.8rem; margin: 1rem 0; font-family: Cormorant Garamond, serif;
    font-size: 1.05rem; line-height: 1.6;'>
    <strong>Nota interpretativa.</strong> El desplome de Telecomunicaciones (–15,4%
    interanual T3 2025) no refleja crisis sectorial sino consumación del modelo de
    externalización: las grandes operadoras (Telefónica, Orange, Vodafone) han
    traspasado funciones técnicas a integradores y consultoras, lo que figura como
    <em>caída</em> en CNAE 61 y <em>subida parcial</em> en CNAE 62. La cifra agregada
    del sector (–2,2%) encubre esta recomposición interna.
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────── TAB IV: Geografía ──────────────────────────────
with tab4:
    st.markdown("## § IV — Concentración *geográfica*")

    hhi_data = indice_herfindahl(df_ccaa)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Top 2 (Madrid + Cataluña)", f"{hhi_data['top2_pct']:.1f}%",
                  "del empleo TIC nacional")
    with col2:
        st.metric("Top 4 CCAA", f"{hhi_data['top4_pct']:.1f}%",
                  "concentración de cuatro polos")
    with col3:
        st.metric("Índice HHI", f"{hhi_data['hhi']:.0f}",
                  hhi_data["interpretacion_hhi"], delta_color="off")

    df_destacar = df_ccaa.copy()
    if ccaa_seleccionadas:
        df_destacar = df_destacar[df_destacar["ccaa"].isin(ccaa_seleccionadas)]

    if not df_destacar.empty and len(df_destacar) < len(df_ccaa):
        st.markdown(f"#### CCAA seleccionadas: {', '.join(ccaa_seleccionadas)}")
        for _, row in df_destacar.iterrows():
            st.markdown(f"""
            **{row['ccaa']}** — {row['empleo_tic_miles']:.0f}k ocupados ·
            {row['pct_sobre_empleo_ccaa']:.1f}% del empleo de la CCAA ·
            {row['pct_sobre_total_tic']:.1f}% del empleo TIC nacional
            """)

    st.plotly_chart(mapa_concentracion(df_ccaa), width="stretch")

    st.markdown("""
    <div style='background:#1a1612; color: #f4f1ea; padding: 1.8rem 2rem;
    margin: 1.5rem 0;'>
    <h3 style='color: #f4f1ea !important; font-style: italic;'>Implicación política</h3>
    <p style='font-size: 1rem; line-height: 1.7; color: rgba(244,241,234,0.9); max-width: 760px;'>
    El discurso oficial de la "España conectada" se vuelve frágil cuando el 60% del
    talento tecnológico vive en dos polos. La transformación digital, lejos de ser
    deslocalizadora, ha resultado profundamente metropolitana. Cualquier shock
    localizado —fiscal, inmobiliario, migratorio— amenaza la capacidad de
    transformación digital del país.
    </p>
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────── TAB V: Metodología ─────────────────────────────
with tab5:
    st.markdown("## § V — Ruptura *CNAE-2025*")

    st.markdown("""
    <div style='background:#1a1612; color: #f4f1ea; padding: 2rem 2rem;'>
    <h3 style='color:#f4f1ea !important; font-style: italic;'>Lo que se reescribe cuando se reescribe la clasificación</h3>
    <p style='color: rgba(244,241,234,0.85); font-size: 0.95rem; line-height: 1.7;'>
    A partir del T1 2026 la EPA codifica simultáneamente con CNAE-2009 y CNAE-2025
    (Reglamento Delegado UE 2023/137). Durante los cuatro trimestres de 2026 conviven
    ambas. Desde 2027, sólo la nueva. <strong>Toda comparación interanual T1 2027 vs.
    T1 2026 sin matriz de transición será espuria.</strong>
    </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Ramas que cambian de hogar estadístico")

    transiciones = pd.DataFrame([
        {"CNAE-2009": "Reparación e instalación de maquinaria y equipo",
         "Pertenecía a": "Industria (íntegramente)",
         "CNAE-2025": "Industria + Agricultura + Servicios"},
        {"CNAE-2009": "Construcción de edificios, ingeniería civil, especializada",
         "Pertenecía a": "Construcción (íntegramente)",
         "CNAE-2025": "Construcción + Servicios"},
        {"CNAE-2009": "Almacenamiento, otras prof./científ./técn., admin. auxiliares",
         "Pertenecía a": "Servicios (íntegramente)",
         "CNAE-2025": "Servicios + Industria + Construcción"},
    ])
    st.dataframe(transiciones, width="stretch", hide_index=True)

    st.markdown("""
    <div style='background:#ebe6da; border-left: 3px solid #7a1f1f;
    padding: 1.5rem 1.8rem; margin: 1.5rem 0; font-family: Cormorant Garamond, serif;
    font-size: 1.05rem; line-height: 1.6;'>
    <strong>Tesis para discusión.</strong> Las ramas más afectadas por la
    automatización —reparación de maquinaria, almacenamiento (con su Amazon-economy
    embebida), actividades técnicas auxiliares— son precisamente las que cambian
    de hogar estadístico. La frontera misma entre "trabajo industrial" y "trabajo
    de servicios" deja de medir lo que medía. La estadística pública es ya un
    actor del fenómeno que mide.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Procedencia de los datos")
    provenance = get_data_provenance()
    for key, meta in provenance.items():
        with st.expander(f"📋 {key}"):
            for k, v in meta.items():
                st.markdown(f"**{k.replace('_', ' ').title()}:** {v}")

# ──────────────────────────── TAB VI: Datos ──────────────────────────────────
with tab6:
    st.markdown("## § VI — Datos *crudos* y descarga")

    st.caption("Cuatro tablas reproducibles. Reemplazar CSVs en /data por microdatos INEbase para producción.")

    dataset = st.selectbox("Conjunto de datos", [
        "Sector TIC trimestral (rama CNAE)",
        "Especialistas TIC anual (ocupación CNO)",
        "Distribución por CCAA",
        "Macro EPA total",
    ])

    if dataset == "Sector TIC trimestral (rama CNAE)":
        df_show = df_sector
    elif dataset == "Especialistas TIC anual (ocupación CNO)":
        df_show = df_especialistas
    elif dataset == "Distribución por CCAA":
        df_show = df_ccaa
    else:
        df_show = df_macro

    st.dataframe(df_show, width="stretch", height=420)

    col1, col2 = st.columns(2)
    with col1:
        csv = df_show.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Descargar CSV",
            data=csv,
            file_name=f"{dataset.lower().replace(' ', '_')}.csv",
            mime="text/csv",
            width="stretch",
        )
    with col2:
        # Excel descarga
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_show.to_excel(writer, index=False, sheet_name="datos")
        st.download_button(
            "⬇ Descargar Excel",
            data=buffer.getvalue(),
            file_name=f"{dataset.lower().replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
        )

    st.divider()

    st.markdown("### Bundle completo")
    st.caption("Todas las tablas en un solo Excel con cuatro hojas, listo para anexo de paper.")

    bundle = BytesIO()
    with pd.ExcelWriter(bundle, engine="openpyxl") as writer:
        df_sector.to_excel(writer, index=False, sheet_name="sector_TIC_trim")
        df_especialistas.to_excel(writer, index=False, sheet_name="especialistas_anual")
        df_ccaa.to_excel(writer, index=False, sheet_name="ccaa")
        df_macro.to_excel(writer, index=False, sheet_name="macro_EPA")
    st.download_button(
        "⬇ Descargar bundle completo (XLSX, 4 hojas)",
        data=bundle.getvalue(),
        file_name="empleo_tic_bundle_completo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch",
    )

# ──────────────────────────── TAB VII: Pipeline ──────────────────────────────
with tab7:
    st.markdown("## § VII — Estado del *pipeline* de actualización")

    st.markdown("""
    <div style='font-family: Cormorant Garamond, serif; font-size: 1.15rem;
    line-height: 1.5; font-style: italic; color: #4a4239; max-width: 720px;
    margin-bottom: 1.5rem;'>
    El MVP se actualiza automáticamente al ritmo de las publicaciones oficiales
    del INE. Esta vista muestra qué fuente está fresca, cuál vencida, y cuál
    requiere intervención manual.
    </div>
    """, unsafe_allow_html=True)

    # Estado de fuentes
    st.markdown("### Estado de las fuentes")
    df_pipeline = get_pipeline_status()
    st.dataframe(df_pipeline, width="stretch", hide_index=True)

    # KPIs de frescura
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        n_fresh = (df_pipeline['estado'].str.contains('actualizado')).sum()
        st.metric("Fuentes frescas", f"{n_fresh}/{len(df_pipeline)}")
    with col2:
        n_due = df_pipeline['estado'].str.contains('pendiente').sum()
        st.metric("Pendientes", str(n_due))
    with col3:
        n_overdue = df_pipeline['estado'].str.contains('retrasado').sum()
        st.metric("Retrasadas", str(n_overdue), delta_color="inverse")
    with col4:
        n_manual = df_pipeline['estado'].str.contains('manual').sum()
        st.metric("Acción manual", str(n_manual))

    st.divider()

    # Calendario INE
    st.markdown("### Calendario de publicaciones EPA · INE")
    año_cal = st.selectbox("Año", [2025, 2026, 2027], index=1)
    df_cal = get_publication_calendar(año_cal)
    st.dataframe(df_cal, width="stretch", hide_index=True)

    st.markdown("""
    <div style='background:#ebe6da; border-left: 3px solid #b8860b;
    padding: 1.2rem 1.5rem; margin: 1rem 0; font-family: Cormorant Garamond, serif;
    font-size: 1rem; line-height: 1.6;'>
    <strong>Nota operativa.</strong> El INE publica la EPA el último martes
    o jueves del mes posterior al cierre del trimestre. El pipeline ejecuta
    el día 29 a las 06:00 UTC para garantizar disponibilidad. La acción
    GitHub abre automáticamente un <em>issue</em> con los cambios detectados
    y commitea los CSVs actualizados.
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Cambios desde último snapshot
    st.markdown("### Detección de cambios")
    changes = detect_changes_since_last_snapshot()

    if changes.get("status") == "no_snapshots":
        st.info("Aún no hay snapshots. Pulsa 'Crear snapshot' para iniciar histórico.")
    else:
        st.code(json.dumps(changes, indent=2, ensure_ascii=False), language="json")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("📸 Crear snapshot manual", width="stretch"):
            label = f"manual_{datetime.now().strftime('%Y%m%d_%H%M')}"
            try:
                path = take_snapshot(label=label.split('_', 1)[1])
                st.success(f"Snapshot creado: {path.name}")
            except Exception as e:
                st.error(f"Error: {e}")
    with col_b:
        if st.button("🔄 Refrescar estado", width="stretch"):
            st.cache_data.clear()
            st.rerun()

    st.divider()

    # Niveles de automatización
    st.markdown("### Tres niveles de automatización implementados")
    st.markdown("""
    <div style='background:#1a1612; color: #f4f1ea; padding: 2rem 2rem;
    margin: 1.5rem 0;'>
    <h3 style='color:#f4f1ea !important; font-style: italic; margin-bottom: 1rem;'>
    ¿Qué se automatiza y qué no</h3>

    <p style='color: rgba(244,241,234,0.9); margin-bottom: 1rem; line-height: 1.6;'>
    <strong style='color:#b8860b;'>Nivel 1 — GitHub Actions programado.</strong>
    El día 29 de cada mes de publicación EPA (enero, abril, julio, octubre)
    se ejecuta automáticamente el cliente del API INE Tempus 3.0, descarga
    las series, las commitea al repositorio y abre un issue notificando
    cambios. <em>Reproducible, gratuito, sin servidor propio.</em>
    </p>

    <p style='color: rgba(244,241,234,0.9); margin-bottom: 1rem; line-height: 1.6;'>
    <strong style='color:#b8860b;'>Nivel 2 — Streamlit on-demand.</strong>
    El usuario puede pulsar "Refrescar estado" en esta tab para forzar una
    recarga. Útil cuando el INE publica fuera del calendario oficial.
    </p>

    <p style='color: rgba(244,241,234,0.9); line-height: 1.6;'>
    <strong style='color:#7a1f1f;'>Lo que NO se automatiza.</strong>
    ONTSI publica edición anual sin API; requiere descarga de PDF y
    extracción manual del dato. Randstad Research no tiene API estable.
    El pipeline notifica cuando estas fuentes vencen (>365 días para ONTSI),
    pero la actualización debe hacerse a mano. La honestidad metodológica
    exige distinguir lo automatizable de lo no automatizable.
    </p>
    </div>
    """, unsafe_allow_html=True)

    # Aviso CNAE-2025
    st.markdown("""
    <div style='background:#7a1f1f; color: #f4f1ea; padding: 1.5rem 1.8rem;
    margin: 1.5rem 0;'>
    <h3 style='color:#f4f1ea !important; font-style: italic;'>
    ⚠ Atención: ruptura CNAE-2025 en curso</h3>
    <p style='color: rgba(244,241,234,0.95); line-height: 1.6;'>
    La antigua Sección J (Información y Comunicaciones) de CNAE-2009 se
    divide en CNAE-2025 en <strong>dos secciones</strong>: J (edición,
    radiodifusión, contenidos) y K (telecomunicaciones, programación,
    consultoría TI). El sector tecnológico ya no se localiza con una sola
    letra.
    </p>
    <p style='color: rgba(244,241,234,0.95); line-height: 1.6; margin-top: 0.6rem;'>
    A partir de 2027, las series CNAE-2009 dejan de publicarse. La tabla
    INE 4128 está deprecada. El pipeline tendrá que migrar a las nuevas
    tablas CNAE-2025 cuando estén disponibles, y será necesario reescribir
    las series históricas con la matriz de transición que publica el INE.
    Esto no es una limitación técnica del MVP: es el objeto teórico que
    el MVP estudia, materializado.
    </p>
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────── TAB VIII: Diálogo Funcas ───────────────────────
with tab8:
    st.markdown("## § VIII — Diálogo crítico con *Funcas* (2026)")

    st.markdown("""
    <div style='font-family: Cormorant Garamond, serif; font-size: 1.15rem;
    line-height: 1.5; font-style: italic; color: #4a4239; max-width: 720px;
    margin-bottom: 1.5rem;'>
    El informe Rodríguez-Fernández (Funcas, abril 2026) estima una destrucción
    bruta de entre 1,7 y 2,3 millones de empleos en España por efecto de la IA
    a horizonte 2025-2035. Esta sección dialoga críticamente con esas estimaciones
    desde el ángulo del MVP: no compite con ellas, las problematiza.
    </div>
    """, unsafe_allow_html=True)

    # Tres escenarios de Funcas
    st.markdown("### Los tres escenarios de Funcas")
    df_escenarios = pd.DataFrame({
        "Escenario": ["Optimista", "Central", "Pesimista"],
        "δ_sust (sustitución)": [0.10, 0.22, 0.35],
        "γ (automatización 10y)": [0.40, 0.65, 0.85],
        "ρ (adopción empresarial)": [0.12, 0.21, 0.40],
        "Destrucción bruta (millones)": [0.7, 2.0, 3.5],
        "Creación (millones)": [1.61, 1.61, 1.61],
        "Pérdida neta (millones)": [-0.91, 0.39, 1.89],
    })
    st.dataframe(df_escenarios, width="stretch", hide_index=True)

    st.caption("Fuente: Rodríguez-Fernández (Funcas, 2026). La creación es exógena al modelo y proviene de Randstad/COIT 2024.")

    # Adopción IA empresarial real
    st.markdown("### Velocidad real de adopción · serie ETICCE INE")

    col1, col2 = st.columns([2, 1])
    with col1:
        import plotly.graph_objects as go
        fig_adop = go.Figure()
        fig_adop.add_trace(go.Scatter(
            x=df_adopcion["año"], y=df_adopcion["pct_empresas_uso_ia"],
            mode="lines+markers", name="Total empresas (≥10 emp.)",
            line=dict(color="#7a1f1f", width=3.5),
            marker=dict(size=11),
        ))
        fig_adop.add_trace(go.Scatter(
            x=df_adopcion["año"], y=df_adopcion["pct_sector_tic"],
            mode="lines+markers", name="Sector TIC",
            line=dict(color="#1a1612", width=2.5, dash="dot"),
            marker=dict(size=8),
        ))
        fig_adop.add_trace(go.Scatter(
            x=df_adopcion["año"], y=df_adopcion["pct_servicios"],
            mode="lines+markers", name="Servicios",
            line=dict(color="#b8860b", width=2),
        ))
        fig_adop.add_trace(go.Scatter(
            x=df_adopcion["año"], y=df_adopcion["pct_industria"],
            mode="lines+markers", name="Industria",
            line=dict(color="#4a6c3f", width=2),
        ))
        fig_adop.update_layout(
            paper_bgcolor="#f4f1ea", plot_bgcolor="#f4f1ea",
            title="Adopción de IA por sector · % de empresas que la usan",
            yaxis_title="% empresas",
            xaxis_title="Año",
            height=400,
            font=dict(family="Inter, sans-serif", size=12, color="#1a1612"),
            legend=dict(orientation="h", y=1.08, x=0),
        )
        st.plotly_chart(fig_adop, width="stretch")
    with col2:
        último = df_adopcion.iloc[-1]
        primero = df_adopcion.iloc[0]
        delta_4y = último["pct_empresas_uso_ia"] - primero["pct_empresas_uso_ia"]
        st.metric("Adopción 2025", f"{último['pct_empresas_uso_ia']:.1f}%",
                  f"+{delta_4y:.1f}pp en 4 años")
        st.metric("Sector TIC", f"{último['pct_sector_tic']:.1f}%",
                  "lidera adopción")
        st.metric("Brecha sector TIC vs total",
                  f"{último['pct_sector_tic'] - último['pct_empresas_uso_ia']:.1f}pp",
                  "hipótesis del millón invisible reforzada")

    st.markdown("""
    <div style='background:#ebe6da; border-left: 3px solid #7a1f1f;
    padding: 1.5rem 1.8rem; margin: 1rem 0; font-family: Cormorant Garamond, serif;
    font-size: 1.05rem; line-height: 1.6;'>
    <strong>Crítica metodológica.</strong> Funcas usa ρ=0,21 como parámetro fijo
    de adopción para todo el horizonte 2025-2035. La serie real de ETICCE muestra
    que la adopción <em>se está acelerando</em> a +4,3pp/año. Si esa tasa se
    mantuviera, en 2035 la adopción rondaría el 60-70% (no el 21% del modelo
    central). Esto significaría que el escenario "central" de Funcas
    es probablemente <strong>sustancialmente conservador</strong> en términos
    del parámetro ρ, lo que empuja la verdadera estimación hacia el escenario
    pesimista.
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Las cuatro tesis críticas
    st.markdown("### Cuatro tesis críticas del MVP al modelo Funcas")

    st.markdown("""
    <div style='background:#1a1612; color: #f4f1ea; padding: 2rem 2rem;
    margin: 1.5rem 0;'>
    <p style='color:#b8860b; font-family: JetBrains Mono, monospace;
    font-size: 0.75rem; letter-spacing: 0.15em; margin-bottom: 1rem;'>
    TESIS 1 — INCERTIDUMBRE NO PROPAGADA</p>
    <p style='color: rgba(244,241,234,0.92); line-height: 1.6; margin-bottom: 1.5rem;'>
    El modelo encadena <strong>cinco parámetros multiplicativos</strong>
    (φ · AIOE · δ · γ · ρ), pero presenta sólo tres puntos discretos
    (optimista/central/pesimista) en lugar de propagar la incertidumbre
    conjunta vía Monte Carlo. El verdadero intervalo de confianza es
    probablemente <strong>más amplio</strong> que el rango 700k-3.500k reportado.
    </p>

    <p style='color:#b8860b; font-family: JetBrains Mono, monospace;
    font-size: 0.75rem; letter-spacing: 0.15em; margin-bottom: 1rem;'>
    TESIS 2 — AIOE COMO CATEGORÍA NO PROBLEMATIZADA</p>
    <p style='color: rgba(244,241,234,0.92); line-height: 1.6; margin-bottom: 1.5rem;'>
    Felten et al. (2023) construyen AIOE sobre O*NET, que refleja el mercado
    laboral <strong>estadounidense de los 2010s</strong>. La doble correspondencia
    SOC→ISCO→CNO opera sobre categorías que están siendo redibujadas
    administrativamente (CNAE-2025). El parámetro φ=0,82 que ajusta
    esta pérdida es un <strong>supuesto sin calibración empírica</strong>,
    como el propio informe reconoce.
    </p>

    <p style='color:#b8860b; font-family: JetBrains Mono, monospace;
    font-size: 0.75rem; letter-spacing: 0.15em; margin-bottom: 1rem;'>
    TESIS 3 — EL "MILLÓN INVISIBLE" SESGA EL MODELO</p>
    <p style='color: rgba(244,241,234,0.92); line-height: 1.6; margin-bottom: 1.5rem;'>
    Si el 55% de los profesionales TIC trabaja fuera del sector TIC (ver Tab II),
    el AIOE-CNO subestima sistemáticamente la exposición real del trabajo
    tecnológico distribuido. Un programador en un banco se contabiliza como
    "técnico financiero", no como profesional TIC. La adopción 58,7% del
    sector TIC <em>vs.</em> 21,1% media empresarial sugiere que el verdadero
    foco de disrupción es donde el AIOE-CNO no mira.
    </p>

    <p style='color:#b8860b; font-family: JetBrains Mono, monospace;
    font-size: 0.75rem; letter-spacing: 0.15em; margin-bottom: 1rem;'>
    TESIS 4 — LA PERFORMATIVIDAD COMO OBJETO TEÓRICO</p>
    <p style='color: rgba(244,241,234,0.92); line-height: 1.6;'>
    Funcas no problematiza filosóficamente las categorías sobre las que opera.
    Pero la transición CNAE-2009→2025 ocurre simultáneamente con el despliegue
    de IA: <strong>la administración estadística europea está reescribiendo
    las categorías del trabajo en el momento exacto en que la IA reescribe
    el trabajo mismo</strong>. Esto no es una coincidencia: es el objeto teórico
    central que el marco de la <em>Causa Segunda</em> permite formular.
    </p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Predicciones falsables
    st.markdown("### Lo que el MVP puede falsar del modelo Funcas")

    st.markdown("""
    El modelo Funcas hace tres predicciones contrastables con datos trimestrales:

    1. **Caída sostenida en grupo CNO 2** (técnicos científicos): el MVP ya observa
       declive significativo en CNAE 61 (Telecomunicaciones, Z=-1,55) que está
       dentro del grupo 2. Predicción **parcialmente confirmada**.

    2. **Crecimiento en grupo CNO 5** (servicios) por complementariedad: el MVP
       muestra Servicios T1 2026 con –228k ocupados pero +254k anual.
       **Pendiente de validar** con desglose por subsector.

    3. **Aceleración del gap rama/ocupación** si el modelo central acierta:
       el MVP cuantifica gap creciente +28k/año (Mann-Kendall p=0,006).
       Predicción **confirmada empíricamente**.
    """)

    st.markdown("""
    <div style='background:#ebe6da; border-left: 3px solid #b8860b;
    padding: 1.2rem 1.5rem; margin: 1rem 0; font-family: Cormorant Garamond, serif;
    font-size: 1rem; line-height: 1.6;'>
    <strong>Próximo paso de investigación.</strong> Convertir el MVP en observatorio
    de validación externa de modelos prospectivos. Cada trimestre que pasa, el
    pipeline automático compara las predicciones de Funcas (y otros modelos
    similares) con la evolución observada. Esta función no es una alternativa al
    informe Funcas: es su contraparte empírica trimestral.
    </div>
    """, unsafe_allow_html=True)

# ═════════════════════════════ Footer ════════════════════════════════════════
st.divider()
st.markdown("""
<div style='display: flex; justify-content: space-between; flex-wrap: wrap;
font-family: JetBrains Mono, monospace; font-size: 0.7rem; letter-spacing: 0.05em;
color: #4a4239; padding: 1rem 0;'>
<div>MVP académico v0.1 · UNIE Universidad · Cátedra de Filosofía y Tecnología</div>
<div>José Fernández Tamames · jtamames@unie.es</div>
<div>Generado el 29·IV·2026</div>
</div>
""", unsafe_allow_html=True)
