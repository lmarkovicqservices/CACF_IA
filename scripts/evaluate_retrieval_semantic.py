"""Evaluación de recall@K semántico del retriever (ChromaDB + embeddings).

Mide si el retriever trae el documento correcto para cada pregunta de control.
Requiere que data/documentos ya esté indexado (scripts/ingest_documents.py)
y que OPENAI_API_KEY tenga cuota disponible.

Uso:
    python scripts/evaluate_retrieval_semantic.py
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.rag.engine import get_rag_engine

TOP_K = 3

# Ground truth: mapeo pregunta → documento(s) que deberían aparecer en los resultados.
# Anotado a mano en base al tema de cada .docx en data/documentos/.
GROUND_TRUTH: dict[str, list[str]] = {
    "el silo autoconsumo conviene para el tambo?": ["Autoconsumo.docx"],
    "que cuidados hay que tener con el autoconsumo para que no pierda calidad?": ["Autoconsumo.docx"],
    "con que humedad se cosecha el earlage?": ["Earlage.docx"],
    "como es el proceso de henificación?": ["Henificación.docx"],
    "con cuanta humedad puedo enfardar para que no se me prenda fuego el rollo después?": ["Henificación.docx"],
    "cual es la diferencia entre henolaje y silaje?": ["Henolaje.docx", "Silajes.docx"],
    "a que humedad se hace el henolaje?": ["Henolaje.docx"],
    "Hay que tapar el silo? y que que pasa si lo tapo mal=": ["IMPORTANCIA DEL TAPADO DE LOS SILOS.docx"],
    "para que sirven los inoculantes en el silaje?": ["Inoculantes para ensilaje.docx"],
    "que inoculante me conviene usar?": ["Inoculantes para ensilaje.docx"],
    "como se si mi silo fermentó bien?": ["Interpretación de los silos.docx"],
    "que olorindica que el silo está podrido?": ["Interpretación de los silos.docx"],
    "que es la capa negra del silo?": ["La capa negra y sus consecuencias.docx"],
    "es peligroso darle a los animales silaje con capa negra?": ["La capa negra y sus consecuencias.docx"],
    "que son las micotoxinas?": ["micotoxinas.docx"],
    "como evito que se me formen micotoxinas?": ["micotoxinas.docx"],
    "cuales son los errores mas comunes al hacer silaje?": [
        "Pasos necesarios para la confección de silajes.docx",
        "Pérdidas durante el proceso de ensilaje.docx",
    ],
    "en que parte del proceso se pierde mas silaje?": ["Pérdidas durante el proceso de ensilaje.docx"],
    "que tengo que analizar en un forraje conservado?": ["Qué analizar de los forrajes conservados.docx"],
    "como leo un análisis de laboratorio de silaje?": [
        "Qué analizar de los forrajes conservados.docx",
        "Interpretación de los silos.docx",
    ],
    "que riesgos físicos tiene trabajar con silos aéreos?": ["Seguridadenelmanejodelossilos.docx"],
    "como me cuido para no tener un accidente con el silo aéreo?": ["Seguridadenelmanejodelossilos.docx"],
    "de que depende que un silaje salga bueno?": [
        "Silajes.docx",
        "Pasos necesarios para la confección de silajes.docx",
    ],
    "como tomo una muestra de silaje? y cada cuanto hay que muestrear?": ["Tomademuestras.docx"],
}

# Hipótesis de causa para las preguntas que fallan.
# Categorías:
#   - sesgo por tamaño: el documento correcto es chico / el que ganó es grande.
#   - vocabulario genérico: las palabras clave son términos generales de silaje.
#   - typo: un error de tipeo en la pregunta rompe el matching.
#   - pregunta multi-tema: la pregunta mezcla dos temas.
#   - ambigüedad real: el término aparece en más de un documento.
FAILURE_HYPOTHESIS: dict[str, str] = {
    "con cuanta humedad puedo enfardar para que no se me prenda fuego el rollo después?": (
        "ambigüedad real: 'rollo' y 'humedad' aparecen tanto en Henificación.docx "
        "como en Henolaje.docx, ambos hablan de forraje enrollado."
    ),
    "como se si mi silo fermentó bien?": (
        "vocabulario genérico: 'silo' y 'fermentó' son términos usados en casi "
        "todos los documentos del corpus."
    ),
    "que olorindica que el silo está podrido?": (
        "typo en la pregunta: 'olorindica' (sin espacio) no matchea con 'olor' "
        "ni 'indica' por separado."
    ),
    "es peligroso darle a los animales silaje con capa negra?": (
        "sesgo por tamaño: aunque 'capa'+'negra' son específicos, la pregunta "
        "también repite 'silaje'/'animales', términos genéricos que favorecen "
        "a documentos grandes."
    ),
    "cuales son los errores mas comunes al hacer silaje?": (
        "sesgo por tamaño + vocabulario genérico: pregunta muy general."
    ),
    "en que parte del proceso se pierde mas silaje?": (
        "sesgo por tamaño: pierde contra documentos más largos del corpus."
    ),
    "como leo un análisis de laboratorio de silaje?": (
        "pregunta multi-tema: mezcla 'análisis' con 'interpretación', "
        "el score se reparte entre documentos relacionados."
    ),
    "que riesgos físicos tiene trabajar con silos aéreos?": (
        "sesgo por tamaño: Seguridadenelmanejodelossilos.docx es el documento "
        "más chico del corpus y no puede competir en score."
    ),
    "como me cuido para no tener un accidente con el silo aéreo?": (
        "sesgo por tamaño: mismo caso, el documento correcto es el más chico."
    ),
    "de que depende que un silaje salga bueno?": (
        "vocabulario genérico + sesgo por tamaño: pregunta muy abierta."
    ),
}


def load_control_questions() -> list[str]:
    """Carga las preguntas de control desde el archivo de texto."""
    questions_path = PROJECT_ROOT / "data" / "preguntas_de_control.txt"
    if not questions_path.exists():
        return list(GROUND_TRUTH.keys())
    questions = []
    with questions_path.open("r", encoding="utf-8") as f:
        for line in f:
            q = line.strip()
            if q:
                questions.append(q)
    return questions


def main() -> None:
    preguntas = load_control_questions()
    engine = get_rag_engine()

    if engine.vectorstore is None:
        print("El vectorstore no está disponible.")
        print("Asegurate de correr: python scripts/ingest_documents.py")
        return

    print(f"Evaluando {len(preguntas)} preguntas con recall@{TOP_K} semántico...\n")
    aciertos = 0
    sin_ground_truth = 0
    fallas = []

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
        print(f"[{estado}] {pregunta}")
        print(f"    esperado={esperados} traido={fuentes_traidas}")

        if not acierto:
            causa = FAILURE_HYPOTHESIS.get(pregunta, "sin hipótesis anotada")
            fallas.append((pregunta, esperados, fuentes_traidas, causa))

    evaluadas = len(preguntas) - sin_ground_truth
    recall = aciertos / evaluadas if evaluadas else 0.0

    print(f"\n{'='*60}")
    print(f"RESUMEN")
    print(f"{'='*60}")
    print(f"Preguntas evaluadas: {evaluadas} de {len(preguntas)}")
    print(f"Aciertos (documento correcto en top-{TOP_K}): {aciertos}")
    print(f"Recall@{TOP_K}: {recall:.0%}")

    if fallas:
        print(f"\nFallas ({len(fallas)}):")
        for pregunta, esperado, traido, causa in fallas:
            print(f"  - {pregunta}")
            print(f"    Causa: {causa}")


if __name__ == "__main__":
    main()
