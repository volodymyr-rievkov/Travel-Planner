from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import time
import services, database

router = APIRouter(tags=["System"])

@router.get("/health")
async def health_check(db: Session = Depends(database.get_db)):
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {"database": "unhealthy", "external_api": "unhealthy"}
    }
    try:
        db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "healthy"
    except Exception:
        health_status["status"] = "unhealthy"

    try:
        if await services.validate_artwork(129693):
            health_status["services"]["external_api"] = "healthy"
    except Exception:
        health_status["status"] = "unhealthy"

    if health_status["status"] != "healthy":
        raise HTTPException(status_code=503, detail=health_status)
    return health_status