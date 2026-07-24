"""Corre en batch las preguntas de prueba de data/preguntas_prueba/*.docx.

Para cada pregunta intenta el RAG completo (embeddings + LLM). Si falla
(por ejemplo por falta de cuota de OpenAI), cae a una búsqueda local por
palabras clave sobre los chunks reales, para no dejar la pregunta sin
ninguna respuesta.

Guarda los resultados en data/preguntas_prueba/resultados.md.
"""
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.rag.document_loader import load_and_chunk_documents
from app.rag.engine import get_rag_engine
from app.rag.keyword_retrieval import search
from app.rag.preguntas_prueba import PREGUNTAS_DIR, load_questions

RESULTADOS_PATH = PREGUNTAS_DIR / "resultados.md"
RESULTADOS_LIMPIO_PATH = PREGUNTAS_DIR / "respuestas_para_revision.md"


def buscar_local(pregunta: str, chunks) -> str:
    resultados = search(pregunta, chunks)

    if not resultados:
        return "_Sin coincidencias en la búsqueda local._"

    partes = []
    for score, chunk in resultados:
        fuente = chunk.metadata.get("source_file", "?")
        partes.append(f"**{fuente}** (score={score}):\n> {chunk.page_content[:400].strip()}")
    return "\n\n".join(partes)


async def main() -> None:
    preguntas = load_questions()
    if not preguntas:
        print(f"No se encontraron preguntas en {PREGUNTAS_DIR}")
        return

    print(f"{len(preguntas)} preguntas encontradas. Cargando chunks locales de respaldo...")
    chunks = load_and_chunk_documents(str(PROJECT_ROOT / "data" / "documentos"))
    engine = get_rag_engine()

    lineas = ["# Resultados de preguntas de prueba\n"]
    lineas_limpio = ["# Preguntas y respuestas para revisión\n"]

    for i, pregunta in enumerate(preguntas, start=1):
        print(f"[{i}/{len(preguntas)}] {pregunta}")
        try:
            respuesta = await engine.query(pregunta)
            modo = "RAG completo (LLM)"
        except Exception as e:
            respuesta = buscar_local(pregunta, chunks)
            modo = f"local sin LLM (fallback por error: {e})"

        lineas.append(f"## {i}. {pregunta}\n")
        lineas.append(f"_Modo: {modo}_\n")
        lineas.append(f"{respuesta}\n")

        lineas_limpio.append(f"## {i}. {pregunta}\n")
        lineas_limpio.append(f"{respuesta}\n")

    RESULTADOS_PATH.write_text("\n".join(lineas), encoding="utf-8")
    RESULTADOS_LIMPIO_PATH.write_text("\n".join(lineas_limpio), encoding="utf-8")
    print(f"\nResultados guardados en {RESULTADOS_PATH}")
    print(f"Versión para revisión externa guardada en {RESULTADOS_LIMPIO_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
