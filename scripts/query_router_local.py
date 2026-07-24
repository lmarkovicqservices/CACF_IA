"""Router local de consultas: decide entre RAG y APIs sin usar WhatsApp.

Uso:
    python scripts/query_router_local.py "consulta"
    python scripts/query_router_local.py --pretty "consulta"
    python scripts/query_router_local.py
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.agent.router import classify_intent, format_pricing_response
from app.pricing.client import get_pricing_client
from app.rag.engine import get_rag_engine

PRICING_INTENTS = {
    "precios_referencia",
    "costos_silaje",
    "costo_materia_seca",
    "costos_transporte",
}


def _build_success(
    *,
    question: str,
    intent: str,
    route: str,
    source: str,
    answer: str,
    raw_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "ok": True,
        "question": question,
        "intent": intent,
        "route": route,
        "source": source,
        "answer": answer,
        "error": None,
        "raw_data": raw_data,
    }


def _build_error(
    *,
    question: str,
    intent: str | None,
    route: str,
    source: str,
    error: str,
) -> dict[str, Any]:
    return {
        "ok": False,
        "question": question,
        "intent": intent,
        "route": route,
        "source": source,
        "answer": "",
        "error": error,
        "raw_data": None,
    }


async def _resolve_pricing(intent: str) -> dict[str, Any]:
    pricing = get_pricing_client()

    if intent == "precios_referencia":
        return await pricing.get_precios_referencia()
    if intent == "costos_silaje":
        return await pricing.get_costos_silaje()
    if intent == "costo_materia_seca":
        return await pricing.get_costo_materia_seca()
    if intent == "costos_transporte":
        return await pricing.get_costos_transporte_mv()

    return await pricing.get_precios_referencia()


async def route_query(message: str) -> dict[str, Any]:
    question = message.strip()
    if not question:
        return _build_error(
            question=message,
            intent=None,
            route="invalid_input",
            source="local_router",
            error="La consulta no puede estar vacia.",
        )

    try:
        intent = await classify_intent(question)
    except Exception as exc:
        return _build_error(
            question=question,
            intent=None,
            route="classification",
            source="openai_intent_classifier",
            error=f"Error al clasificar la intencion: {exc}",
        )

    if intent == "saludo":
        greeting = (
            "¡Hola! Soy el asistente tecnico de CACF.\n\n"
            "Puedo ayudarte con:\n"
            "- Consultas tecnicas sobre ensilado, earlage, henolaje\n"
            "- Precios de referencia\n"
            "- Costos de silaje y materia seca\n"
            "- Costos de transporte\n\n"
            "¿En que puedo ayudarte?"
        )
        return _build_success(
            question=question,
            intent=intent,
            route="greeting",
            source="router_template",
            answer=greeting,
        )

    if intent == "tecnico":
        try:
            engine = get_rag_engine()
            answer = await engine.query(question)
            return _build_success(
                question=question,
                intent=intent,
                route="rag",
                source="chroma_rag",
                answer=answer,
            )
        except Exception as exc:
            return _build_error(
                question=question,
                intent=intent,
                route="rag",
                source="chroma_rag",
                error=f"Error consultando RAG: {exc}",
            )

    if intent in PRICING_INTENTS:
        try:
            data = await _resolve_pricing(intent)
            answer = format_pricing_response(data, intent)
            return _build_success(
                question=question,
                intent=intent,
                route="pricing",
                source="cacf_pricing_api",
                answer=answer,
                raw_data=data,
            )
        except Exception as exc:
            return _build_error(
                question=question,
                intent=intent,
                route="pricing",
                source="cacf_pricing_api",
                error=f"Error consultando API de precios: {exc}",
            )

    # Fallback defensivo para intenciones desconocidas.
    try:
        engine = get_rag_engine()
        answer = await engine.query(question)
        return _build_success(
            question=question,
            intent=intent,
            route="rag_fallback",
            source="chroma_rag",
            answer=answer,
        )
    except Exception as exc:
        return _build_error(
            question=question,
            intent=intent,
            route="rag_fallback",
            source="chroma_rag",
            error=f"Error en fallback RAG: {exc}",
        )


def _print_pretty(result: dict[str, Any]) -> None:
    status = "OK" if result["ok"] else "ERROR"
    print(f"Estado: {status}")
    print(f"Intent: {result['intent']}")
    print(f"Ruta: {result['route']}")
    print(f"Fuente: {result['source']}")
    print("\nConsulta:")
    print(result["question"])

    if result["ok"]:
        print("\nRespuesta:")
        print(result["answer"])
    else:
        print("\nError:")
        print(result["error"])


def _print_json(result: dict[str, Any]) -> None:
    print(json.dumps(result, ensure_ascii=False))


async def _run_single(message: str, pretty: bool) -> int:
    result = await route_query(message)
    if pretty:
        _print_pretty(result)
    else:
        _print_json(result)
    return 0 if result["ok"] else 1


async def _run_interactive(pretty: bool) -> int:
    print("Modo interactivo. Escribi tu consulta (salir para terminar).")

    while True:
        message = input("\nConsulta> ").strip()
        if not message:
            print("La consulta no puede estar vacia.")
            continue

        if message.lower() in {"salir", "exit", "quit"}:
            print("Sesion finalizada.")
            return 0

        result = await route_query(message)
        if pretty:
            _print_pretty(result)
        else:
            _print_json(result)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Enruta consultas a RAG o API de precios sin usar WhatsApp."
    )
    parser.add_argument(
        "message",
        nargs="*",
        help="Texto de la consulta. Si se omite, entra en modo interactivo.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Muestra salida legible en lugar de JSON.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    message = " ".join(args.message).strip()

    if message:
        raise SystemExit(asyncio.run(_run_single(message, args.pretty)))

    raise SystemExit(asyncio.run(_run_interactive(args.pretty)))


if __name__ == "__main__":
    main()
