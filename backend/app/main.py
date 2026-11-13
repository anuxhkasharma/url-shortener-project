from fastapi import FastAPI

app = FastAPI(title="LinkTrim API")


@app.get("/")
def home():
    return {"message": "LinkTrim API chal rahi hai!"}


@app.get("/health")
def health():
    return {"status": "ok"}