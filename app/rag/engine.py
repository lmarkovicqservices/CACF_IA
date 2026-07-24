from pathlib import Path
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from app.config import get_settings

try:
    from langchain_community.vectorstores import Chroma
except ImportError:  # pragma: no cover - optional dependency for local testing
    Chroma = None

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

    def __init__(self, docs_path: str | None = None, use_chroma: bool = True):
        settings = get_settings()
        self.docs_path = Path(docs_path or settings.chroma_persist_dir)
        self.use_chroma = use_chroma
        self.embeddings = OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            openai_api_key=settings.openai_api_key,
        )

        if not self.use_chroma:
            self.vectorstore = None
            self.qa_chain = None
            return

        if Chroma is None:
            self.vectorstore = None
            self.qa_chain = None
            return

        try:
            self.vectorstore = Chroma(
                collection_name=settings.chroma_collection_name,
                embedding_function=self.embeddings,
                persist_directory=settings.chroma_persist_dir,
            )
        except Exception:
            self.vectorstore = None
            self.qa_chain = None
            return

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
        if self.use_chroma and self.qa_chain is not None:
            result = await self.qa_chain.ainvoke({"query": question})
            return result["result"]

        if self.docs_path.exists() and self.docs_path.is_dir():
            matches = []
            for path in self.docs_path.glob("**/*"):
                if path.is_file() and path.suffix.lower() in {".md", ".txt", ".json"}:
                    text = path.read_text(encoding="utf-8")
                    lowered = text.lower()
                    if question.lower() in lowered or any(keyword in lowered for keyword in ["silaje", "forraje", "ensilado", "earlage"]):
                        matches.append((path.name, text))

            if matches:
                snippets = []
                for name, text in matches[:3]:
                    sentence = text.strip().splitlines()[0] if text.strip() else ""
                    snippets.append(f"- {name}: {sentence}")
                return (
                    "Respuesta basada en documentos locales:\n"
                    + "\n".join(snippets)
                )

        return (
            "No pude encontrar una respuesta suficiente en la base de conocimiento. "
            "Podés volver a intentarlo o consultar al equipo técnico de CACF."
        )


# Singleton
_engine: RAGEngine | None = None


def get_rag_engine() -> RAGEngine:
    global _engine
    if _engine is None:
        _engine = RAGEngine()
    return _engine
