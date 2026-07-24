"""Carga de las preguntas de prueba desde data/preguntas_prueba/*.docx."""
from pathlib import Path

import docx2txt

PREGUNTAS_DIR = Path(__file__).resolve().parents[2] / "data" / "preguntas_prueba"


def load_questions(preguntas_dir: Path = PREGUNTAS_DIR) -> list[str]:
    preguntas = []
    for path in sorted(preguntas_dir.glob("*.docx")):
        texto = docx2txt.process(str(path))
        for linea in texto.splitlines():
            linea = linea.strip()
            if linea:
                preguntas.append(linea)
    return preguntas
