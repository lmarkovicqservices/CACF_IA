"""Prueba manual del retrieval del RAG sobre los documentos reales, sin usar OpenAI.

Carga y trocea los documentos de data/documentos/ y busca los chunks más
relevantes para una pregunta por coincidencia de palabras clave. No genera
una respuesta en lenguaje natural (eso requiere el LLM) ni usa embeddings
semánticos: sirve para validar que la carga e indexación de documentos
encuentra el contenido correcto antes de gastar cuota de OpenAI.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.rag.document_loader import load_and_chunk_documents
from app.rag.keyword_retrieval import search


def main() -> None:
    docs_dir = PROJECT_ROOT / "data" / "documentos"
    print(f"Cargando documentos de {docs_dir} ...")
    chunks = load_and_chunk_documents(str(docs_dir))
    print(f"{len(chunks)} chunks disponibles.\n")

    while True:
        pregunta = input("Pregunta (enter vacío para salir): ").strip()
        if not pregunta:
            break

        resultados = search(pregunta, chunks)
        if not resultados:
            print("Sin coincidencias.\n")
            continue

        for score, chunk in resultados:
            fuente = chunk.metadata.get("source_file", "?")
            print(f"\n--- {fuente} (score={score}) ---")
            print(chunk.page_content[:400].strip())
        print()


if __name__ == "__main__":
    main()
