"""Script para indexar los documentos técnicos en ChromaDB."""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.rag.document_loader import load_and_index_documents


def main():
    docs_dir = PROJECT_ROOT / "data" / "documentos"
    print("Indexando documentos tecnicos...")
    try:
        count = load_and_index_documents(str(docs_dir))
        print(f"Se indexaron {count} chunks exitosamente.")
        print("Se soportan archivos .md, .txt, .json y .docx.")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("   Asegurate de colocar los documentos en data/documentos/")
    except ValueError as e:
        print(f"Error: {e}")
    except RuntimeError as e:
        print(f"Error: {e}")
        print("   Revisá que OPENAI_API_KEY en .env sea una key válida.")


if __name__ == "__main__":
    main()
