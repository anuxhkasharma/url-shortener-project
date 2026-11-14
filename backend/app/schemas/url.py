from pydantic import BaseModel, HttpUrl


class URLCreate(BaseModel):
    long_url: HttpUrl


class URLResponse(BaseModel):
    short_code: str
    short_url: str
    long_url: str