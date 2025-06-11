import asyncio
from app import main, runProgram
from uvicorn import Config, Server
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/exec")
async def exec_script(request: Request):
    script = await request.body()
    # print(script)
    if script:
        await runProgram(script)
    return {"status": "done"}


@app.get("/status")
async def status():
    return {"scan": "ok"}


async def run_uvicorn():
    config = Config(app, host="0.0.0.0", port=8001, loop="asyncio")
    server = Server(config)
    await server.serve()

async def main_concurrent():
    await asyncio.gather(
        main(),
        run_uvicorn()
    )

asyncio.run(main_concurrent())

