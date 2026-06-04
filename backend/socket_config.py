import socketio

# List of allowed CORS origins matching FastAPI's CORS configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "http://0.0.0.0:3000",
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://localhost:3002",
    "http://127.0.0.1:3002",
]

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=CORS_ALLOWED_ORIGINS
)
