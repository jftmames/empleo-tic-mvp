# Paper: "El millón invisible"

Borrador del manuscrito para *Ratio & Machina* vol. I, núm. 1.

## Compilación

### Opción A: Overleaf (recomendado)

1. Crea proyecto nuevo en [overleaf.com](https://www.overleaf.com)
2. Sube `main.tex`
3. Compila con XeLaTeX (necesario para `ebgaramond`)

### Opción B: Local

```bash
cd paper/
xelatex main.tex
bibtex main         # si añades referencias BibTeX en archivo separado
xelatex main.tex
xelatex main.tex    # segunda pasada para resolver referencias cruzadas
```

Output: `main.pdf` (~12-14 páginas).

## Compilación con docker (totalmente reproducible)

```bash
docker run --rm -v "$PWD":/workdir texlive/texlive:latest \
  bash -c "cd /workdir && xelatex main.tex && xelatex main.tex"
```

## Estructura

- `main.tex` — manuscrito completo IMRAD
- (Pendiente) `figures/` — figuras exportadas del notebook (PDF/PNG)
- (Pendiente) `tables/` — tablas exportadas del notebook (TEX/CSV)
- (Pendiente) `references.bib` — bibliografía BibTeX

## Para v1.1 — Pipeline auto-figuras

El notebook `notebooks/analisis_formal.ipynb` puede generar las figuras
para el paper directamente. Añadir al notebook:

```python
# Al final del notebook
import os
os.makedirs('../paper/figures', exist_ok=True)
fig.savefig('../paper/figures/divergencia.pdf', dpi=300, bbox_inches='tight')
fig.savefig('../paper/figures/stl_decomposition.pdf', dpi=300, bbox_inches='tight')
```

Y en `main.tex`:

```latex
\begin{figure}[h]
\includegraphics[width=\linewidth]{figures/divergencia.pdf}
\caption{Evolución de la divergencia rama--ocupación.}
\end{figure}
```

## Destinos de publicación candidatos

1. **Ratio & Machina** (revista propia) — primera opción natural
2. **Revista Internacional de Sociología (RIS)** — CSIC, indexada en SCOPUS
3. **PhilPapers / PhilArchive** — preprint inmediato, acceso abierto
4. **SSRN — Spain & Portugal Network** — visibilidad internacional
5. **REIS** (Revista Española de Investigaciones Sociológicas) — para versión más empírica

## Publicación con DOI

Una vez publicado el paper:

1. Subir versión final a Zenodo desde el repositorio GitHub
2. Zenodo genera DOI automáticamente
3. Actualizar `CITATION.cff` con el DOI
4. Comunicar el DOI al editor de *Ratio & Machina*

---
*Última revisión: 29-IV-2026*
