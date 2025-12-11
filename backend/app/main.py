from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import auth, dashboard, sales, press, master, warehouse, mold, schedule, process, trace, admin

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/api/docs",           
    openapi_url="/api/openapi.json" 
)


# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(sales.router, prefix="/api/sales", tags=["sales"])
app.include_router(press.router, prefix="/api/press", tags=["press"])
app.include_router(master.router, prefix="/api/master", tags=["master"])
app.include_router(warehouse.router, prefix="/api/warehouse", tags=["warehouse"])
app.include_router(mold.router, prefix="/api/mold", tags=["mold"])
app.include_router(schedule.router, prefix="/api/schedule", tags=["schedule"])
app.include_router(process.router, prefix="/api/process", tags=["process"])
app.include_router(trace.router, prefix="/api/trace", tags=["trace"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])


@app.get("/")
async def root():
    return {
        "message": "Factory Database Portal API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
