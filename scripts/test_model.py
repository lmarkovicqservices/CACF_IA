import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.agent.router import process_message


async def main() -> None:
    message = input("Escribí el mensaje para probar el modelo: ").strip()
    if not message:
        print("No se ingresó ningún mensaje.")
        return

    response = await process_message("5491112345678", message)
    print("\nRespuesta:\n")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
