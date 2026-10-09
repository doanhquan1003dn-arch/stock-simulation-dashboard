
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
import pandas as pd
import numpy as np

app = FastAPI()

# Doc du lieu va xu ly giong main.py
P = pd.read_csv("data/abc-2.csv", header=None).to_numpy(float)
TC = np.r_[P[0, 6], P[:-1, 6]]
P = np.clip(P, TC[:, None] * 0.9, TC[:, None] * 1.1)

# Tinh 4 thong tin thong ke
stats = {
    "mean": round(P.mean()),
    "high": round(P.max()),
    "low": round(P.min()),
    "range": round(P.max() - P.min())
}

@app.get("/", response_class=HTMLResponse)
def home():
    with open("templates/index.html", encoding="utf-8") as f:
        html = f.read()

    for key, value in stats.items():
        html = html.replace("{{" + key + "}}", f"{value:,.0f}")

    return HTMLResponse(html)

@app.get("/video")
def video():
    return FileResponse(
        "static/video/price_simulation.mp4",
        media_type="video/mp4",
        headers={"Cache-Control": "no-store"}
    )
