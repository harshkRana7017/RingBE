from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from routers import calls, auth

app = FastAPI()

origins = [
    "http://localhost:5173",  # React app
    "http://localhost:8000",  # FastAPI app (if you ever need to call APIs from the same origin)
    # Add other origins as needed
]

app.add_middleware(CORSMiddleware, 
                   allow_origins=origins, 
                   allow_credentials=True, 
                   allow_methods=["*"],
                   allow_headers=["*"]
                   )

app.include_router(calls.router)
app.include_router(auth.router)

