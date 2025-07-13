from fastapi import FastAPI
from api.endpoint import router, load_all_mappings
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    load_all_mappings()
    yield
    # Shutdown code (if needed) can go here


app = FastAPI(
    title="Readmission Predictor API",
    description="Predict patient readmission",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)
