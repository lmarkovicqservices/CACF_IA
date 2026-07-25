import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import openai
from app.config import get_settings
from app.rag.engine import get_rag_engine
from app.pricing.client import get_pricing_client
from app.services.message_service import MessageService

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

    try:
        client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "Eres un clasificador de intenciones. Responde solo con JSON."},
                {"role": "user", "content": CLASSIFICATION_PROMPT.format(message=message)},
            ],
            temperature=0,
            max_tokens=50,
        )
    except Exception:
        return "tecnico"

    try:
        result = json.loads(response.choices[0].message.content)
        return result.get("intent", "tecnico")
    except (json.JSONDecodeError, AttributeError, TypeError):
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
    service = MessageService(
        intent_classifier=classify_intent,
        rag_engine=get_rag_engine(),
        pricing_client=get_pricing_client(),
    )
    return await service.handle_message(phone_number, message)
