from fastapi import FastAPI

app = FastAPI(title="MyFitnessBot Web", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
	return {"status": "ok"}


@app.get("/readiness")
async def readiness() -> dict[str, str]:
	return {"status": "ready"}