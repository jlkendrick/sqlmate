from utils.constants import PORT

import uvicorn
from routers import auth, users, query

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://sqlmate-ruddy.vercel.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return "Welcome to SQLMate API!"

app.include_router(router=auth.router, prefix="/auth")
app.include_router(router=users.router, prefix="/users")
app.include_router(router=query.router, prefix="/query")

if __name__ == "__main__":
    port = PORT
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)