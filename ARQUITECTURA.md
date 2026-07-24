# CACF IA - Asistente Técnico de Ensilado via WhatsApp

## Visión General
Asistente conversacional vía WhatsApp para socios de la Cámara Argentina de Contratistas Forrajeros (CACF).
Responde consultas técnicas sobre ensilado, earlage, henolaje y henificación, y provee información de precios de referencia.

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                        WHATSAPP USER                        │
└─────────────────────┬───────────────────────────────────────┘
                      │ Meta Cloud API (Webhook)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                         │
│  ┌───────────────────────────────────────────────────────┐ │
│  │               Capa de Entrada / API                   │ │
│  │  - Webhook WhatsApp                                  │ │
│  │  - Health endpoint                                   │ │
│  └───────────────────────┬───────────────────────────────┘ │
│                          ▼                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │           Capa de Servicios de Aplicación            │ │
│  │  - MessageService                                   │ │
│  │  - IntentRouter                                      │ │
│  │  - RAGService                                        │ │
│  │  - PricingService                                    │ │
│  └───────────────────────┬───────────────────────────────┘ │
│                          ▼                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │         Capa de Infraestructura / Integraciones      │ │
│  │  - Auth Client (socios)                              │ │
│  │  - WhatsApp Client                                   │ │
│  │  - Pricing Client                                    │ │
│  │  - OpenAI / Embeddings                               │ │
│  │  - ChromaDB                                          │ │
│  └───────────────────────┬───────────────────────────────┘ │
│                          ▼                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │            Persistencia y Conocimiento               │ │
│  │  - Documentos técnicos .docx                         │ │
│  │  - Chunks indexados                                  │ │
│  │  - Metadatos: fuente, tema, fecha                    │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Propuesta de arquitectura para el MVP

La arquitectura se organiza en capas para que el proyecto sea más claro, testeable y fácil de defender en el TP:

1. Capa de entrada
   - Recibe mensajes desde WhatsApp mediante el webhook de Meta.
   - Valida la firma del request y el acceso del usuario.

2. Capa de servicios de aplicación
   - Orquesta el flujo completo de la conversación.
   - Clasifica la intención del mensaje.
   - Decide si la consulta debe resolverse con RAG, con precios o con una respuesta directa.

3. Capa de infraestructura
   - Encapsula las integraciones externas: WhatsApp, OpenAI, validación de socios y API de precios.
   - Permite aislar el resto del sistema de cambios en terceros.

4. Capa de conocimiento
   - Mantiene los documentos técnicos y su representación vectorial en ChromaDB.
   - Los documentos pasan por ingestión, chunking, embeddings y almacenamiento.

### Mejoras propuestas respecto a la versión inicial

- Agregar una capa de servicios para separar la lógica de negocio de los endpoints.
- Definir fallbacks explícitos para casos donde:
  - no haya contexto suficiente en el RAG,
  - falle la API de precios,
  - o falle la llamada al modelo.
- Hacer explícito el pipeline de ingesta de documentos:
  1. cargar documentos .docx,
  2. normalizar texto,
  3. dividir en chunks,
  4. generar embeddings,
  5. indexarlos en ChromaDB con metadatos.

### Mecanismos de robustez

- Si el RAG no encuentra información relevante, la respuesta debe indicar que no hay suficiente contexto y ofrecer una derivación al equipo técnico.
- Si falla la integración con la API de precios, la aplicación debe responder con un mensaje claro de error o una respuesta fallback controlada.
- Si falla el modelo de generación, se puede usar un template simple de respuesta para no dejar la conversación vacía.

---

## Stack Tecnológico

| Capa          | Tecnología             | Versión |
|---------------|------------------------|---------|
| Lenguaje      | Python                 | 3.11+   |
| Framework API | FastAPI                | 0.115+  |
| Server ASGI   | Uvicorn                | 0.30+   |
| LLM           | OpenAI GPT-4o          | API     |
| Embeddings    | text-embedding-3-small | API     |
| RAG Framework | LangChain              | 0.2+    |
| Vector Store  | ChromaDB               | 0.5+    |
| WhatsApp      | Meta Cloud API         | v21.0   |
| Doc Processing| python-docx, unstructured| -     |
| Validación    | Pydantic v2              | -     |
| Testing       | pytest + httpx           | -     |
| Hosting       | DonWeb VPS (Ubuntu)      | -     |

---

## Estructura del Proyecto

```
CACF_IA/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app + startup
│   ├── config.py               # Settings (env vars)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── webhooks.py         # WhatsApp webhook endpoint
│   │   └── health.py           # Health check
│   ├── auth/
│   │   ├── __init__.py
│   │   └── validator.py        # Validación de socios por celular
│   ├── whatsapp/
│   │   ├── __init__.py
│   │   ├── client.py           # Envío de mensajes WhatsApp
│   │   └── models.py           # Modelos de mensajes WA
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── engine.py           # Pipeline RAG principal
│   │   ├── embeddings.py       # Generación de embeddings
│   │   ├── vectorstore.py      # ChromaDB operations
│   │   └── document_loader.py  # Carga de .docx técnicos
│   ├── pricing/
│   │   ├── __init__.py
│   │   └── client.py           # Cliente API Precios CACF
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── router.py           # Intent classification
│   │   └── prompts.py          # System prompts del agente
│   └── models/
│       ├── __init__.py
│       └── schemas.py          # Pydantic schemas compartidos
├── data/
│   └── documentos/             # .docx técnicos (por tema)
├── scripts/
│   ├── ingest_documents.py     # Script para indexar documentos
│   └── test_rag.py             # Test manual del RAG
├── tests/
│   ├── __init__.py
│   ├── test_webhook.py
│   ├── test_auth.py
│   ├── test_rag.py
│   └── test_pricing.py
├── .env.example                # Variables de entorno (template)
├── .gitignore
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Flujo de un Mensaje

1. **Recepción**: Meta Cloud API envía POST al webhook `/api/webhook`
2. **Verificación**: Se valida la firma del webhook (seguridad Meta)
3. **Autenticación**: Se extrae el número de celular y se valida contra la API de socios
4. **Orquestación**: El servicio de aplicación recibe el mensaje y lo deriva al componente adecuado
5. **Clasificación**: El router determina si la consulta es:
   - Técnica (→ servicio RAG)
   - De precios (→ servicio de precios)
   - General/saludo (→ respuesta directa o template)
6. **Procesamiento RAG** (si aplica):
   - Se genera embedding de la consulta
   - Se buscan los 5 chunks más relevantes en ChromaDB
   - Se arma el prompt con contexto recuperado
7. **Fallbacks**: Si no hay contexto suficiente o falla una integración, se responde con una alternativa controlada
8. **Respuesta**: Se envía la respuesta al usuario vía WhatsApp API

---

## Seguridad

- Webhook verificado con firma HMAC (Meta)
- Validación de usuario por número de celular (API socios)
- Rate limiting por usuario (evitar abuso de tokens)
- Variables sensibles en `.env` (nunca en código)
- HTTPS obligatorio (requisito de Meta)

---

## Fases de Desarrollo

### Fase 1: Fundación (Semana 1-2)
- [ ] Setup proyecto Python + FastAPI
- [ ] Configuración de variables de entorno
- [ ] Webhook WhatsApp (recibir/enviar mensajes)
- [ ] Autenticación de socios

### Fase 2: RAG Engine (Semana 3-4)
- [ ] Procesamiento de documentos .docx
- [ ] Chunking inteligente por temas
- [ ] Indexación en ChromaDB
- [ ] Pipeline de retrieval + generación

### Fase 3: Integración Precios (Semana 4-5)
- [ ] Cliente API Precios
- [ ] Router de intenciones (técnico vs precio)
- [ ] Formateo de respuestas de precios para WhatsApp

### Fase 4: Deploy (Semana 5-6)
- [ ] Dockerfile + docker-compose
- [ ] Deploy en DonWeb VPS
- [ ] Configuración Meta Business (número WhatsApp)
- [ ] Testing end-to-end

### Fase 5: Optimización (Continuo)
- [ ] Logging y monitoreo
- [ ] Ajuste de prompts según feedback
- [ ] Ampliación de base de conocimiento
