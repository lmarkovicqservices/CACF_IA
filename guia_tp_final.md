# Guía rápida para el Trabajo Final

Este documento adapta las consignas del TP a este proyecto de CACF IA y sirve como checklist para la presentación e informe final.

## 1. Definición del problema

### Problema a resolver
Crear un asistente conversacional vía WhatsApp para socios de CACF que pueda responder preguntas técnicas sobre ensilado, earlage, henolaje y henificación, y también ofrecer información de precios de referencia.

### Justificación
- Los socios necesitan respuestas rápidas y accesibles sin revisar manuales extensos.
- WhatsApp es un canal natural y de alto uso para consulta inmediata.
- Una solución con IA puede reducir tiempos de búsqueda y mejorar la disponibilidad de información.

### Propuesta de solución
Implementar un asistente que:
- reciba mensajes por WhatsApp,
- valide al socio,
- clasifique la consulta,
- responda usando documentos técnicos o información de precios,
- y entregue la respuesta en lenguaje natural.

### MVP propuesto
Un MVP mínimo debe incluir:
- recepción de mensajes vía webhook,
- autenticación básica del socio,
- respuesta a consultas técnicas con RAG,
- respuesta a consultas simples o de saludo,
- y una salida funcional por WhatsApp.

---

## 2. Revisión del estado del arte

### Qué incluir en este apartado
Buscar y resumir trabajos o enfoques relacionados con:
- asistentes conversacionales para agricultura o industria agropecuaria,
- sistemas RAG para respuesta a preguntas sobre documentos técnicos,
- chatbots en WhatsApp con IA,
- y aplicaciones de IA en contextos de soporte técnico.

### Punto clave para el informe
Mostrar que la solución no es solo una demo de chatbot, sino una propuesta concreta basada en técnicas conocidas como RAG, LLM y recuperación de información.

### Ejemplo de estructura
- Introducción al problema.
- Trabajos relacionados.
- Comparación de enfoques.
- Conclusión sobre la elección del enfoque propuesto.

---

## 3. Implementación del MVP

### Funcionalidades mínimas del proyecto
- [ ] Recibir mensajes desde WhatsApp.
- [ ] Validar el número del socio.
- [ ] Clasificar el tipo de consulta.
- [ ] Responder consultas técnicas usando documentos cargados.
- [ ] Responder consultas generales o saludos.
- [ ] Enviar la respuesta de vuelta por WhatsApp.

### Componentes del proyecto que ya existen
- Estructura base de FastAPI.
- Webhook de entrada.
- Endpoints de health.
- Organización por módulos: API, auth, whatsapp, rag, pricing, agent.

### Qué falta completar para que el MVP quede sólido
- [ ] Integración real del motor RAG.
- [ ] Carga e indexación de documentos técnicos.
- [ ] Recuperación de chunks relevantes.
- [ ] Prompt con contexto y respuesta final.
- [ ] Manejo de consultas de precios.
- [ ] Pruebas básicas.
- [ ] Despliegue o demo local funcional.

---

## 4. Entregables del TP

### Entregable 1: propuesta inicial
- 2 a 3 páginas.
- Incluir problema, propuesta, alcance del MVP y datos/documentos previstos.

### Entregable 2: revisión del estado del arte
- 4 a 5 páginas.
- Incluir 3 o más referencias y análisis breve de cada una.

### Entregable 3: presentación final
- Hasta 8 diapositivas.
- Máximo 10 minutos.
- Fuente 28 puntos.
- Enfatizar problema, solución, arquitectura, resultados y impacto.

### Entregable 4: informe final
- Hasta 10 páginas.
- Incluir resumen, introducción, trabajos relacionados, MVP, resultados, impacto social y ético, conclusiones y trabajo futuro.

---

## 5. Sugerencia de estructura para la presentación final

### Diapositiva 1: título
- Nombre del proyecto.
- Integrantes.
- Contexto general.

### Diapositiva 2: problema
- Qué problema resuelve la solución.
- Por qué es relevante para CACF.

### Diapositiva 3: solución propuesta
- Qué hace el asistente.
- Cómo funciona por WhatsApp.

### Diapositiva 4: arquitectura
- FastAPI, WhatsApp, LLM, RAG, documentos.

### Diapositiva 5: MVP
- Qué quedó implementado.
- Qué se pudo demostrar.

### Diapositiva 6: resultados o demo
- Ejemplo de conversación.
- Resultado obtenido.

### Diapositiva 7: impacto ético y social
- Accesibilidad.
- Mejora de información técnica.
- Riesgos y limitaciones.

### Diapositiva 8: próximos pasos
- Mejoras futuras.
- Escalabilidad.
- Integración con más fuentes de información.

---

## 6. Checklist final para este proyecto

### Preparación conceptual
- [ ] Definir claramente el problema.
- [ ] Explicar por qué el canal WhatsApp es adecuado.
- [ ] Definir el alcance del MVP.

### Preparación técnica
- [ ] Mostrar la arquitectura del sistema.
- [ ] Explicar cómo funciona el motor RAG.
- [ ] Mostrar cómo se integran los módulos del proyecto.

### Preparación del informe y presentación
- [ ] Redactar propuesta inicial.
- [ ] Completar revisión del estado del arte.
- [ ] Preparar presentación de 8 diapositivas.
- [ ] Preparar informe final de hasta 10 páginas.

---

## 7. Enfoque recomendado para este TP

La propuesta más sólida para este trabajo es presentar este proyecto como un asistente de IA para soporte técnico y consulta de precios para socios de CACF, usando una arquitectura basada en:
- FastAPI,
- WhatsApp,
- LLM,
- y RAG sobre documentos técnicos.

Eso conecta muy bien con el objetivo del TP: resolver un problema real usando IA de forma concreta y medible.
