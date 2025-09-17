import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from wakeonlan import send_magic_packet
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Environment variables
MAC_ADDRESS = os.getenv("MAC_ADDRESS")
BROADCAST_IP = os.getenv("BROADCAST_IP")  # keep None if not set

app = FastAPI(title="Wake-on-LAN API", version="1.0")


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
        broadcast = request.broadcast_ip or BROADCAST_IP

        if not mac:
            raise HTTPException(status_code=400, detail="MAC address not provided")

        if broadcast:
            send_magic_packet(mac, ip_address=broadcast)
            msg = f"Magic packet sent to {mac} via {broadcast}"
        else:
            send_magic_packet(mac)
            msg = f"Magic packet sent to {mac} (no broadcast specified)"

        return {"status": "success", "message": msg}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/wake")
async def wake_default_pc():
    """
    Wake the default PC from .env settings.
    """
    try:
        if not MAC_ADDRESS:
            raise HTTPException(status_code=400, detail="Default MAC address not configured")
        if not BROADCAST_IP:
            raise HTTPException(status_code=400, detail="Broadcast IP not configured")

        send_magic_packet(MAC_ADDRESS, ip_address=BROADCAST_IP)
        msg = f"Magic packet sent to {MAC_ADDRESS} via {BROADCAST_IP}"

        return {"status": "success", "message": msg}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {"message": "Wake-on-LAN API is running!"}
