from fastapi import FastAPI

app = FastAPI(
    title="Backend API 2",
    description="Segunda API conectada mediante API Gateway"
)


@app.get("/health")
def health():
    return {
        "status": "OK",
        "service": "Backend API 2"
    }


@app.get("/productos")
def productos():
    return {
        "productos": [
            {"id": 1, "nombre": "Mouse", "precio": 25000},
            {"id": 2, "nombre": "Audifonos", "precio": 50000},
            {"id": 3, "nombre": "Webcam", "precio": 40000}
        ]
    }


@app.get("/ordenes")
def ordenes():
    return {
        "ordenes": [
            {"id": 2001, "status": "pagada"},
            {"id": 2002, "status": "pendiente"}
        ]
    }