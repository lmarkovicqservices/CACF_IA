"""Búsqueda simple por palabras clave sobre chunks, sin embeddings ni LLM.

Sirve como retrieval de respaldo cuando no hay cuota de OpenAI disponible,
y como base para evaluar la calidad del retrieval real.
"""
from langchain_core.documents import Document

MIN_WORD_LENGTH = 4


def search(pregunta: str, chunks: list[Document], top_k: int = 3) -> list[tuple[int, Document]]:
    """Devuelve los top_k chunks con más coincidencias de palabras clave."""
    palabras = [
        w.lower() for w in pregunta.replace("¿", "").replace("?", "").split()
        if len(w) >= MIN_WORD_LENGTH
    ]
    resultados = []
    for chunk in chunks:
        texto = chunk.page_content.lower()
        score = sum(texto.count(palabra) for palabra in palabras)
        if score > 0:
            resultados.append((score, chunk))
    resultados.sort(key=lambda item: -item[0])
    return resultados[:top_k]
