import secrets
import string

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

app = FastAPI(title="LinkTrim API")

url_store: dict[str, str] = {}

BASE_URL = "http://127.0.0.1:8000"
ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 6


class URLCreate(BaseModel):
    long_url: HttpUrl


class URLResponse(BaseModel):
    short_code: str
    short_url: str
    long_url: str


def generate_short_code() -> str:
    
    while True:
        code = "".join(secrets.choice(ALPHABET) for _ in range(CODE_LENGTH))
        if code not in url_store:
            return code


@app.get("/")
def home():
    return {"message": "LinkTrim API chal rahi hai!"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/shorten", response_model=URLResponse)
def shorten(payload: URLCreate):
    code = generate_short_code()
    url_store[code] = str(payload.long_url)
    return URLResponse(
        short_code=code,
        short_url=f"{BASE_URL}/{code}",
        long_url=str(payload.long_url),
    )

@app.get("/{short_code}")
def redirect_to_url(short_code: str):
    long_url = url_store.get(short_code)
    if long_url is None:
        raise HTTPException(status_code=404, detail="Short link not found")
    return RedirectResponse(url=long_url, status_code=307)