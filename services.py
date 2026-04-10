import httpx
from fastapi import HTTPException

# Simple in-memory cache
api_cache = set()

async def validate_artwork(artwork_id: int):
    if artwork_id in api_cache:
        return True
    
    url = f"https://api.artic.edu/api/v1/artworks/{artwork_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=5.0)
            if response.status_code == 200:
                api_cache.add(artwork_id)
                return True
            return False
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Art Institute API is unavailable")
