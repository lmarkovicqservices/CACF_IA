import pytest

from app.rag.engine import RAGEngine


@pytest.mark.asyncio
async def test_rag_engine_answers_from_local_documents(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "guia_silaje.md").write_text(
        "El silaje se arma mezclando forraje húmedo, compactando bien la masa y cerrando el silo para evitar la entrada de aire.",
        encoding="utf-8",
    )

    engine = RAGEngine(docs_path=str(docs_dir), use_chroma=False)
    answer = await engine.query("¿Cómo se arma un silaje?")

    assert "silaje" in answer.lower() or "forraje" in answer.lower()
