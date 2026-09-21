from fastapi import FastAPI

app = FastAPI(
    title="Backend API 1",
    description="Primera API conectada mediante API Gateway"
)


@app.get("/health")
def health():
    return {
        "status": "OK",
        "service": "Backend API 1"
    }


@app.get("/products")
def products():
    return {
        "products": [
            {"id": 1, "name": "Notebook", "price": 900000},
            {"id": 2, "name": "Monitor", "price": 250000},
            {"id": 3, "name": "Teclado", "price": 45000}
        ]
    }


@app.get("/orders")
def orders():
    return {
        "orders": [
            {"id": 1001, "status": "paid"},
            {"id": 1002, "status": "pending"},
            {"id": 1003, "status": "pending"}
        ]
    }