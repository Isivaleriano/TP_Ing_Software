from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY = "abcdef12345"
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(api_key: str = Security(api_key_header)):
    """Valida la API Key enviada en el header."""
    
    if api_key == API_KEY:
        return api_key
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Acceso denegado. API Key inválida o faltante en el header."
    )