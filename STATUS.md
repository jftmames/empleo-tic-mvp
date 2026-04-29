# Estado del proyecto · v1.0

*Empleo Tecnológico en España — MVP académico · 29-IV-2026*

---

## Resumen ejecutivo

Proyecto cerrado a v1.0 publicable. Cubre el ciclo académico completo:
**fuentes públicas → análisis estadístico → divulgación interactiva → manuscrito**.

---

## Lo que está hecho (v1.0)

### Infraestructura técnica

| Componente | Estado | Notas |
|---|---|---|
| App Streamlit (7 tabs) | ✅ | Datos, divergencia, subsectores, geografía, metodología, descargas, pipeline |
| Análisis estadístico (Jupyter) | ✅ | Mann-Kendall, STL, Friedman/Wilcoxon · ejecutado limpio |
| Cliente API INE Tempus 3.0 | ✅ | Descarga vía URL pública, sin autenticación |
| Pipeline actualización automática | ✅ | GitHub Actions cron + detección de cambios |
| Parser microdatos EPA | ✅ | Esquema CNAE-2009 + CNAE-2025 (doble codificación 2026) |
| Tests pytest | ✅ | 20/21 passing + 1 xfail documentando heterogeneidad |
| Dockerfile + docker-compose | ✅ | Streamlit + Jupyter ambos containerizados |
| CITATION.cff + LICENSE | ✅ | Listo para Zenodo |
| Manuscrito LaTeX | ✅ | Borrador completo, compilable, ~12 páginas |

### Hallazgos académicos validados

| Hallazgo | Método | Resultado |
|---|---|---|
| Tendencia creciente del sector | Mann-Kendall (Hamed-Rao) | $Z=5{,}74$, $p<0{,}001$ |
| Estacionalidad cuasi-nula | STL | $\text{Var}(S)/\text{Var}(Y) < 0{,}01$ |
| Subsectores heterogéneos | Friedman + Wilcoxon | Act. inf. $\neq$ Telecom ($p<10^{-4}$) |
| Gap rama/ocupación creciente | MK sobre serie del gap | +28 mil personas/año |
| Concentración geográfica | Índice HHI | 1.684 (moderada-alta) |

---

## Lo que NO está hecho (con justificación)

### Decididamente fuera de alcance

| Idea descartada | Por qué |
|---|---|
| Mapa coroplético geo-espacial | Estética, no aporta ciencia. Las CCAA están en tabla. |
| Proyecciones predictivas | Requiere supuestos teóricos no justificados aún |
| API REST propia | Innecesaria para herramienta académica |
| Dashboard móvil específico | Público objetivo no es móvil |
| Scraping de Randstad | Frágil; introduciría ruido invisible |
| Comparativa Eurostat completa | Costoso de mantener; mejor en v2.0 |

### Pospuesto a v1.1 (si hay demanda)

- [ ] Pipeline de auto-exportación notebook → figuras del paper
- [ ] CI/CD: ejecutar pytest en cada push (GitHub Actions)
- [ ] Comparativa NACE Rev. 2.1 con Eurostat (subset reducido)
- [ ] Dashboard derivado para presentación a Rectorado UNIE

### Pospuesto a v2.0 (si el proyecto se consolida)

- [ ] Series 2002-2026 reconstruidas con matriz de transición CNAE
- [ ] Análisis municipal (no solo CCAA) para algunas comunidades
- [ ] Cruce con Seguridad Social (afiliación al RGSS)
- [ ] Dataset de validación externa con ofertas LinkedIn / Infojobs

---

## Limitaciones honestas (declaradas en el paper y README)

1. **Datos 2024Q3-2026Q1 a nivel subsector** vienen de Randstad Research, no
   microdatos EPA brutos. El parser de microdatos está implementado para
   sustituir esto cuando el ZIP del INE esté accesible en el entorno de ejecución.
2. **CCAA fuera del top 4** son estimaciones; requieren validación con tabla
   provincial EPA específica.
3. **Especialistas TIC trimestrales** no disponibles en ONTSI; sólo serie anual.
4. **Test de coherencia de subsectores** marcado como `xfail` documentando
   heterogeneidad metodológica entre fuentes (Randstad vs. EPA).

Estas limitaciones están explícitas tanto en el código (docstrings) como en
el manuscrito (sección 2.1) y en el README. La honestidad metodológica forma
parte del marco teórico del proyecto.

---

## Métricas del proyecto

```
Líneas de código Python:           ~1.500
Líneas LaTeX (manuscrito):           ~250
Líneas Markdown (documentación):     ~700
Tests automatizados:                   21
Cobertura conceptual:        EPA + ONTSI + microdatos + Eurostat
Dependencias externas:                 11 (todas open source)
Tiempo de despliegue local:        < 5 min
```

---

## Indicadores de calidad académica

- ✅ Reproducibilidad total (Docker + requirements pinned)
- ✅ Datos abiertos (todos los CSVs incluidos)
- ✅ Código abierto (MIT)
- ✅ Documentación bilingüe (código en inglés, prosa en español)
- ✅ Citable (CITATION.cff + DOI Zenodo posible)
- ✅ Tests automatizados (pytest)
- ✅ Análisis estadístico formal (no solo descriptivo)
- ✅ Discusión filosófica articulada con marco teórico propio
- ✅ Implicaciones de política pública explicitadas
- ✅ Limitaciones declaradas

---

## Próximos pasos recomendados (orden sugerido)

1. **Despliegue inmediato**: GitHub público + Streamlit Community Cloud + Zenodo
2. **Comunicación**: comunicar al editor de *Ratio & Machina* y a Susana Checa
3. **Solicitud de DOI**: Zenodo automático tras release v1.0
4. **Submission**: revisar el paper LaTeX y enviar a la revista
5. **Iteración**: incorporar feedback de Susana Checa y revisores

---

*Documento generado el 29 de abril de 2026 · v1.0 final*
