from pathlib import Path
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from app.config import get_settings


def load_and_index_documents(docs_path: str = "data/documentos") -> int:
    """Carga documentos .docx y los indexa en ChromaDB.
    
    Retorna la cantidad de chunks indexados.
    """
    settings = get_settings()
    docs_dir = Path(docs_path)

    if not docs_dir.exists():
        raise FileNotFoundError(f"Directorio no encontrado: {docs_path}")

    # Cargar todos los .docx
    documents = []
    for docx_file in docs_dir.glob("**/*.docx"):
        loader = Docx2txtLoader(str(docx_file))
        docs = loader.load()
        # Agregar metadata del archivo fuente
        for doc in docs:
            doc.metadata["source_file"] = docx_file.name
            doc.metadata["topic"] = docx_file.parent.name
        documents.extend(docs)

    if not documents:
        raise ValueError(f"No se encontraron archivos .docx en {docs_path}")

    # Dividir en chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)

    # Indexar en ChromaDB
    embeddings = OpenAIEmbeddings(
        model=settings.openai_embedding_model,
        openai_api_key=settings.openai_api_key,
    )
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=settings.chroma_collection_name,
        persist_directory=settings.chroma_persist_dir,
    )

    return len(chunks)
