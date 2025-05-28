from fastapi import FastAPI
from app.routers import wiki , project_list
app = FastAPI()

app.include_router(project_list.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI app!"}
