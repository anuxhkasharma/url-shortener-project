import secrets
import redis
import string
from app.core.redis_client import redis_client

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import Base, engine, get_db
from app.models.url import URL
from app.schemas.url import URLCreate, URLResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title="LinkTrim API")

ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 6
MAX_RETRIES = 5


def generate_short_code() -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(CODE_LENGTH))


@app.get("/")
def home():
    return {"message": "LinkTrim API chal rahi hai!"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/shorten", response_model=URLResponse)
def shorten(payload: URLCreate, db: Session = Depends(get_db)):
    long_url = str(payload.long_url)

    for _ in range(MAX_RETRIES):
        code = generate_short_code()
        db.add(URL(short_code=code, long_url=long_url))
        try:
            db.commit()
        except IntegrityError:
            
            db.rollback()
            continue
        return URLResponse(
            short_code=code,
            short_url=f"{settings.base_url}/{code}",
            long_url=long_url,
        )

    raise HTTPException(status_code=500, detail="Could not generate a unique code")




@app.get("/{short_code}")
def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    cache_key = f"url:{short_code}"

    
    try:
        cached = redis_client.get(cache_key)
    except redis.RedisError:
        cached = None  

    if cached:
        return RedirectResponse(url=cached, status_code=307)  

    
    url = db.scalar(select(URL).where(URL.short_code == short_code))
    if url is None:
        raise HTTPException(status_code=404, detail="Short link not found")

    
    try:
        redis_client.setex(cache_key, settings.cache_ttl_seconds, url.long_url)
    except redis.RedisError:
        pass

    return RedirectResponse(url=url.long_url, status_code=307)