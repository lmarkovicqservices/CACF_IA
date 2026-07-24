import hashlib
import hmac
from fastapi import APIRouter, Request, Query, HTTPException
from app.config import get_settings
from app.auth.validator import validate_member
from app.whatsapp.client import send_text_message
from app.agent.router import process_message

router = APIRouter()

@router.post("/answer")
async def receive_answer_control(request: Request):
    """Recibe mensaje de prueba via POST de API."""
    settings = get_settings()

    data = await request.json()

    # Extraer mensaje del payload de Meta
    try:

        if "pregunta" not in data:
            return {"status": "no question"}

        message = data["pregunta"]

        if not message:
            return {"status": "no text"}

    except (KeyError, IndexError):
        return {"status": "invalid payload"}

    # Procesar mensaje y generar respuesta
    response_text = await process_message("", message)
    # await send_text_message(phone_number, response_text)

    return {response_text}
