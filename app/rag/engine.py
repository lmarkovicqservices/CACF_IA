from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from app.config import get_settings

SYSTEM_TEMPLATE = """Eres un asistente técnico especializado en ensilado, earlage, henolaje y henificación
para la Cámara Argentina de Contratistas Forrajeros (CACF).

Responde de forma clara, técnica pero accesible. Si no encuentras la respuesta en el contexto proporcionado,
indica que no tienes esa información y sugiere contactar al equipo técnico de CACF.

Contexto recuperado:
{context}

Pregunta del socio: {question}

Respuesta:"""

PROMPT = ChatPromptTemplate.from_template(SYSTEM_TEMPLATE)


def _format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


class RAGEngine:
    """Motor RAG para consultas técnicas sobre ensilado."""

    def __init__(self):
        settings = get_settings()
        self.embeddings = OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            openai_api_key=settings.openai_api_key,
        )
        self.vectorstore = Chroma(
            collection_name=settings.chroma_collection_name,
            embedding_function=self.embeddings,
            persist_directory=settings.chroma_persist_dir,
        )
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            openai_api_key=settings.openai_api_key,
            temperature=0.2,
        )
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})
        self.chain = (
            {"context": retriever | _format_docs, "question": RunnablePassthrough()}
            | PROMPT
            | self.llm
            | StrOutputParser()
        )

    async def query(self, question: str) -> str:
        """Ejecuta una consulta técnica contra la base de conocimiento."""
        return await self.chain.ainvoke(question)


# Singleton
_engine: RAGEngine | None = None


def get_rag_engine() -> RAGEngine:
    global _engine
    if _engine is None:
        _engine = RAGEngine()
    return _engine
