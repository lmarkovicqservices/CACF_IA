from __future__ import annotations

from typing import Protocol


class IntentClassifier(Protocol):
    async def __call__(self, message: str) -> str:
        ...


class RAGEngine(Protocol):
    async def query(self, question: str) -> str:
        ...


class PricingClient(Protocol):
    async def get_precios_referencia(self) -> dict:
        ...

    async def get_costos_silaje(self) -> dict:
        ...

    async def get_costo_materia_seca(self) -> dict:
        ...

    async def get_costos_transporte_mv(self) -> dict:
        ...


class MessageService:
    """Servicio de aplicación para orquestar el flujo del asistente."""

    def __init__(self, intent_classifier: IntentClassifier, rag_engine: RAGEngine, pricing_client: PricingClient):
        self.intent_classifier = intent_classifier
        self.rag_engine = rag_engine
        self.pricing_client = pricing_client

    async def handle_message(self, phone_number: str, message: str) -> str:
        intent = await self.intent_classifier(message)

        if intent == "saludo":
            return (
                "¡Hola! Soy el asistente técnico de CACF. 🌾\n\n"
                "Puedo ayudarte con consultas técnicas, precios de referencia y costos."
            )

        if intent == "tecnico":
            try:
                return await self.rag_engine.query(message)
            except Exception:
                return (
                    "No pude encontrar una respuesta suficiente en la base de conocimiento. "
                    "Podés volver a intentarlo o consultar al equipo técnico de CACF."
                )

        try:
            if intent == "precios_referencia":
                data = await self.pricing_client.get_precios_referencia()
            elif intent == "costos_silaje":
                data = await self.pricing_client.get_costos_silaje()
            elif intent == "costo_materia_seca":
                data = await self.pricing_client.get_costo_materia_seca()
            elif intent == "costos_transporte":
                data = await self.pricing_client.get_costos_transporte_mv()
            else:
                data = await self.pricing_client.get_precios_referencia()

            return f"Información de precios:\n{data}"
        except Exception:
            return "No pude obtener la información de precios en este momento."
