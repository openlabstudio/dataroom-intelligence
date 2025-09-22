# PRD-001: Pipeline de Extracción Híbrida de Documentos

**Épica:** Fase 1: La Fundación del RAG - Extracción y Persistencia de Datos
**Referencia:** Este documento detalla la implementación de la acción más crítica de la **Fase 1** descrita en el `ROADMAP_SaaS_Architecture.md`.
**Status:** Propuesto
**Autor:** Gemini
**Fecha:** 2025-09-19

---

## 1. Contexto y Problema a Resolver

**Problema:** El sistema actual depende exclusivamente de la API de GPT-4o Vision para extraer texto de los PDFs. Este enfoque ha demostrado ser poco fiable, lento y costoso. Produce un texto de baja fidelidad que a su vez provoca que la capa de análisis final "alucine" o genere resúmenes de baja calidad. Esto bloquea la capacidad del producto para aportar valor real y ser comercialmente viable.

**Objetivo:** Reemplazar el pipeline de extracción actual por un **sistema híbrido, robusto y eficiente**. El objetivo es producir un texto con una fidelidad cercana al 100% para cada página del documento, sentando una base de datos fiable sobre la que se puedan construir todas las futuras funcionalidades de análisis, Q&A y, fundamentalmente, el sistema RAG.

## 2. Requisitos Funcionales (RF)

*   **RF-1: Clasificación de Páginas:** El sistema debe ser capaz de analizar cada página de un PDF de entrada y clasificarla como **"Texto-Dominante"** (la mayoría del contenido es texto digital nativo) o **"Imagen-Dominante"** (la mayoría del contenido es una imagen, un gráfico complejo, o texto no nativo).

*   **RF-2: Extracción de Texto Nativo:** Para las páginas clasificadas como "Texto-Dominante", el sistema **DEBE** usar una librería local (`PyMuPDF`) para extraer el contenido de texto. Este método es el preferido por su velocidad, coste cero y máxima precisión.

*   **RF-3: Extracción de Texto de Imágenes (OCR):** Para las páginas clasificadas como "Imagen-Dominante", el sistema **DEBE** renderizar la página como una imagen de alta resolución y enviarla a un modelo de IA con capacidad de visión (GPT-4o) para realizar un OCR de alta fidelidad.

*   **RF-4: Ensamblaje de Contenido:** El sistema **DEBE** consolidar los resultados de los diferentes métodos de extracción en una única estructura de datos coherente. El formato final debe ser una lista de strings, donde cada string representa el texto completo de una página, manteniendo el orden original del documento.

*   **RF-5: Aislamiento de Sesiones por Canal:** El sistema **DEBE** gestionar cada análisis como una sesión única y aislada por canal de Slack. Esto es un prerrequisito para la persistencia y la funcionalidad multi-tenant.

    **Notas de Implementación Técnica (TASK_1.2):**
    *   En `app.py`, la variable global en memoria `user_sessions` será renombrada a `channel_sessions` para reflejar la nueva lógica.
    *   Todas las lecturas y escrituras a este diccionario se refactorizarán para usar `channel_id` como la clave principal en lugar de `user_id`. Esto afecta a las funciones `debug_sessions`, `perform_dataroom_analysis`, `handle_ask_command`, y `handle_reset_command`.
    *   Al inicio de la función `perform_dataroom_analysis`, se añadirá lógica para crear un directorio de sesión si no existe, usando la ruta `/.datarooms/{channel_id}/`. Se usará la función `os.makedirs(path, exist_ok=True)`.

## 3. Requisitos No Funcionales (RNF)

*   **RNF-1 (Rendimiento):** El proceso de extracción completo para un deck estándar de 20 páginas (mayoritariamente texto) no debería superar los 15 segundos, excluyendo los tiempos de red de subida/bajada de ficheros.

*   **RNF-2 (Precisión):** La extracción de texto para páginas nativas debe tener una precisión >99.9%. La precisión del OCR para páginas gráficas debe ser >95%.

*   **RNF-3 (Coste):** El sistema debe ser económicamente eficiente, minimizando las llamadas a la costosa API de Vision y reservándola exclusivamente para las páginas que no pueden ser procesadas localmente.

*   **RNF-4 (Robustez):** El sistema debe gestionar de forma elegante los posibles errores durante el parseo de PDFs (ej. ficheros corruptos) y registrarlos adecuadamente sin interrumpir el flujo completo de análisis de un dataroom.

## 4. Historias de Usuario

*   **Como Analista de VC**, quiero que el sistema extraiga los datos de las tablas y los números de los gráficos con la misma precisión que el texto de los párrafos, para asegurar que no se pierde ninguna métrica clave en el análisis.
*   **Como Product Owner**, quiero que el pipeline de extracción sea fiable y predecible, para poder construir con confianza funcionalidades de RAG y Q&A sobre una base de datos sólida.
*   **Como Cliente (Fondo de Inversión)**, quiero que el análisis sea rápido y preciso, para poder tomar decisiones de inversión informadas sin tener que revisar manualmente cada documento por miedo a que la IA se haya equivocado.

## 5. Criterios de Aceptación

*   **Dado** un PDF con texto nativo, **cuando** se procesa, **entonces** el texto extraído es una copia exacta del contenido del fichero.
*   **Dado** un PDF que contiene slides que son solo imágenes, **cuando** se procesa, **entonces** el sistema identifica esas páginas y utiliza la API de Vision para extraer el texto de ellas.
*   **Dado** un PDF mixto, **cuando** se procesa, **entonces** el log del sistema muestra claramente qué páginas se procesaron con `PyMuPDF` y cuáles con la API de Vision.
*   **Dado** un PDF corrupto, **cuando** se procesa, **entonces** el sistema lo marca como erróneo y continúa con el resto de documentos del dataroom sin fallar.
*   El objeto final devuelto por el procesador para un PDF exitoso contiene la clave `"pages"` con una lista de strings.

## 6. Fuera de Alcance (Para esta Épica)

*   La implementación del almacenamiento persistente de esta información (será abordado en la **Fase 1** junto a esto).
*   La implementación del "chunking" o la vectorización del texto (será abordado en la **Fase 2**).
*   Cualquier análisis o interpretación semántica del contenido extraído. El único objetivo de esta épica es la **extracción de texto de alta fidelidad**.

---
### Technical Implementation Notes (TASK_1.3)

1.  **Objective**: Refactor `handlers/doc_processor.py` to replace the existing extraction logic with a hybrid model that combines local text extraction and a vision-based OCR fallback.

2.  **File to Modify**: `handlers/doc_processor.py`.

3.  **Core Logic Implementation (`_process_pdf` method)**:
    *   The method will accept a file path and file name.
    *   It will use `fitz.open(file_path)` to open the PDF document.
    *   It will iterate through each `page` of the document.
    *   For each page, it will attempt to extract native text using `page.get_text("text", sort=True)`.

4.  **Hybrid Heuristic**:
    *   A simple heuristic will be used to classify the page. If the extracted text's character count is greater than 100 (`len(page_text) > 100`), the page will be classified as **"Text-Dominant"**.
    *   If the character count is 100 or less, it will be classified as **"Image-Dominant"**, triggering the OCR fallback.

5.  **OCR Fallback Logic (`_get_ocr_for_image` method)**:
    *   When a page is deemed "Image-Dominant":
        *   A log message will indicate the fallback to Vision OCR.
        *   The page will be rendered as a high-resolution PNG image (e.g., 200 DPI) using `page.get_pixmap()`.
        *   The image will be saved to a temporary directory (e.g., `./temp/`).
        *   The `_get_ocr_for_image` helper method will be called with the path to the temporary image. This method uses the `gpt4o_processor` to send the image to the "gpt-4o" model with a specific OCR prompt.
        *   The text returned by the API will be appended to the list of page contents.
        *   The temporary image file will be deleted using `os.remove()`.

6.  **Final Output Structure**:
    *   The `_process_pdf` method will return a dictionary containing:
        *   `name`: The original file name.
        *   `type`: 'pdf'.
        *   `pages`: A list of strings, where each string is the full text of a page.
        *   `metadata`: A sub-dictionary including `extraction_method`, `pages_count`, `text_pages`, and `image_pages` to provide visibility into the process.

7.  **Error Handling**: The entire `_process_pdf` logic will be wrapped in a `try...except` block to gracefully handle file corruption or other processing errors, returning a structured error message without crashing.

---
### Technical Implementation Plan for TASK_1.4

1.  **Objective**: Persist the JSON output from the `DocumentProcessor` to disk.
2.  **File Format**: The output for each processed document will be saved as a separate `.json` file.
3.  **File Naming Convention**: The name of the JSON file will be derived from the original document's name, but with the `.json` extension. For example, `investor_deck.pdf` will become `investor_deck.pdf.json`.
4.  **Storage Location**: The JSON files will be stored inside the session directory that is already being created, i.e., `/.datarooms/{channel_id}/{file_name}.json`.
5.  **Implementation Details**:
    *   The `perform_dataroom_analysis` function in `app.py` will be modified.
    *   After the `doc_processor.process_dataroom_documents(downloaded_files)` call, a loop will iterate through the `processed_documents` list.
    *   For each `doc` in the list, the full output path will be constructed: `os.path.join(session_dir, f"{doc['name']}.json")`.
    *   `json.dump()` will be used to write the `doc` dictionary to the specified path.
    *   A log entry will be added to confirm the file has been saved, e.g., `logger.info(f"💾 Saved extraction results to {output_path}")`.