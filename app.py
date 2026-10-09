
from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()

@app.get("/")
def home():
    return FileResponse("templates/index.html")

@app.get("/video")
def video():
    return FileResponse(
        "static/video/price_simulation.mp4",
        media_type="video/mp4",
        headers={"Cache-Control": "no-store"}
    )
