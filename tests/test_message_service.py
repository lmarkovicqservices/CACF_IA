import pytest
from openai import AuthenticationError

from app.agent import router
from app.services.message_service import MessageService


class FakeClassifier:
    def __init__(self, intent: str):
        self.intent = intent

    async def __call__(self, message: str) -> str:
        return self.intent


class FakeRAG:
    async def query(self, question: str) -> str:
        return "respuesta técnica desde el RAG"


class FailingRAG:
    async def query(self, question: str) -> str:
        raise RuntimeError("sin contexto")


class FakePricingClient:
    async def get_precios_referencia(self) -> dict:
        return {"valor": 100}


@pytest.mark.asyncio
async def test_handle_message_returns_rag_answer_for_technical_queries():
    service = MessageService(
        intent_classifier=FakeClassifier("tecnico"),
        rag_engine=FakeRAG(),
        pricing_client=FakePricingClient(),
    )

    response = await service.handle_message("5491112345678", "¿Cómo se arma un silaje?")

    assert "respuesta técnica desde el RAG" in response


@pytest.mark.asyncio
async def test_handle_message_returns_fallback_when_rag_fails():
    service = MessageService(
        intent_classifier=FakeClassifier("tecnico"),
        rag_engine=FailingRAG(),
        pricing_client=FakePricingClient(),
    )

    response = await service.handle_message("5491112345678", "¿Cómo se arma un silaje?")

    assert "No pude encontrar una respuesta" in response


@pytest.mark.asyncio
async def test_classify_intent_falls_back_when_openai_auth_fails(monkeypatch):
    class FailingAsyncOpenAI:
        def __init__(self, *args, **kwargs):
            raise AuthenticationError("invalid api key", response=None, body=None)

    monkeypatch.setattr(router.openai, "AsyncOpenAI", FailingAsyncOpenAI)

    intent = await router.classify_intent("¿Cómo se arma un silaje?")

    assert intent == "tecnico"
