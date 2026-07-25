from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.config import get_settings

try:
    from langchain_openai import OpenAIEmbeddings
except ImportError:  # pragma: no cover - optional dependency for local testing
    OpenAIEmbeddings = None

try:
    from langchain_community.vectorstores import Chroma
except ImportError:  # pragma: no cover - optional dependency for local testing
    Chroma = None

try:
    from langchain_community.document_loaders import Docx2txtLoader
except ImportError:  # pragma: no cover - optional dependency for local testing
    Docx2txtLoader = None


def _load_plain_text_documents(docs_dir: Path) -> List[Document]:
    documents: List[Document] = []
    for path in sorted(docs_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".md", ".txt", ".json"}:
            continue
        text = path.read_text(encoding="utf-8")
        documents.append(
            Document(
                page_content=text,
                metadata={"source_file": path.name, "topic": path.parent.name},
            )
        )
    return documents


def _load_docx_documents(docs_dir: Path) -> List[Document]:
    if Docx2txtLoader is None:
        return []

    documents: List[Document] = []
    for path in sorted(docs_dir.rglob("*.docx")):
        loader = Docx2txtLoader(str(path))
        loaded_docs = loader.load()
        for doc in loaded_docs:
            doc.metadata["source_file"] = path.name
            doc.metadata["topic"] = path.parent.name
            documents.append(doc)
    return documents


def load_and_chunk_documents(docs_path: str = "data/documentos") -> List[Document]:
    """Carga documentos .md/.txt/.json y .docx desde docs_path y los trocea en chunks.

    No requiere OpenAI ni ChromaDB: útil para inspeccionar o buscar sobre los
    documentos sin generar embeddings.
    """
    docs_dir = Path(docs_path)

    if not docs_dir.exists():
        raise FileNotFoundError(f"Directorio no encontrado: {docs_path}")

    documents = _load_plain_text_documents(docs_dir) + _load_docx_documents(docs_dir)

    if not documents:
        raise ValueError(f"No se encontraron archivos soportados en {docs_path}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(documents)


def load_and_index_documents(docs_path: str = "data/documentos") -> int:
    """Carga documentos .md/.txt/.json y .docx y los indexa en ChromaDB.

    Retorna la cantidad de chunks indexados.
    """
    settings = get_settings()
    chunks = load_and_chunk_documents(docs_path)

    if Chroma is None:
        raise RuntimeError("langchain_community no está instalado: no se puede indexar en ChromaDB.")

    if OpenAIEmbeddings is None:
        raise RuntimeError("langchain_openai no está instalado: no se pueden generar embeddings.")

    try:
        embeddings = OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            openai_api_key=settings.openai_api_key,
        )
        Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name=settings.chroma_collection_name,
            persist_directory=settings.chroma_persist_dir,
        )
    except Exception as e:
        raise RuntimeError(f"Fallo al generar embeddings o indexar en ChromaDB: {e}") from e

    return len(chunks)
