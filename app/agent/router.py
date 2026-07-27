import json
from openai import AsyncOpenAI
from app.config import get_settings
from app.rag.engine import get_rag_engine
from app.pricing.client import get_pricing_client

VALID_INTENTS = {
    "precios_referencia",
    "costos_silaje",
    "costo_materia_seca",
    "costos_transporte",
    "saludo",
    "tecnico",
}

CLASSIFICATION_PROMPT = """Clasifica la siguiente consulta de un socio de la Cámara Argentina de Contratistas Forrajeros.
Responde SOLO con una de estas categorías en JSON:

- {{"intent": "precios_referencia"}} → pregunta sobre precios de referencia
- {{"intent": "costos_silaje"}} → pregunta sobre costos de silaje/ensilado
- {{"intent": "costo_materia_seca"}} → pregunta sobre costo de materia seca
- {{"intent": "costos_transporte"}} → pregunta sobre costos de transporte de materia verde
- {{"intent": "saludo"}} → saludo o mensaje general
- {{"intent": "tecnico"}} → consulta técnica sobre ensilado, maquinaria, forraje, earlage, henolaje, henificación

Consulta: {message}"""


async def classify_intent(message: str) -> str:
    """Clasifica la intención del mensaje del usuario."""
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": "Eres un clasificador de intenciones. Responde solo con JSON."},
            {"role": "user", "content": CLASSIFICATION_PROMPT.format(message=message)},
        ],
        response_format={"type": "json_object"},
        temperature=0,
        max_tokens=80,
    )

    try:
        content = (response.choices[0].message.content or "").strip()
        result = json.loads(content) if content else {}
        if not isinstance(result, dict):
            return "tecnico"

        intent = result.get("intent", "tecnico")
        return intent if intent in VALID_INTENTS else "tecnico"
    except (json.JSONDecodeError, AttributeError, TypeError, IndexError):
        return "tecnico"


PRICING_PROMPT = """Eres un asistente de la Cámara Argentina de Contratistas Forrajeros (CACF).
El socio hizo una consulta sobre precios/costos y el sistema obtuvo los siguientes datos actualizados de la API de CACF.

Contexto sobre las APIs de precios:
{pricing_context}

Datos obtenidos de la API:
{api_data}

Pregunta del socio: {question}

Responde de forma clara, amigable y bien formateada para WhatsApp (usa negritas con *texto*, listas con •).
Interpreta los datos y presenta la información relevante a la pregunta del socio.
Si hay fechas o períodos, mencionálos. Si hay valores en pesos, formateálos con separador de miles."""

PRICING_API_CONTEXT = """La CACF publica 4 indicadores económicos para sus socios contratistas forrajeros:

1. *Precios de Referencia (API_EcoPF)*: Precios sugeridos por hectárea para servicios de picado fino (silaje). 
   Incluyen valores orientativos según zona, tipo de cultivo (maíz, sorgo) y rendimiento estimado.

2. *Costos de Silaje (API_EcoCS)*: Estructura de costos operativos para el contratista que realiza silaje. 
   Incluye combustible, mano de obra, amortización de maquinaria, logística y márgenes.

3. *Costo por Materia Seca (API_EcoMS)*: Costo por tonelada de materia seca producida. 
   Útil para comparar eficiencia entre distintos cultivos y condiciones.

4. *Costos de Transporte de Materia Verde (API_EcoTMV)*: Tarifas de flete para transporte de material 
   picado desde el lote hasta la bolsa/bunker, según distancia en km.

Estos valores se actualizan periódicamente y son referencia para negociaciones entre contratistas y productores."""


async def generate_pricing_answer(data: dict, question: str) -> str:
    """Pasa los datos de la API al LLM para generar una respuesta natural."""
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "user", "content": PRICING_PROMPT.format(
                pricing_context=PRICING_API_CONTEXT,
                api_data=json.dumps(data, indent=2, ensure_ascii=False),
                question=question,
            )},
        ],
        temperature=0.3,
        max_tokens=1000,
    )
    return (response.choices[0].message.content or "").strip()


async def process_message(phone_number: str, message: str) -> str:
    """Procesa un mensaje y genera la respuesta apropiada."""
    intent = await classify_intent(message)

    if intent == "saludo":
        return (
            "¡Hola! Soy el asistente técnico de CACF. 🌾\n\n"
            "Puedo ayudarte con:\n"
            "• Consultas técnicas sobre ensilado, earlage, henolaje\n"
            "• Precios de referencia\n"
            "• Costos de silaje y materia seca\n"
            "• Costos de transporte\n\n"
            "¿En qué puedo ayudarte?"
        )

    if intent == "tecnico":
        engine = get_rag_engine()
        return await engine.query(message)

    # Intents de precios
    pricing = get_pricing_client()
    try:
        if intent == "precios_referencia":
            data = await pricing.get_precios_referencia()
        elif intent == "costos_silaje":
            data = await pricing.get_costos_silaje()
        elif intent == "costo_materia_seca":
            data = await pricing.get_costo_materia_seca()
        elif intent == "costos_transporte":
            data = await pricing.get_costos_transporte_mv()
        else:
            data = await pricing.get_precios_referencia()

        return await generate_pricing_answer(data, message)
    except Exception as e:
        return (
            "No pude obtener la información de precios en este momento. "
            "Por favor, intentá nuevamente en unos minutos.\n"
            f"[Error técnico: {e}]"
        )
