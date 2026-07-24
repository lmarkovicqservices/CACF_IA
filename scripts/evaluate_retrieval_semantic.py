"""Igual que evaluate_retrieval.py, pero mide recall@K con el retriever
semántico real (ChromaDB + embeddings de OpenAI) en vez de keyword search.

Requiere que data/documentos ya esté indexado (scripts/ingest_documents.py)
y que OPENAI_API_KEY tenga cuota disponible.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.rag.engine import get_rag_engine
from app.rag.preguntas_prueba import PREGUNTAS_DIR, load_questions
from evaluate_retrieval import GROUND_TRUTH, TOP_K

RESULTADOS_PATH = PREGUNTAS_DIR / "evaluacion_retrieval_semantico.md"
KEYWORD_RECALL_BASELINE = 0.58


def main() -> None:
    preguntas = load_questions()
    engine = get_rag_engine()

    if engine.vectorstore is None:
        print("El vectorstore no está disponible (revisá OPENAI_API_KEY y que se haya corrido ingest_documents.py).")
        return

    lineas = [f"# Evaluación de retrieval semántico (recall@{TOP_K})\n"]
    aciertos = 0
    sin_ground_truth = 0

    for i, pregunta in enumerate(preguntas, start=1):
        esperados = GROUND_TRUTH.get(pregunta)
        if esperados is None:
            sin_ground_truth += 1
            continue

        resultados = engine.vectorstore.similarity_search(pregunta, k=TOP_K)
        fuentes_traidas = list(dict.fromkeys(
            doc.metadata.get("source_file", "?") for doc in resultados
        ))

        acierto = any(fuente in fuentes_traidas for fuente in esperados)
        aciertos += acierto

        estado = "OK" if acierto else "FALLA"
        lineas.append(f"## {i}. {pregunta}\n")
        lineas.append(f"- Esperado: {esperados}")
        lineas.append(f"- Traído (top-{TOP_K}): {fuentes_traidas}")
        lineas.append(f"- Resultado: **{estado}**\n")

        print(f"[{estado}] {pregunta}")
        print(f"    esperado={esperados} traido={fuentes_traidas}")

    evaluadas = len(preguntas) - sin_ground_truth
    recall = aciertos / evaluadas if evaluadas else 0.0

    resumen = (
        f"\n## Resumen\n\n"
        f"- Preguntas evaluadas: {evaluadas} de {len(preguntas)}\n"
        f"- Aciertos (documento correcto en top-{TOP_K}): {aciertos}\n"
        f"- Recall@{TOP_K} semántico: {recall:.0%}\n"
        f"- Recall@{TOP_K} keyword (baseline anterior): {KEYWORD_RECALL_BASELINE:.0%}\n"
        f"- Mejora: {(recall - KEYWORD_RECALL_BASELINE) * 100:+.0f} puntos porcentuales\n"
    )
    lineas.append(resumen)
    print(resumen)

    RESULTADOS_PATH.write_text("\n".join(lineas), encoding="utf-8")
    print(f"Detalle guardado en {RESULTADOS_PATH}")


if __name__ == "__main__":
    main()
