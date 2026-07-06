"""Script para indexar los documentos técnicos en ChromaDB."""
import sys
sys.path.insert(0, ".")

from app.rag.document_loader import load_and_index_documents


def main():
    print("🔄 Indexando documentos técnicos...")
    try:
        count = load_and_index_documents("data/documentos")
        print(f"✅ Se indexaron {count} chunks exitosamente.")
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("   Asegurate de colocar los .docx en data/documentos/")
    except ValueError as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
