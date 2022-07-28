import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.middleware.cors import CORSMiddleware
import uvicorn
import websockets.exceptions

from .settings import Settings
from .spot import SpotState


def create_app(settings: Settings, spot_state: SpotState) -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.WEB_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.websocket("/spot/state/ws")
    async def listen_spot_state(ws: WebSocket):
        await ws.accept()
        while True:
            await asyncio.sleep(1)
            try:
                await ws.send_json(spot_state.items())
            except (WebSocketDisconnect, websockets.exceptions.ConnectionClosedError):
                return

    return app


def run_server(
    settings: Settings,
    spot_state: SpotState,
):
    web_app = create_app(settings, spot_state)
    uvicorn.run(web_app, host=settings.WEB_HOST, port=settings.WEB_PORT)
