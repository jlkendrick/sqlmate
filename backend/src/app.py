from utils.constants import PORT

import uvicorn
from routers import auth, users, query

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

appy = FastAPI()
appy.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://sqlmate-ruddy.vercel.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@appy.route("/")
def home():
    return "Hello, world!"

appy.include_router(router=auth.router, prefix="/auth")
appy.include_router(router=users.router, prefix="/users")
appy.include_router(router=query.router, prefix="/query")

if __name__ == "__main__":
    port = PORT
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)