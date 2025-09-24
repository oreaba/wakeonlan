import os
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from datetime import datetime

from oreaba_wol import send_wol
from dotenv import load_dotenv
from ping3 import ping

# Load .env file
load_dotenv()

# Environment variables
MAC_ADDRESS = os.getenv("MAC_ADDRESS")
TARGET_IP = os.getenv("TARGET_IP")        # for status check

app = FastAPI(title="Wake-on-LAN API", version="1.2")


class WakeRequest(BaseModel):
    mac_address: str | None = None
    broadcast_ip: str | None = None


@app.post("/wake")
async def wake_pc(request: WakeRequest):
    """
    Wake a PC using JSON body. Falls back to .env values if fields are missing.
    """
    try:
        mac = request.mac_address or MAC_ADDRESS
        send_wol(mac)
        return {"status": "success", "message": f"Magic packet sent to {mac} via 255.255.255.255:9"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/wake")
async def wake_default_pc():
    """
    Wake the default PC from .env settings.
    """
    try:
        send_wol(MAC_ADDRESS)
        return {"status": "success", "message": f"Magic packet sent to {mac} via 255.255.255.255:9"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/status")
async def check_status(ip: str | None = None):
    target = ip or TARGET_IP
    if not target:
        raise HTTPException(status_code=400, detail="No IP provided or configured")

    try:
        response_time = ping(target, timeout=2)  # seconds
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if response_time is not None:
            status = f"✅ online ({round(response_time*1000)} ms) @ {now}"
        else:
            status = f"❌ offline @ {now}"
        return {"ip": target, "status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/status/stream")
async def stream_status(ip: str | None = None, delay: int = 3, max_retries: int = 30):
    """
    Stream ping results every `delay` seconds until the PC is online or retries run out.
    Uses ping3 for cleaner response times.
    """
    target = ip or TARGET_IP
    if not target:
        raise HTTPException(status_code=400, detail="No IP provided or configured")

    async def event_generator():
        for attempt in range(1, max_retries + 1):
            try:
                response_time = ping(target, timeout=2)
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if response_time is not None:
                    status = f"✅ online ({round(response_time*1000)} ms)"
                    yield f'data: {{"time": "{now}", "ip": "{target}", "status": "{status}", "attempt": {attempt}}}\n\n'
                    break
                else:
                    status = "❌ offline"
                    yield f'data: {{"time": "{now}", "ip": "{target}", "status": "{status}", "attempt": {attempt}}}\n\n'
            except Exception as e:
                yield f'data: {{"time": "{now}", "ip": "{target}", "status": "error: {str(e)}", "attempt": {attempt}}}\n\n'

            await asyncio.sleep(delay)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/")
async def root():
    return {"message": "Wake-on-LAN API is running!"}
