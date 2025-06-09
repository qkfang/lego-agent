from fastapi import FastAPI, HTTPException, BackgroundTasks


app = FastAPI()

@app.get("/scan")
async def scan():
    return {"status": "found"}

@app.post("/upload")
async def upload():
    return {"status": "uploading"}

@app.get("/status")
async def status():
    return {"scan": "aaa"}
