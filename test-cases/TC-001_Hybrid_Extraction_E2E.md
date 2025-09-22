# Test Case 001: End-to-End Hybrid Extraction and Analysis

**ID:** TC-001
**Epic:** Fase 1: La Fundación del RAG
**Feature:** `TASK_1.3`: Refactorizar doc_processor.py con lógica de extracción híbrida

**Objective:** Verificar que el nuevo pipeline híbrido (`PyMuPDF` + GPT-4o Vision) extrae correctamente el contenido de un PDF y que el `ai_analyzer` genera un resumen de alta calidad sin alucinaciones, comparable al análisis de referencia.

---

## 1. Pre-condiciones (Setup)

1.  El código se encuentra en el estado actual (tras la implementación de la lógica híbrida en `doc_processor.py`).
2.  El fichero `requirements.txt` incluye `PyMuPDF`.
3.  Las variables de entorno (`.env`) para Slack y OpenAI están configuradas correctamente.
4.  El PDF de prueba es `Stamp_Investor-Deck.pdf`, disponible en la carpeta de Google Drive que se usará para el análisis.

## 2. Pasos de la Ejecución (Action)

1.  En la terminal, iniciar la aplicación con el comando: `python app.py`.
2.  En el canal de Slack configurado para la app, ejecutar el comando: `/analyze [link-a-la-carpeta-de-drive-con-el-deck-de-Stamp]`.
3.  Esperar a que la aplicación complete todo el proceso y publique el mensaje con el análisis final en el canal de Slack.
4.  Copiar el **log completo de la consola**, desde el momento en que se inicia la app hasta que finaliza el análisis.
5.  Copiar el **texto completo del mensaje final** recibido en Slack.
6.  Entregar a Rita (yo) tanto el log como el mensaje de Slack para su validación.

## 3. Resultados Esperados (Expected Results)

*   **ER-1: Sin Errores Críticos:** La aplicación no debe detenerse por un error. El log no debe contener errores de tipo `ERROR` o `FATAL` en el flujo principal de `doc_processor` o `ai_analyzer`.

*   **ER-2: Verificación del Método Híbrido (en Logs):** El log **DEBE** contener la línea:
    ```
    INFO - 📄 Processing PDF with HYBRID method
    ```

*   **ER-3: Verificación de la Calidad de Extracción (en Logs):** El log **DEBE** mostrar una extracción de contenido sustancial. Se espera una línea similar a:
    ```
    INFO - ✅ Hybrid processing successful: ... X chars
    ```
    ...donde `X` sea un número significativamente mayor a 2,000 (se esperan más de 10,000 caracteres para el deck de Stamp).

*   **ER-4: Calidad del Resumen Final (en Slack):** El mensaje publicado en Slack **DEBE** ser factualmente correcto y de alta calidad.
    *   **Criterio 4a (No Alucinaciones):** NO DEBE contener datos obviamente inventados (ej. "John Doe", "Paris", rondas de financiación incorrectas, etc.).
    *   **Criterio 4b (Extracción Correcta):** DEBE contener las métricas de tracción clave del documento (ej. "+1300 Comerciantes", "+40,000 Viajeros", "2M€ Seed Round", logos de clientes, etc.).
    *   **Criterio 4c (Calidad Analítica):** La interpretación de los datos debe ser correcta (ej. no confundir GMV con tamaño de mercado). La calidad general debe ser muy cercana a la del análisis de referencia guardado en `docs/outputs analyze/gemini`.
