from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
import os
from controllers.auth import router as auth_router
from functions.auth import get_current_user_token
from functions.found_item_forms import router as found_item_router


app = FastAPI(
    title="api",
    version="1.0.0",
)

app.include_router(
    router=auth_router
)

app.include_router(
    router=found_item_router
)



@app.get("/protected")
async def protected_endpoint(
    request: Request,
    token_data: dict = Depends(get_current_user_token)
):
    return {"message": "OK", "user_id": token_data.get("user_id")}

raw_origins = os.getenv("CORS_ORIGINS", "")
allowed_origins = [
    origin.strip() for origin in raw_origins.split(",") if origin.strip()
]


default_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://frontendhack-eta.vercel.app",
]

all_origins = list(set(allowed_origins + default_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=all_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)



@app.get("/")
async def read_root():
    return {""}