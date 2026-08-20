from fastapi import FastAPI
app = FastAPI()
@app.get("/",tags=["Root"], summary="Root endpoint")
def hello():
    return {"message": "hell world!"}
@app.get("/hello", tags=["hello"], summary="hello endpoint")
def hello_name():
    return {"message": "Hello from FastAPI!"}
