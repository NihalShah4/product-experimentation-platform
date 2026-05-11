from fastapi import FastAPI

app = FastAPI(
    title="Product Experimentation Platform",
    description="API for product analytics, experimentation, and KPI monitoring.",
    version="0.1.0",
)

@app.get("/")
def home():
    return {"message": "Product Experimentation Platform API"}

@app.get("/health")
def health_check():
    return {"status": "running"}