"""
Socket.IO handler for real-time progress updates.

Event pattern: {user_id}/{skill_name}_progress
Payload: {tracking_id, stage, progress, message}
"""

import socketio

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
sio_app = socketio.ASGIApp(sio)


@sio.event
async def connect(sid, environ, auth=None):
    """Handle client connection."""
    # Optional JWT validation
    if auth and "token" in auth:
        # In production, validate JWT here
        pass
    print(f"Socket.IO client connected: {sid}")


@sio.event
async def disconnect(sid):
    print(f"Socket.IO client disconnected: {sid}")


@sio.event
async def join_room(sid, data):
    """Join a user-specific room for targeted progress updates."""
    user_id = data.get("user_id", "default")
    await sio.enter_room(sid, user_id)
    await sio.emit("joined", {"room": user_id}, to=sid)


async def emit_progress(
    user_id: str,
    skill_name: str,
    tracking_id: str,
    stage: str,
    progress: int,
    message: str = "",
):
    """Emit a progress event to a user's room."""
    event_name = f"{skill_name}_progress"
    payload = {
        "tracking_id": tracking_id,
        "stage": stage,
        "progress": progress,
        "message": message,
    }
    await sio.emit(event_name, payload, room=user_id)


def create_progress_callback(user_id: str, skill_name: str, tracking_id: str):
    """Create a progress callback for use in pipeline execution."""
    async def callback(stage: str, pct: int, msg: str = ""):
        await emit_progress(
            user_id=user_id,
            skill_name=skill_name,
            tracking_id=tracking_id,
            stage=stage,
            progress=pct,
            message=msg,
        )
    return callback
