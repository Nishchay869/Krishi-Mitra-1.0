"""
FastAPI Real-Time Plant Vision & IPM Advisory Server
Provides WebSocket endpoint (/ws/crop-diagnostics) and HTTP endpoint
for real-time leaf disease diagnostics, Laplacian focus rejection,
multi-class instance segmentation polygon streaming, and IPM advisory.
"""

import asyncio
import json
import logging
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from vision_engine import PlantVisionEngine, DiagnosticResponse
from advisory_matrix import SeverityStage, get_advisory

# Configure structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("CropVisionServer")

app = FastAPI(
    title="Krishi Mitra - Real-Time Plant Vision & IPM Advisory API",
    description="Digital pathology computer vision engine with real-time WebSocket streaming.",
    version="2.0.0"
)

# Enable CORS for web apps and dashboard integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate singleton vision engine
vision_engine = PlantVisionEngine()


class DiagnosticRequest(BaseModel):
    """HTTP payload for frame diagnostics."""
    frame: str = Field(..., description="Base64 encoded image frame or data URL")
    crop_hint: Optional[str] = Field("Tomato", description="Crop type context")
    target_hint: Optional[str] = Field(None, description="Suspected disease/pest hint")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Plant Vision & IPM Advisory Engine",
        "blur_threshold": vision_engine.BLUR_THRESHOLD,
        "onnx_accelerated": vision_engine.onnx_session is not None
    }


@app.post("/api/crop-vision/diagnose", response_model=DiagnosticResponse)
async def diagnose_frame_http(payload: DiagnosticRequest):
    """
    HTTP REST endpoint: Process a single frame and return comprehensive
    digital pathology metrics, segmentation polygons, and IPM prescriptions.
    """
    try:
        response = await asyncio.to_thread(
            vision_engine.analyze_frame,
            payload.frame,
            payload.target_hint
        )
        return response
    except Exception as e:
        logger.error(f"Error analyzing frame via HTTP: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/crop-diagnostics")
async def websocket_diagnostics_endpoint(
    websocket: WebSocket,
    crop: Optional[str] = Query("General"),
    target_hint: Optional[str] = Query(None)
):
    """
    Full WebSocket streaming endpoint (/ws/crop-diagnostics).
    Accepts continuous binary or base64 frame chunks at 1–2 FPS.
    Asynchronously processes frames and streams real-time JSON diagnostics.
    """
    await websocket.accept()
    client_host = websocket.client.host if websocket.client else "unknown"
    logger.info(f"WebSocket client connected from {client_host} [Crop: {crop}]")

    active_target_hint = target_hint

    try:
        while True:
            # Receive message (supports either text/base64 JSON or raw binary bytes)
            message = await websocket.receive()

            frame_data = None
            if "bytes" in message and message["bytes"]:
                frame_data = message["bytes"]
            elif "text" in message and message["text"]:
                try:
                    payload = json.loads(message["text"])
                    frame_data = payload.get("frame")
                    if "target_hint" in payload:
                        active_target_hint = payload["target_hint"]
                except json.JSONDecodeError:
                    frame_data = message["text"]

            if not frame_data:
                await websocket.send_text(json.dumps({
                    "success": False,
                    "error": "Empty frame data received"
                }))
                continue

            # Run computer vision inference in worker thread to prevent event loop blocking
            diagnostic_result: DiagnosticResponse = await asyncio.to_thread(
                vision_engine.analyze_frame,
                frame_data,
                active_target_hint
            )

            # Stream serialized JSON response
            await websocket.send_text(diagnostic_result.model_dump_json())

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected: {client_host}")
    except Exception as e:
        logger.error(f"Unexpected WebSocket streaming error: {e}")
        try:
            await websocket.close()
        except Exception:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)

