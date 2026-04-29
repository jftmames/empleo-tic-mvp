# Guía de despliegue · v1.0 · Web-first

*Empleo Tecnológico MVP — del ZIP a la publicación, sin instalar nada local*

---

## Resumen

Cinco fases, todas vía navegador:

1. **Preparación** (5 min) · descomprimir el ZIP
2. **GitHub** (15 min) · crear repo y subir el código
3. **Streamlit Cloud** (10 min) · publicar la app pública
4. **Zenodo** (10 min) · obtener DOI académico
5. **Overleaf** (15 min) · compilar el paper

Total: **~ 1 hora**. Sin instalar Python, sin terminal, sin Docker.

> **Tip ergonómico**: usa Chrome o Edge. Algunas funciones de GitHub web
> (subir carpetas) no funcionan bien en Safari/Firefox antiguos.

---

## Fase 1: Preparación

Esto sí lo haces en tu ordenador, pero sin instalar nada.

### Paso 1.1 — Descargar el ZIP

Has descargado `empleo_tic_mvp_v1.0.zip` desde Claude.

### Paso 1.2 — Descomprimir

- **Windows**: clic derecho sobre el ZIP → "Extraer todo" → "Extraer"
- **Mac**: doble clic sobre el ZIP

Te queda una carpeta `empleo_tic_mvp/` con todo dentro. Déjala en el escritorio
o en Documentos, donde la encuentres fácil.

✅ **Hito 1 completado**: tienes la carpeta lista para subir.

---

## Fase 2: GitHub web

### Paso 2.1 — Crear cuenta GitHub

Si ya tienes cuenta, salta al paso 2.2.

1. Ve a [github.com/signup](https://github.com/signup)
2. Email recomendado: `jtamames@unie.es` (o el que uses para Zenodo después)
3. Username sugerido: `jtamames` (corto y profesional para citas académicas)
4. Crea contraseña fuerte
5. Verifica el email
6. Salta los pasos opcionales de bienvenida

### Paso 2.2 — Crear repositorio nuevo

1. En la esquina superior derecha de GitHub: **+ → New repository**
2. Rellena el formulario:
   - **Repository name**: `empleo-tic-mvp`
   - **Description**: `Análisis crítico del empleo tecnológico español a partir de la EPA`
   - **Public** (necesario para Streamlit Cloud y Zenodo gratuitos)
   - ❌ **NO marques** "Add a README file"
   - ❌ **NO marques** "Add .gitignore"
   - ❌ **NO marques** "Choose a license"

   *(Importante: dejar el repo vacío porque ya traemos todos los archivos.)*

3. Click **Create repository**

Te llevará a una página con instrucciones de "Quick setup". Ignóralas.

### Paso 2.3 — Subir todos los archivos vía drag & drop

Desde la página de tu repo recién creado:

1. Verás un mensaje "Quick setup" con varias opciones. Busca el enlace
   **"uploading an existing file"** (suele estar en azul, mitad de la página).

2. Click en **"uploading an existing file"**.

3. Llegas a la pantalla de subida. Verás un área grande que dice:
   **"Drag files here to add them to your repository"**

4. **En tu ordenador**, abre la carpeta `empleo_tic_mvp/` que descomprimiste.

5. **Selecciona TODO el contenido de la carpeta** (Ctrl+A en Windows / Cmd+A en Mac).

   *Importante: no la carpeta entera, sino su contenido. Es decir, dentro
   de `empleo_tic_mvp/` selecciona los archivos y subcarpetas que ves
   (`app.py`, `data/`, `modules/`, `notebooks/`, etc.).*

6. **Arrastra todo** al área de drag & drop de GitHub.

7. GitHub procesa los archivos. **Conserva la estructura de carpetas** (lo verás
   indicado con `data/sector_tic_trimestral.csv`, `modules/app.py`, etc.).

   > ⚠ Si algún archivo no aparece, repite el drag & drop sólo con los que faltan.
   > No es problema hacerlo en varias tandas.

8. Mientras se procesan, baja a "Commit changes":
   - **Commit message**: `v1.0 inicial · MVP académico empleo tecnológico`
   - Mantén marcado: **Commit directly to the main branch**

9. Click **Commit changes**.

10. Espera 30-60 segundos. Te lleva de vuelta a la página principal del repo.

### Paso 2.4 — Verificar que está todo

Deberías ver, en la página principal del repo:

```
empleo-tic-mvp/
├── .github/
├── data/
├── modules/
├── notebooks/
├── paper/
├── tests/
├── .dockerignore
├── CITATION.cff
├── DEPLOYMENT.md
├── Dockerfile
├── LICENSE
├── README.md
├── STATUS.md
├── app.py
├── docker-compose.yml
└── requirements.txt
```

Si falta algo, repite el drag & drop con los archivos que falten.

> 💡 **Truco**: GitHub muestra el `README.md` automáticamente debajo del listado.
> Es buena señal: significa que el repo se ve correctamente.

### Paso 2.5 — Activar permisos para GitHub Actions

Necesario para que el cron trimestral funcione:

1. En tu repo: **Settings** (pestaña arriba a la derecha)
2. Menú lateral izquierdo: **Actions → General**
3. Baja hasta **Workflow permissions**
4. Marca: **🔘 Read and write permissions**
5. Marca también: **☑ Allow GitHub Actions to create and approve pull requests**
6. Click **Save**

### Paso 2.6 — (Opcional) Probar el workflow ahora

Para verificar que todo funciona sin esperar al próximo trimestre:

1. Vuelve a la página principal del repo
2. Pestaña **Actions** (arriba)
3. En el menú izquierdo, click en **"Actualización automática de datos EPA"**
4. Botón gris a la derecha: **Run workflow → Run workflow** (verde)
5. Espera ~2 minutos
6. Click sobre la ejecución para ver logs

Si todo va verde: GitHub Actions funciona. Si falla, revisa logs (suele ser un
problema de permisos del paso 2.5).

✅ **Hito 2 completado**: tu código está en GitHub, público y citable por URL.

URL de tu repo: `https://github.com/<tu-usuario>/empleo-tic-mvp`

---

## Fase 3: Streamlit Community Cloud

Despliegue de la app pública para que cualquiera (revisores, colegas, alumnos)
pueda interactuar con ella sin instalar nada.

### Paso 3.1 — Login en Streamlit Cloud

1. Ve a [streamlit.io/cloud](https://streamlit.io/cloud)
2. Click **Sign up** o **Sign in**
3. Click **Continue with GitHub**
4. Autoriza el acceso (Streamlit pedirá leer tus repos)

### Paso 3.2 — Crear nueva app

1. En el dashboard: click **Create app** (arriba derecha)
2. Selecciona **Deploy a public app from GitHub**
3. Rellena el formulario:
   - **Repository**: `<tu-usuario>/empleo-tic-mvp`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL** (personalizable): `empleo-tic-mvp` o el que prefieras
4. Click **Deploy!**

### Paso 3.3 — Esperar la primera compilación

Streamlit Cloud:
1. Clona tu repo
2. Crea entorno Python
3. Instala dependencias (~3 min la primera vez)
4. Lanza la app

Verás en directo los logs en pantalla. Si sale algún error, normalmente es por:

- **Falta `requirements.txt`**: ya lo tienes, no debería pasar
- **Versión de Python**: si pasa, ve al paso 3.5

### Paso 3.4 — Verificar la app

Cuando termine, verás "Your app is live!" y la URL pública:

```
https://empleo-tic-mvp.streamlit.app
```

Visítala. Deberías ver las 7 tabs operativas. Prueba:

1. **§ I Macro EPA**: gráficos cargados
2. **§ II Divergencia**: las cifras muestran ~644k (rama) vs ~1000k (ocupación)
3. **§ III Subsectores**: selector de año funciona
4. **§ VI Datos**: descargas de CSV/XLSX funcionan
5. **§ VII Pipeline**: estado de las fuentes visible

### Paso 3.5 — Si algo falla

**App build failed por versión de Python:**

1. Ve a tu repo en GitHub web
2. Click **Add file → Create new file**
3. Nombre: `runtime.txt`
4. Contenido: `3.11`
5. **Commit new file**

Streamlit re-despliega automáticamente.

**App build failed por dependencia:**

Si la salida menciona alguna librería específica:

1. Ve a `requirements.txt` en GitHub
2. Click el icono del lápiz (✏ "Edit this file")
3. Modifica si es necesario
4. **Commit changes**

Re-despliegue automático.

✅ **Hito 3 completado**: tu app es pública, funcional, accesible 24/7.

URL pública: `https://empleo-tic-mvp.streamlit.app`

> 💡 Esta URL ya puedes citarla en cualquier comunicación académica
> (presentación a Rectorado UNIE, mail a Susana Checa, charla con Anthropic, etc.).

---

## Fase 4: Zenodo + DOI

Para que el proyecto sea citable como software académico con identificador
permanente.

### Paso 4.1 — Login en Zenodo

1. Ve a [zenodo.org](https://zenodo.org)
2. Click **Sign up** o **Login** → **Login via GitHub**
3. Autoriza acceso

### Paso 4.2 — Conectar tu repositorio con Zenodo

1. En Zenodo, click tu avatar arriba derecha → **GitHub**
2. Verás lista de tus repos
3. Localiza `empleo-tic-mvp`
4. Activa el **switch a la derecha** (cambia de "Off" gris a "On" verde)

A partir de ahora, cada release que crees en GitHub generará automáticamente
un snapshot Zenodo con DOI.

### Paso 4.3 — Crear el primer release en GitHub

Vuelve a [github.com/<tu-usuario>/empleo-tic-mvp](https://github.com).

1. Página principal del repo
2. Columna derecha: **Releases** (debajo de "About")
3. Si no hay releases aún: click **Create a new release**

   Si ya hay releases: **Releases → Draft a new release**

4. Rellena el formulario:
   - **Choose a tag**: escribe `v1.0.0` y click "Create new tag: v1.0.0 on publish"
   - **Release title**: `v1.0.0 — MVP académico inicial`
   - **Describe this release** (caja de texto):

     ```
     Primera versión publicable del MVP académico para análisis del empleo
     tecnológico español a partir de la EPA T1 2026.

     Incluye:
     - Aplicación Streamlit con 7 paneles interactivos
     - Análisis estadístico formal (Mann-Kendall, STL, Friedman) en Jupyter
     - Cliente API INE Tempus 3.0 + parser de microdatos EPA
     - Pipeline de actualización automática (GitHub Actions trimestral)
     - Manuscrito en LaTeX (~12 páginas, IMRAD)
     - Tests automatizados (20 passing + 1 xfail documentado)
     - Documentación completa, contenedorización Docker, citación CFF

     Hallazgos validados estadísticamente:
     - Tendencia creciente del sector TIC (Z=5,74; p<0,001)
     - Estacionalidad cuasi-nula (Var(S)/Var(Y) < 0,01)
     - Gap rama/ocupación creciente +28k personas/año
     - Concentración Madrid+Cataluña: 60% (HHI=1.684)
     ```

   - ❌ NO marques "Set as a pre-release"
   - ☑ Marca "Set as the latest release"

5. Click **Publish release** (verde, abajo)

### Paso 4.4 — Esperar el DOI de Zenodo

Zenodo detecta el release en 1-3 minutos:

1. Vuelve a [zenodo.org](https://zenodo.org)
2. Click tu avatar → **Uploads**
3. Verás `empleo-tic-mvp v1.0.0` con un DOI asignado

Tu DOI tendrá formato `10.5281/zenodo.NNNNNNN`.

### Paso 4.5 — Actualizar CITATION.cff con el DOI

Para que las herramientas de citación recojan el DOI automáticamente:

1. En GitHub web, navega a `CITATION.cff` en tu repo
2. Click el icono ✏ (Edit this file)
3. Localiza el bloque de metadatos al inicio
4. Después de la línea `version: 0.2.0`, añade:

   ```yaml
   doi: 10.5281/zenodo.NNNNNNN
   identifiers:
     - type: doi
       value: 10.5281/zenodo.NNNNNNN
   ```

   *(Reemplaza NNNNNNN con tu número real.)*

5. También actualiza la versión: cambia `0.2.0` por `1.0.0`
6. Baja a "Commit changes":
   - Commit message: `docs: añadir DOI Zenodo a citación`
   - Marca: **Commit directly to the main branch**
7. Click **Commit changes**

✅ **Hito 4 completado**: tienes DOI permanente. El proyecto es citable con
formato académico estándar.

Tu cita BibTeX (anótala):

```bibtex
@software{fernandez_tamames_2026_empleo_tic,
  author    = {Fernández Tamames, José},
  title     = {Empleo Tecnológico en España: el millón invisible},
  version   = {1.0.0},
  year      = {2026},
  doi       = {10.5281/zenodo.NNNNNNN},
  url       = {https://github.com/<tu-usuario>/empleo-tic-mvp}
}
```

---

## Fase 5: Overleaf — compilar el paper

Para tener el `paper/main.tex` como PDF compilado y enviar a la revista.

### Paso 5.1 — Crear cuenta en Overleaf

1. Ve a [overleaf.com](https://www.overleaf.com)
2. **Sign Up** → recomendado: **Continue with Google** o usar email institucional
3. Si tu universidad UNIE tiene cuenta institucional Overleaf, úsala
4. Plan gratuito es suficiente para esto

### Paso 5.2 — Crear proyecto desde GitHub

**Opción A — Importar desde GitHub (más limpio):**

1. Dashboard Overleaf: **New Project → Import from GitHub**
2. Si es la primera vez, autoriza Overleaf a leer tus repos
3. Selecciona `empleo-tic-mvp`
4. Click **Create**

Overleaf importa todo el repo. Pero solo te interesa la carpeta `paper/`.

**Opción B — Subir solo el .tex (más simple):**

1. En GitHub, navega a `paper/main.tex`
2. Click el botón **Raw** (arriba derecha del visor de archivo)
3. Ctrl+A para seleccionar todo, Ctrl+C para copiar
4. En Overleaf: **New Project → Blank Project**
5. Nombre: `empleo-tic-millon-invisible`
6. Click el archivo `main.tex` que viene por defecto (a la izquierda)
7. Borra todo su contenido y pega el tuyo (Ctrl+V)
8. **Save** (icono disquete arriba)

### Paso 5.3 — Configurar XeLaTeX

Necesario para la fuente EB Garamond:

1. En tu proyecto Overleaf: **Menu** (esquina superior izquierda)
2. Sección **Settings → Compiler**: cambia a **XeLaTeX**
3. Cierra el menú

### Paso 5.4 — Compilar

1. Click **Recompile** (botón verde arriba derecha)
2. Primera compilación: ~30 segundos
3. Si hay error sobre `ebgaramond`:
   - Cambia en `main.tex` (línea ~5):
     ```latex
     \usepackage{ebgaramond}
     ```
     por:
     ```latex
     \usepackage{lmodern}
     ```
   - Recompila

4. Verás el PDF en el panel derecho (~12-14 páginas)

### Paso 5.5 — Descargar el PDF

1. Click el icono **Download** (encima del PDF, flecha hacia abajo)
2. Se descarga `main.pdf`
3. Guárdalo como `Tamames_2026_millon_invisible.pdf`

### Paso 5.6 — Subir el PDF a tu repo (opcional)

Para que esté junto al código:

1. En GitHub web, ve a la carpeta `paper/`
2. Click **Add file → Upload files**
3. Arrastra el `main.pdf`
4. Commit message: `paper: añadir PDF compilado v1.0`
5. **Commit changes**

✅ **Hito 5 completado**: paper compilado, listo para submission.

---

## (Opcional) Fase 6: Probar la app sin desplegarla — GitHub Codespaces

Si en algún momento quieres modificar algo del código y probarlo antes de
hacer commit, GitHub Codespaces te da Python + Streamlit en el navegador,
sin instalar nada.

### Cuándo usarlo

- Quieres editar un CSV y ver el resultado antes de publicarlo
- Quieres ejecutar `pytest` para validar cambios
- Quieres ejecutar el notebook Jupyter sin instalar nada

### Cómo lanzarlo

1. En tu repo GitHub: presiona la tecla **`.`** (punto)
2. Se abre VS Code en el navegador (`github.dev`)
3. Para ejecutar código (Streamlit, pytest), hace falta un Codespace real:
   - Botón verde **Code** (arriba derecha del repo)
   - Pestaña **Codespaces**
   - **Create codespace on main**
   - Esperar ~2 min

4. Una vez dentro:
   - Terminal: ya disponible (Ctrl+`)
   - Comandos:
     ```bash
     pip install -r requirements.txt
     streamlit run app.py
     ```
   - Streamlit lanza un puerto que Codespaces hace público para ti
   - Click "Open in Browser" en el popup

### Cuota gratuita

GitHub da **60 horas/mes gratis** de Codespaces a cuentas personales.
Suficiente para tu uso académico.

> ⚠ Recuerda **detener el codespace** cuando acabes para no consumir cuota:
> Codespaces → click en los tres puntos → **Stop codespace**.

---

## Mantenimiento posterior · web only

### Cada trimestre (automático)

GitHub Actions hace el trabajo. Recibirás email cuando se ejecute.

Si abre un *issue* indicando cambios:
1. Lee el issue (link en email)
2. Si los datos cambiaron, Streamlit Cloud ya redesplegó solo
3. Cierra el issue cuando lo hayas verificado

### Cada año (manual, ~marzo-abril)

Cuando ONTSI publique nueva edición:

1. Descarga el PDF nuevo
2. Anota la cifra de especialistas TIC
3. En GitHub web:
   - Ve a `data/especialistas_tic_anual.csv`
   - Click ✏ (Edit this file)
   - Añade nueva fila al final con el año nuevo
   - Commit
4. Streamlit Cloud redesplega solo en ~3 min

### Cuando llegue T1 2027 (crítico)

Es el momento donde la transición CNAE-2025 obliga a refactorizar el cliente API.
Cuando llegues a ese punto, vuelve a abrir el chat con Claude y te ayudo a
hacer la migración. Es trabajo de unas horas.

---

## URLs públicas finales

Tras completar las fases 1-5 tienes:

| Recurso | URL | Uso |
|---|---|---|
| Repositorio código | `github.com/<tu-usuario>/empleo-tic-mvp` | Citar en papers |
| App interactiva | `<tu-app>.streamlit.app` | Demos, presentaciones |
| Snapshot Zenodo | `zenodo.org/records/NNNNNNN` | Cita formal con DOI |
| Paper PDF | `paper/main.pdf` en repo | Submission revista |

---

## Diagnóstico rápido — qué hacer si algo falla

| Problema | Diagnóstico | Solución |
|---|---|---|
| Repo no aparece en Streamlit Cloud | Tarda en sincronizar | Espera 5 min, refresca |
| App "Build failed" | Falta `runtime.txt` | Crear `runtime.txt` con `3.11` |
| App carga pero crashes | Versión de pandas | Edita `requirements.txt` con versiones más recientes |
| GitHub Actions falla | Permisos | Settings → Actions → "Read and write" |
| Zenodo no detecta release | Switch desactivado | Verifica zenodo.org → GitHub |
| Overleaf compila con errores | XeLaTeX no activo | Settings → Compiler → XeLaTeX |
| Paper sin EB Garamond | Font no instalada | Reemplazar por `lmodern` |

---

## Resumen visual del flujo completo

```
   [ ZIP local ]
        ↓ descomprimir
   [ Carpeta empleo_tic_mvp/ ]
        ↓ drag & drop a GitHub
   [ Repo público en GitHub ] ──→ Activar Actions
        ├──→ Streamlit Cloud  ──→ App pública 24/7
        ├──→ Zenodo            ──→ DOI permanente
        └──→ Overleaf          ──→ Paper PDF
        
   Resultado: proyecto académico publicable y citable, sin código local.
```

---

*Última revisión: 29 de abril de 2026 · José Fernández Tamames · UNIE Universidad*
