import json
from openai import AsyncOpenAI
from app.config import get_settings
from app.rag.engine import get_rag_engine
from app.pricing.client import get_pricing_client

CLASSIFICATION_PROMPT = """Clasifica la siguiente consulta de un socio de la Cámara Argentina de Contratistas Forrajeros.
Responde SOLO con una de estas categorías en JSON:

- {{"intent": "tecnico"}} → consulta técnica sobre ensilado, maquinaria, forraje, earlage, henolaje, henificación
- {{"intent": "precios_referencia"}} → pregunta sobre precios de referencia
- {{"intent": "costos_silaje"}} → pregunta sobre costos de silaje/ensilado
- {{"intent": "costo_materia_seca"}} → pregunta sobre costo de materia seca
- {{"intent": "costos_transporte"}} → pregunta sobre costos de transporte de materia verde
- {{"intent": "saludo"}} → saludo o mensaje general

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
        temperature=0,
        max_tokens=50,
    )

    try:
        result = json.loads(response.choices[0].message.content)
        return result.get("intent", "tecnico")
    except (json.JSONDecodeError, AttributeError):
        return "tecnico"


def format_pricing_response(data: dict, tipo: str) -> str:
    """Formatea la respuesta de precios para WhatsApp."""
    # TODO: Ajustar formateo según estructura real de la API
    header = {
        "precios_referencia": "📊 *Precios de Referencia CACF*",
        "costos_silaje": "🌾 *Costos de Silaje*",
        "costo_materia_seca": "📦 *Costo Materia Seca*",
        "costos_transporte": "🚛 *Costos Transporte Materia Verde*",
    }
    title = header.get(tipo, "📊 *Información de Precios*")
    return f"{title}\n\n{json.dumps(data, indent=2, ensure_ascii=False)}"


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

        return format_pricing_response(data, intent)
    except Exception:
        return (
            "No pude obtener la información de precios en este momento. "
            "Por favor, intentá nuevamente en unos minutos."
        )
