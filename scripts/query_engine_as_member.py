"""Consulta directa al engine como socio, sin webhook de WhatsApp con un input de texto. Útil para tests y debugging."""
import argparse
import asyncio
import json
import sys

sys.path.insert(0, ".")

from app.agent.router import classify_intent
from app.rag.engine import get_rag_engine


async def query_as_member(message: str) -> dict:
    """Clasifica la consulta y devuelve la respuesta del engine.

    Este flujo evita por completo la capa de WhatsApp y cualquier validación externa.
    """
    intent = await classify_intent(message)
    engine = get_rag_engine()
    answer = await engine.query(message)

    return {
        "intent": intent,
        "question": message,
        "answer": answer,
    }


async def _amain(message: str) -> None:
    result = await query_as_member(message)

    print("Intent detectado:", result["intent"])
    print("\nConsulta:")
    print(result["question"])
    print("\nRespuesta del engine:")
    print(result["answer"])


async def _amain_json(message: str) -> None:
    result = await query_as_member(message)
    print(json.dumps(result, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clasifica una consulta y obtiene respuesta del engine (sin WhatsApp/tokens)."
    )
    parser.add_argument(
        "message",
        nargs="*",
        help="Texto de la consulta. Si se omite, se solicita por stdin.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Imprime la salida en JSON (útil para tests automatizados).",
    )
    args = parser.parse_args()

    message = " ".join(args.message).strip()
    if not message:
        message = input("Escribi la consulta del socio: ").strip()

    if not message:
        raise SystemExit("La consulta no puede estar vacia.")

    if args.as_json:
        asyncio.run(_amain_json(message))
        return

    asyncio.run(_amain(message))


if __name__ == "__main__":
    main()
