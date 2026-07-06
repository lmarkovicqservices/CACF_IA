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
│  ┌───────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │ Webhook   │  │ Auth         │  │ Rate Limiter        │   │
│  │ Handler   │→ │ Middleware   │→ │ (por usuario)       │   │
│  └───────────┘  └──────────────┘  └─────────────────────┘   │
│                         │                                   │
│                         ▼                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Router / Intent Classifier              │   │
│  │         (Detecta si es consulta técnica o precio)    │   │
│  └────────────┬─────────────────────┬───────────────────┘   │
│               │                     │                       │
│               ▼                     ▼                       │
│  ┌────────────────────┐  ┌─────────────────────────────┐    │
│  │   RAG Pipeline     │  │   API Precios Client        │    │
│  │  ┌──────────────┐  │  │  - Precios Referencia       │    │
│  │  │ ChromaDB     │  │  │  - Costos Silaje            │    │
│  │  │ (vectores)   │  │  │  - Costo Materia Seca       │    │
│  │  └──────────────┘  │  │  - Costos Transporte MV     │    │
│  │  ┌──────────────┐  │  └─────────────────────────────┘    │
│  │  │ Retriever    │  │                                     │
│  │  │ + Reranker   │  │                                     │
│  │  └──────────────┘  │                                     │
│  └────────────────────┘                                     │
│               │                     │                       │
│               ▼                     ▼                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  GPT-4o (OpenAI)                     │   │
│  │          System Prompt + Context + Query             │   │
│  └──────────────────────────────────────────────────────┘   │
│                         │                                   │
│                         ▼                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              WhatsApp Response Sender                │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

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
4. **Clasificación**: El router determina si la consulta es:
   - Técnica (→ RAG pipeline)
   - De precios (→ API Precios)
   - General/saludo (→ respuesta directa GPT-4o)
5. **Procesamiento RAG** (si aplica):
   - Se genera embedding de la consulta
   - Se buscan los 5 chunks más relevantes en ChromaDB
   - Se arma el prompt con contexto recuperado
6. **Generación**: GPT-4o genera la respuesta con el contexto
7. **Respuesta**: Se envía la respuesta al usuario vía WhatsApp API

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
