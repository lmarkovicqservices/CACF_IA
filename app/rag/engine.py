from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from app.config import get_settings

SYSTEM_TEMPLATE = """Eres un asistente técnico especializado en ensilado, earlage, henolaje y henificación
para la Cámara Argentina de Contratistas Forrajeros (CACF).

Responde de forma clara, técnica pero accesible. Si no encuentras la respuesta en el contexto proporcionado,
indica que no tienes esa información y sugiere contactar al equipo técnico de CACF.

Contexto recuperado:
{context}

Pregunta del socio: {question}

Respuesta:"""

PROMPT = PromptTemplate(
    template=SYSTEM_TEMPLATE, input_variables=["context", "question"]
)


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
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 5}),
            chain_type_kwargs={"prompt": PROMPT},
        )

    async def query(self, question: str) -> str:
        """Ejecuta una consulta técnica contra la base de conocimiento."""
        result = await self.qa_chain.ainvoke({"query": question})
        return result["result"]


# Singleton
_engine: RAGEngine | None = None


def get_rag_engine() -> RAGEngine:
    global _engine
    if _engine is None:
        _engine = RAGEngine()
    return _engine
