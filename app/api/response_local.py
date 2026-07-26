from fastapi import APIRouter, Request
from app.agent.router import process_message

router = APIRouter()


@router.post("/answer")
async def receive_answer_control(request: Request):
    """Recibe mensaje de prueba via POST de API (sin WhatsApp)."""
    data = await request.json()

    if "pregunta" not in data:
        return {"status": "no question"}

    message = data["pregunta"]

    if not message:
        return {"status": "no text"}

    # Procesar mensaje y generar respuesta
    response_text = await process_message("", message)

    return {"respuesta": response_text}
