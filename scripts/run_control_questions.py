"""Ejecuta preguntas de control contra el LLM y exporta resultados en CSV.

Uso:
    python scripts/run_control_questions.py
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.query_engine_as_member import query_as_member


def read_questions(input_path: Path) -> list[str]:
    """Lee preguntas del archivo, una por linea, ignorando lineas vacias."""
    if not input_path.exists():
        raise FileNotFoundError(f"No existe el archivo de entrada: {input_path}")

    questions: list[str] = []
    with input_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            question = line.strip()
            if question:
                questions.append(question)

    return questions


async def process_questions(questions: list[str]) -> list[dict[str, str]]:
    """Procesa cada pregunta contra el engine y devuelve filas para CSV."""
    rows: list[dict[str, str]] = []

    for idx, question in enumerate(questions, start=1):
        print(f"[{idx}/{len(questions)}] Consultando: {question}")

        try:
            result = await query_as_member(question)
            answer = str(result.get("answer", "")).strip()
        except Exception as exc:
            answer = f"ERROR: {exc}"

        rows.append(
            {
                "pregunta": question,
                "respuesta": answer,
            }
        )

    return rows


def write_csv(output_path: Path, rows: list[dict[str, str]]) -> None:
    """Escribe filas en formato CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["pregunta", "respuesta"])
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Lee preguntas de control, consulta al LLM como usuario y exporta pregunta/respuesta en CSV."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=REPO_ROOT / "data" / "preguntas_de_control.txt",
        help="Ruta del archivo de preguntas (una por linea).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "data" / "resultados_de_control.txt",
        help="Ruta del archivo de salida CSV.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    questions = read_questions(args.input)
    if not questions:
        raise SystemExit("No hay preguntas para procesar en el archivo de entrada.")

    rows = asyncio.run(process_questions(questions))
    write_csv(args.output, rows)

    print(f"\nSe exportaron {len(rows)} resultados a: {args.output}")


if __name__ == "__main__":
    main()
