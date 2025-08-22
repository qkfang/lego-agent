import asyncio
from app import main, runProgram, main_with_continuous_connection, run_program_with_auto_reconnect, is_connected
from uvicorn import Config, Server
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/exec")
async def exec_script(request: Request):
    script = await request.body()
    # print(script)
    if script:
        # Use the auto-reconnect version for better reliability
        success = await run_program_with_auto_reconnect(script)
        return {"status": "done" if success else "failed"}
    return {"status": "no_script"}


@app.get("/status")
async def status():
    return {
        "scan": "ok",
        "connected": is_connected(),
        "status": "connected" if is_connected() else "searching"
    }


async def run_uvicorn():
    config = Config(app, host="0.0.0.0", port=8001, loop="asyncio")
    server = Server(config)
    await server.serve()

async def main_concurrent():
    await asyncio.gather(
        main_with_continuous_connection(),
        run_uvicorn()
    )

asyncio.run(main_concurrent())

