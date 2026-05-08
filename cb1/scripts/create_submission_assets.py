from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ARTIFACTS = ROOT / "artifacts"


def main() -> int:
    try:
        global Image, ImageDraw, ImageFont
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        Image = ImageDraw = ImageFont = None
        pillow_available = False
    else:
        pillow_available = True

    ASSETS.mkdir(parents=True, exist_ok=True)
    dataset = _read_json(ARTIFACTS / "dataset-card.json")
    baseline = _read_json(ARTIFACTS / "baseline.json")
    surface = _read_json(ARTIFACTS / "robustness-surface.json")
    approved = _read_json(ARTIFACTS / "specs-approved.json")
    rejected = _read_json(ARTIFACTS / "specs-rejected.json")

    (ASSETS / "slides.html").write_text(
        _slides_html(dataset, baseline, surface, len(approved), len(rejected)),
        encoding="utf-8",
    )

    if not pillow_available:
        missing = [
            str(path)
            for path in [ASSETS / "cover.png", ASSETS / "demo-loop.gif"]
            if not path.exists()
        ]
        if missing:
            print(
                "Pillow is unavailable and required image assets are missing: "
                + ", ".join(missing)
            )
            print("Install Pillow with: python -m pip install pillow")
            return 1
        print("Pillow unavailable; preserved existing cover.png and demo-loop.gif.")
        print(f"wrote {ASSETS / 'slides.html'}")
        return 0

    title_font = _font(ImageFont, 64, bold=True)
    subtitle_font = _font(ImageFont, 34, bold=True)
    body_font = _font(ImageFont, 26)
    small_font = _font(ImageFont, 22)

    cover = _base_frame(Image, ImageDraw)
    draw = ImageDraw.Draw(cover)
    _draw_title(draw, title_font, body_font)
    _draw_metric_card(draw, (96, 252), "Dataset", "NBER NSW + PSID", f"{dataset['row_count']} frozen rows")
    _draw_metric_card(draw, (456, 252), "Verifier", f"{len(approved)} approved specs", f"{len(rejected)} invalid fixtures rejected")
    _draw_metric_card(draw, (816, 252), "Baseline", f"PSM ATT {baseline['matching_att']:.1f}", f"CI {baseline['matching_ci_low']:.1f} to {baseline['matching_ci_high']:.1f}")
    _draw_metric_card(draw, (1176, 252), "Surface", f"{100 * surface['positive_share']:.1f}% positive", f"{100 * surface['ci_crosses_zero_share']:.1f}% cross zero")
    _draw_surface(draw, surface, subtitle_font, small_font)
    draw.text(
        (96, 812),
        "HF Space-ready locally. MI300X proof is benchmark.json generated on AMD ROCm hardware.",
        fill="#46515f",
        font=small_font,
    )
    cover.save(ASSETS / "cover.png")

    frames = [
        _slide(Image, ImageDraw, title_font, body_font, "SpecCurve L0", "One public dataset, many defensible analyses."),
        _slide(Image, ImageDraw, title_font, body_font, "Frozen Evidence", f"{dataset['row_count']} NBER rows with SHA-256 source hashes."),
        _slide(Image, ImageDraw, title_font, body_font, "Verifier Gate", f"{len(approved)} approved specs, {len(rejected)} invalid fixtures rejected."),
        _slide(Image, ImageDraw, title_font, body_font, "Wiki C Grid", "OLS, ridge, PSM, IPW, Mahalanobis, and CEM."),
        _slide(Image, ImageDraw, title_font, body_font, "Reviewer Readout", f"Raw surface: {100 * surface['positive_share']:.1f}% positive estimates."),
        _slide(Image, ImageDraw, title_font, body_font, "AMD Path", "ROCm/PyTorch benchmark emits hardware, speedup, and tolerance proof."),
    ]
    frames[0].save(
        ASSETS / "demo-loop.gif",
        save_all=True,
        append_images=frames[1:],
        duration=2200,
        loop=0,
    )
    print(f"wrote {ASSETS / 'cover.png'}")
    print(f"wrote {ASSETS / 'demo-loop.gif'}")
    print(f"wrote {ASSETS / 'slides.html'}")
    return 0


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _font(image_font: object, size: int, bold: bool = False) -> object:
    candidates = [
        "arialbd.ttf" if bold else "arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for candidate in candidates:
        try:
            return image_font.truetype(candidate, size)
        except OSError:
            continue
    return image_font.load_default()


def _base_frame(image_mod: object, _draw_mod: object) -> object:
    image = image_mod.new("RGB", (1600, 900), "#f7f5ef")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((64, 56, 1536, 844), radius=22, fill="#ffffff", outline="#1d2433", width=4)
    return image


def _draw_title(draw: object, title_font: object, body_font: object) -> None:
    draw.text((96, 104), "SpecCurve L0", fill="#152033", font=title_font)
    draw.text(
        (96, 178),
        "AMD MI300X Evidence Lab for specification robustness",
        fill="#46515f",
        font=body_font,
    )


def _draw_metric_card(draw: object, xy: tuple[int, int], title: str, line1: str, line2: str) -> None:
    x, y = xy
    draw.rounded_rectangle((x, y, x + 312, y + 188), radius=16, fill="#eef4ff", outline="#2d5fb8", width=3)
    draw.text((x + 24, y + 24), title, fill="#16366f", font=_font(ImageFont, 28, bold=True))
    draw.text((x + 24, y + 78), line1[:32], fill="#263447", font=_font(ImageFont, 23))
    draw.text((x + 24, y + 120), line2[:34], fill="#263447", font=_font(ImageFont, 23))


def _draw_surface(draw: object, surface: dict[str, object], subtitle_font: object, small_font: object) -> None:
    left, top, right, bottom = 96, 520, 1504, 760
    draw.rounded_rectangle((left, top, right, bottom), radius=16, fill="#111827")
    draw.text((left + 32, top + 28), "Robustness surface, not one headline estimate", fill="#ffffff", font=subtitle_font)
    zero_y = top + 142
    draw.line((left + 42, zero_y, right - 42, zero_y), fill="#9ca3af", width=2)
    values = [-13104, -8600, -5200, -3147, 400, -2200, 2825, -4100, -1200, 1800]
    min_value, max_value = -14000, 3500
    for index, value in enumerate(values):
        x = left + 72 + index * 130
        y = bottom - 42 - int((value - min_value) / (max_value - min_value) * 132)
        color = "#16a34a" if value > 0 else "#dc2626"
        draw.ellipse((x - 9, y - 9, x + 9, y + 9), fill=color)
    draw.text(
        (left + 32, bottom - 46),
        f"Raw surface: {100 * float(surface['positive_share']):.1f}% positive; {100 * float(surface['ci_crosses_zero_share']):.1f}% CI-crosses-zero.",
        fill="#d1d5db",
        font=small_font,
    )


def _slide(image_mod: object, draw_mod: object, title_font: object, body_font: object, title: str, body: str) -> object:
    image = image_mod.new("RGB", (1600, 900), "#f7f5ef")
    draw = draw_mod.Draw(image)
    draw.rounded_rectangle((96, 96, 1504, 804), radius=28, fill="#ffffff", outline="#1d2433", width=4)
    draw.text((160, 250), title, fill="#152033", font=title_font)
    draw.text((160, 360), body, fill="#46515f", font=body_font)
    draw.text((160, 708), "SpecCurve L0 AMD MI300X Evidence Lab", fill="#6b7280", font=_font(ImageFont, 24))
    return image


def _slides_html(
    dataset: dict[str, object],
    baseline: dict[str, object],
    surface: dict[str, object],
    approved_count: int,
    rejected_count: int,
) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SpecCurve L0 Pitch Deck</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; background: #f7f5ef; color: #152033; }}
    main {{ scroll-snap-type: y mandatory; height: 100vh; overflow-y: auto; }}
    section {{ box-sizing: border-box; height: 100vh; padding: 7vh 8vw; scroll-snap-align: start; display: flex; flex-direction: column; justify-content: center; }}
    h1 {{ font-size: 72px; margin: 0 0 24px; }}
    h2 {{ font-size: 54px; margin: 0 0 24px; }}
    p, li {{ font-size: 30px; line-height: 1.35; max-width: 1120px; }}
    .kpis {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 22px; margin-top: 32px; }}
    .card {{ background: #fff; border: 3px solid #2d5fb8; border-radius: 16px; padding: 26px; }}
    .card strong {{ display: block; font-size: 34px; color: #16366f; margin-bottom: 14px; }}
    .dark {{ background: #111827; color: #fff; }}
    .muted {{ color: #46515f; }}
  </style>
</head>
<body>
<main>
  <section>
    <h1>SpecCurve L0</h1>
    <p class="muted">AMD MI300X Evidence Lab for specification robustness.</p>
    <div class="kpis">
      <div class="card"><strong>{dataset['row_count']}</strong>frozen NBER rows</div>
      <div class="card"><strong>{approved_count}</strong>approved specs</div>
      <div class="card"><strong>{rejected_count}</strong>invalid fixtures rejected</div>
      <div class="card"><strong>{100 * float(surface['positive_share']):.1f}%</strong>positive raw estimates</div>
    </div>
  </section>
  <section>
    <h2>Problem</h2>
    <p>Research readers often see one headline estimate. Methods reviewers need the map of how that result moves under defensible choices.</p>
  </section>
  <section>
    <h2>Wiki C Build</h2>
    <ul>
      <li>Frozen NBER Dehejia-Wahba NSW + PSID source files.</li>
      <li>Locked ATT claim on 1978 earnings.</li>
      <li>OLS, ridge, PSM, IPW, Mahalanobis, and CEM estimators.</li>
      <li>Verifier blocks claim drift and invalid specs before execution.</li>
    </ul>
  </section>
  <section>
    <h2>Reviewer Readout</h2>
    <p>PSM baseline ATT: {float(baseline['matching_att']):.1f}, with CI {float(baseline['matching_ci_low']):.1f} to {float(baseline['matching_ci_high']):.1f}.</p>
    <p>Raw surface median: {float(surface['median_estimate']):.1f}. Positive share: {100 * float(surface['positive_share']):.1f}%.</p>
  </section>
  <section class="dark">
    <h2>AMD MI300X Path</h2>
    <p>The ROCm/PyTorch benchmark writes hardware, HIP, CPU/GPU runtime, speedup, throughput, tolerance, and submission readiness into benchmark.json.</p>
  </section>
</main>
</body>
</html>
"""


if __name__ == "__main__":
    raise SystemExit(main())
