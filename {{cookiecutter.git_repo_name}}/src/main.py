import uvicorn
from fastapi import FastAPI
from mangum import Mangum
from starlette.middleware.cors import CORSMiddleware

from src.api.api_v1.api import api_router
from src.core import settings, init_logging

init_logging(is_lambda=False, loggers=settings.logging)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.project_name, openapi_url=f"{settings.api_v1_str}/openapi.json"
)

# Set all CORS enabled origins
if settings.backend_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.backend_cors_origins.split(",")],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.api_v1_str)

# Uncomment to run inside AWS Lambda
# handler = Mangum(app)

logger.info("App init completed")


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True, log_config=None)
