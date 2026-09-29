from fastapi import FastAPI

app = FastAPI(
    title="FanGap",
    description=(
        "Comparing critic scores versus player scores, "
        "and tracking how that gap changes over time."
    ),
    version="0.1.0",
)


@app.get("/")
def root():
    return {"name": "FanGap", "status": "ok"}


@app.get("/health")
def health():
    return {"status": "ok"}
