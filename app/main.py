import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from app.api.webhooks import router as webhook_router
from app.api.health import router as health_router

app = FastAPI(
    title="CACF IA - Asistente Técnico de Ensilado",
    description="Asistente WhatsApp para socios de la Cámara Argentina de Contratistas Forrajeros",
    version="0.1.0",
)

app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(webhook_router, prefix="/api", tags=["whatsapp"])


@app.on_event("startup")
async def startup_event():
    """Inicializa servicios al arrancar la aplicación."""
    # TODO: Inicializar ChromaDB, verificar conexión a APIs
    pass
