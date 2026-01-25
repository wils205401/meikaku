import socket

import os
import debugpy

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router

if os.getenv("DEBUG", "false").lower() == "true":
    debugpy.listen(("0.0.0.0", 5678))
    print("Debugger listening on port 5678")

app = FastAPI(title="Meikaku API")

app.include_router(auth_router)


# Detect local IP dynamically
def get_local_ip():
    """Return the LAN IP of the current machine."""
    # Create a UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to public DNS server provided by google
        # Does not have to be reachable, just get local IP
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except Exception:
        # Local loopback interface which allows computer to communicate with itself
        local_ip = "127.0.0.1"
    finally:
        s.close()

    return local_ip


local_ip = get_local_ip()

origins = [
    "http://localhost:8081",  # Expo Web
    f"exp://{local_ip}:8081",  # expo go mobile metro bundler (dynamic local ip address + port)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message:": "Meikaku API is running",
        "local_ip": local_ip,
        "allowed_origins": origins,
    }
