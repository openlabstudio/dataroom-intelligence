# ADR-001: Deprecación Temporal de /gaps, /memo y /scoring

**Status:** Aceptado
**Fecha:** 2025-09-19

## Contexto

En la fase actual de desarrollo, el foco principal es construir un pipeline de extracción de datos robusto y una funcionalidad de Q&A básica a través de una arquitectura RAG. Los comandos `/gaps`, `/memo` y `/scoring` representan funcionalidades de análisis de una capa superior que no están alineadas con el objetivo inmediato y probablemente requieran un rediseño completo una vez que la base RAG esté implementada.

## Decisión

Se ha decidido **deprecar temporalmente** los comandos `/gaps`, `/memo` y `/scoring`. El desarrollo activo ignorará estos comandos y no se implementará nueva lógica para ellos hasta que se tome una nueva decisión estratégica en una fase posterior del producto.

## Consecuencias

*   Rita (Lead AI Engineer) no incluirá estos comandos en las refactorizaciones actuales o futuras, a menos que se decida explícitamente reactivarlos.
*   El código existente relacionado con estos comandos puede ser eliminado si interfiere con el nuevo desarrollo para simplificar la base del código.
*   El foco del producto a corto plazo se centrará en la calidad de la extracción (`/analyze`) y la precisión de las respuestas (`/ask`).
