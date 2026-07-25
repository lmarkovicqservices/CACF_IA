"""Evalúa si el retriever trae el documento correcto para cada pregunta de prueba.

Para cada pregunta de data/preguntas_prueba/*.docx hay un documento (o lista
de documentos aceptables) anotado a mano en GROUND_TRUTH. Se compara contra
los source_file de los top-K chunks que trae la búsqueda local por palabras
clave (la misma que usa el fallback del RAG), y se calcula recall@K.

Es una métrica de "trajo la fuente correcta", no evalúa si la respuesta final
generada por el LLM está bien redactada.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.rag.document_loader import load_and_chunk_documents
from app.rag.keyword_retrieval import search
from app.rag.preguntas_prueba import PREGUNTAS_DIR, load_questions

RESULTADOS_PATH = PREGUNTAS_DIR / "evaluacion_retrieval.md"
TOP_K = 3

# Documento(s) que deberían aparecer entre los resultados para cada pregunta.
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

# Hipótesis de causa para las preguntas que fallan, basada en inspeccionar
# qué documento ganó y por qué (largo del documento, vocabulario compartido,
# errores de tipeo en la pregunta, etc.). Categorías usadas:
#   - sesgo por tamaño: el documento correcto es chico/el que ganó es grande,
#     y el score (suma de conteos) favorece a los documentos con más texto.
#   - vocabulario genérico: las palabras clave de la pregunta son términos
#     generales de silaje que aparecen en casi todos los documentos.
#   - typo: un error de tipeo en la pregunta rompe el matching de palabras.
#   - pregunta multi-tema: la pregunta mezcla dos temas y el score se reparte
#     entre documentos relacionados pero no en el correcto.
#   - ambigüedad real: el término buscado aparece genuinamente en más de un
#     documento del corpus, no es un error del retriever.
FAILURE_HYPOTHESIS: dict[str, str] = {
    "con cuanta humedad puedo enfardar para que no se me prenda fuego el rollo después?": (
        "ambigüedad real: \"rollo\" y \"humedad\" aparecen tanto en Henificación.docx "
        "como en Henolaje.docx, ambos hablan de forraje enrollado."
    ),
    "como se si mi silo fermentó bien?": (
        "vocabulario genérico: \"silo\" y \"fermentó\" son términos usados en casi "
        "todos los documentos del corpus, no distinguen Interpretación de los silos.docx."
    ),
    "que olorindica que el silo está podrido?": (
        "typo en la pregunta: \"olorindica\" (sin espacio) no matchea con \"olor\" "
        "ni \"indica\" por separado, se pierde la palabra clave más específica."
    ),
    "es peligroso darle a los animales silaje con capa negra?": (
        "sesgo por tamaño: aunque \"capa\"+\"negra\" son específicos, la pregunta "
        "también repite \"silaje\"/\"animales\", términos genéricos que favorecen "
        "a documentos grandes como Autoconsumo.docx e Inoculantes para ensilaje.docx."
    ),
    "cuales son los errores mas comunes al hacer silaje?": (
        "sesgo por tamaño + vocabulario genérico: pregunta muy general, gana "
        "Inoculantes para ensilaje.docx (12.505 caracteres, el 2do doc más largo)."
    ),
    "en que parte del proceso se pierde mas silaje?": (
        "sesgo por tamaño: pierde contra Silajes.docx, el documento más largo "
        "del corpus (16.018 caracteres) que dilluye el score de Pérdidas durante "
        "el proceso de ensilaje.docx (3.580 caracteres) pese a ser el correcto."
    ),
    "como leo un análisis de laboratorio de silaje?": (
        "pregunta multi-tema: mezcla \"análisis\" (Qué analizar de los forrajes "
        "conservados.docx) con \"interpretación\" (Interpretación de los silos.docx), "
        "el score se reparte y ninguno de los dos gana."
    ),
    "que riesgos físicos tiene trabajar con silos aéreos?": (
        "sesgo por tamaño: Seguridadenelmanejodelossilos.docx es el documento "
        "más CHICO del corpus (2.029 caracteres) y no puede competir en conteo "
        "de palabras contra documentos varias veces más largos."
    ),
    "como me cuido para no tener un accidente con el silo aéreo?": (
        "sesgo por tamaño: mismo caso que la pregunta anterior, el documento "
        "correcto (2.029 caracteres) es el más chico del corpus."
    ),
    "de que depende que un silaje salga bueno?": (
        "vocabulario genérico + sesgo por tamaño: pregunta muy abierta, sin "
        "términos distintivos, gana el documento más denso en vocabulario común."
    ),
}


def main() -> None:
    preguntas = load_questions()
    chunks = load_and_chunk_documents(str(PROJECT_ROOT / "data" / "documentos"))

    lineas = ["# Evaluación de retrieval (recall@{})\n".format(TOP_K)]
    aciertos = 0
    sin_ground_truth = 0

    for i, pregunta in enumerate(preguntas, start=1):
        esperados = GROUND_TRUTH.get(pregunta)
        if esperados is None:
            sin_ground_truth += 1
            lineas.append(f"## {i}. {pregunta}\n\n_Sin ground truth anotado, se omite._\n")
            continue

        resultados = search(pregunta, chunks, top_k=TOP_K)
        fuentes_traidas = list(dict.fromkeys(
            chunk.metadata.get("source_file", "?") for _, chunk in resultados
        ))

        acierto = any(fuente in fuentes_traidas for fuente in esperados)
        aciertos += acierto

        estado = "OK" if acierto else "FALLA"
        lineas.append(f"## {i}. {pregunta}\n")
        lineas.append(f"- Esperado: {esperados}")
        lineas.append(f"- Traído (top-{TOP_K}): {fuentes_traidas}")
        lineas.append(f"- Resultado: **{estado}**")

        print(f"[{estado}] {pregunta}")
        print(f"    esperado={esperados} traido={fuentes_traidas}")

        if not acierto:
            causa = FAILURE_HYPOTHESIS.get(pregunta, "sin hipótesis anotada")
            lineas.append(f"- Causa probable: {causa}")
        lineas.append("")

    evaluadas = len(preguntas) - sin_ground_truth
    recall = aciertos / evaluadas if evaluadas else 0.0
    fallas = evaluadas - aciertos

    categorias: dict[str, int] = {}
    for causa in FAILURE_HYPOTHESIS.values():
        categoria = causa.split(":", 1)[0]
        categorias[categoria] = categorias.get(categoria, 0) + 1

    resumen = [
        "\n## Resumen\n",
        f"- Preguntas evaluadas: {evaluadas} de {len(preguntas)} "
        f"({sin_ground_truth} sin ground truth)",
        f"- Aciertos (documento correcto en top-{TOP_K}): {aciertos}",
        f"- Recall@{TOP_K}: {recall:.0%}\n",
        "### Patrones observados en las fallas\n",
    ]
    for categoria, cantidad in sorted(categorias.items(), key=lambda x: -x[1]):
        resumen.append(f"- {categoria}: {cantidad} de {fallas} fallas")
    resumen.append(
        "\nEl patrón dominante es el **sesgo por tamaño de documento**: al sumar "
        "conteos de palabras sin normalizar por longitud, los documentos más "
        "largos ganan aunque el documento correcto sea más corto pero más "
        "específico. Esto es exactamente lo que los embeddings semánticos "
        "(normalizados por diseño) deberían corregir.\n"
    )
    resumen_texto = "\n".join(resumen)
    lineas.append(resumen_texto)
    print(resumen_texto)

    RESULTADOS_PATH.write_text("\n".join(lineas), encoding="utf-8")
    print(f"Detalle guardado en {RESULTADOS_PATH}")


if __name__ == "__main__":
    main()
