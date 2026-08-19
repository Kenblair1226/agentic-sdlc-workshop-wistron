from fastapi import FastAPI

from app.routers import products

app = FastAPI(
    title="Product Catalog",
    version="1.0.0",
    description="Sample API for the AI Coding Agent Workshop.",
)

app.include_router(products.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
