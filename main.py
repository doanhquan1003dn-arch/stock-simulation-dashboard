
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter
from pathlib import Path

# 1. Doc du lieu
P = pd.read_csv("data/abc-2.csv", header=None).to_numpy(float)
N = len(P)
X = np.arange(N)

TC = np.r_[P[0, 6], P[:-1, 6]]
SAN, TRAN = TC * 0.9, TC * 1.1
P = np.clip(P, SAN[:, None], TRAN[:, None])

CLOSE = P[:, 6]
LOW, HIGH, MEAN = P.min(1), P.max(1), P.mean(1)

BLUE, PURPLE, YELLOW = "#00cfff", "#ae78ef", "#ffe329"
RED, GREEN = "#f12b36", "#20c938"

def mau(c, tc, san, tran):
    if np.isclose(c, san, atol=0.5, rtol=0): return BLUE
    if np.isclose(c, tran, atol=0.5, rtol=0): return PURPLE
    if np.isclose(c, tc, atol=0.5, rtol=0): return YELLOW
    return RED if c < tc else GREEN

# 2. Gom 2 ngay thanh 1 nen
fig, (ax1, ax2) = plt.subplots(
    2, 1, figsize=(16, 9.2), sharex=True,
    gridspec_kw={"hspace": 0.08}
)
fig.patch.set_facecolor("black")
fig.subplots_adjust(left=.08, right=.95, top=.97, bottom=.08)

for ax in (ax1, ax2):
    ax.set_facecolor("black")
    ax.tick_params(colors="white")
    ax.set_xlim(-5, max(375, N + 10))
    ax.set_ylim(-500, max(21000, HIGH.max() * 1.1))
    ax.set_ylabel("VND", color="white")
    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda v, _: f"{v:,.0f}")
    )
    for spine in ax.spines.values():
        spine.set_color("white")

ax2.set_xlabel("Date", color="white")
ax2.set_xticks(np.arange(0, 361, 30))

# Nen theo trung binh 2 ngay
candles = []
for s in range(0, N, 2):
    e = min(s + 2, N)
    p = P[s:e].mean(axis=0)
    q1, med, q3 = np.percentile(p, [25, 50, 75])
    x = (s + e - 1) / 2

    c = mau(CLOSE[s:e].mean(), TC[s:e].mean(),
            SAN[s:e].mean(), TRAN[s:e].mean())

    body = Rectangle((x-.76, q1), 1.52, max(q3-q1, .01),
                     color=c, visible=False)
    ax1.add_patch(body)
    wick, = ax1.plot([x, x], [p.min(), p.max()],
                     color=c, lw=1.2, visible=False)
    median, = ax1.plot([x-.55, x+.55], [med, med],
                       color="white", lw=.7, visible=False)
    candles.append((e-1, body, wick, median))

# 3. Bieu do duoi: dai dao dong xanh olive va nau
upper = ax2.fill_between(X, MEAN, HIGH, color="#617321", alpha=.55)
lower = ax2.fill_between(X, LOW, MEAN, color="#997020", alpha=.45)

from matplotlib.patches import Rectangle as ClipRect
clip = ClipRect((-5, -1e6), 0, 2e6, transform=ax2.transData)
upper.set_clip_path(clip)
lower.set_clip_path(clip)

hi_line, = ax2.plot([], [], color="#667e20", lw=1)
lo_line, = ax2.plot([], [], color="#775222", lw=1)
mean_line, = ax2.plot([], [], lw=1.5)

hmax = ax2.axhline(MEAN[0], color=GREEN, ls=":", lw=.8)
hmin = ax2.axhline(MEAN[0], color=RED, ls=":", lw=.8)

txt = ax2.text(0, MEAN[0], "", fontsize=9, color=GREEN)

# 4. Tao video 60 giay
FPS, SECONDS = 8, 60
frames = np.rint(np.linspace(0, N-1, FPS*SECONDS)).astype(int)

def update(i):
    for end, body, wick, median in candles:
        if end <= i:
            body.set_visible(True)
            wick.set_visible(True)
            median.set_visible(True)

    xi = X[:i+1]
    hi_line.set_data(xi, HIGH[:i+1])
    lo_line.set_data(xi, LOW[:i+1])
    mean_line.set_data(xi, MEAN[:i+1])

    # Doi mau TOAN BO duong khi xu huong thay doi
    c = GREEN if i == 0 or MEAN[i] >= MEAN[i-1] else RED
    mean_line.set_color(c)

    clip.set_width(i + 5)
    hmax.set_ydata([MEAN[:i+1].max()] * 2)
    hmin.set_ydata([MEAN[:i+1].min()] * 2)

    txt.set_position((i+2, MEAN[i]))
    txt.set_text(f"{MEAN[i]:,.0f}")
    txt.set_color(c)

ani = animation.FuncAnimation(
    fig, update, frames=frames,
    interval=1000/FPS, repeat=False,
    cache_frame_data=False
)

Path("static/video").mkdir(parents=True, exist_ok=True)

writer = animation.FFMpegWriter(
    fps=FPS, bitrate=1400,
    extra_args=["-preset", "ultrafast", "-pix_fmt", "yuv420p"]
)

ani.save("static/video/price_simulation.mp4",
         writer=writer, dpi=80)
plt.close(fig)

print("Da xuat video 60 giay thanh cong!")
