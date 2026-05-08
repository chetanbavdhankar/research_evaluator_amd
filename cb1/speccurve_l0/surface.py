from __future__ import annotations

from html import escape
from typing import Any

from .linear import median


def summarize_surface(results: list[dict[str, Any]]) -> dict[str, Any]:
    primary_results = [result for result in results if result.get("outcome_transform") == "raw"]
    if not primary_results:
        primary_results = results
    estimates = [float(result["estimate_att"]) for result in primary_results]
    if not estimates:
        return {"approved_result_count": 0, "surface_result_count": 0}
    ci_crosses_zero = [
        result for result in primary_results if float(result["ci_low"]) <= 0 <= float(result["ci_high"])
    ]
    return {
        "approved_result_count": len(results),
        "surface_result_count": len(primary_results),
        "primary_transform": primary_results[0].get("outcome_transform") if primary_results else None,
        "min_estimate": min(estimates),
        "median_estimate": median(estimates),
        "max_estimate": max(estimates),
        "positive_share": sum(1 for value in estimates if value > 0) / len(estimates),
        "ci_crosses_zero_share": len(ci_crosses_zero) / len(primary_results),
        "filter_levels": sorted({str(result["sample_filter"]) for result in results}),
        "estimator_levels": sorted({str(result["estimator"]) for result in results}),
        "propensity_model_levels": sorted({str(result.get("propensity_model", "none")) for result in results}),
        "support_rule_levels": sorted({str(result.get("support_rule", "none")) for result in results}),
        "transform_levels": sorted({str(result["outcome_transform"]) for result in results}),
        "scale_note": "Headline surface statistics use raw re78 specifications only.",
    }


def render_surface_svg(results: list[dict[str, Any]], width: int = 900, height: int = 360) -> str:
    primary_results = [result for result in results if result.get("outcome_transform") == "raw"]
    if not primary_results:
        primary_results = results
    if not primary_results:
        return "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"900\" height=\"360\"></svg>"

    padding = 46
    estimates = [float(result["estimate_att"]) for result in primary_results]
    lower = min(min(estimates), 0.0)
    upper = max(max(estimates), 0.0)
    span = upper - lower or 1.0

    def x_position(index: int) -> float:
        if len(primary_results) == 1:
            return width / 2
        return padding + index * (width - 2 * padding) / (len(primary_results) - 1)

    def y_position(value: float) -> float:
        return height - padding - ((value - lower) / span) * (height - 2 * padding)

    zero_y = y_position(0.0)
    points = []
    for index, result in enumerate(primary_results):
        estimate = float(result["estimate_att"])
        color = "#1f7a4d" if estimate >= 0 else "#b42318"
        tooltip = escape(f"{result['spec_id']}: {estimate:.2f}")
        points.append(
            f"<circle cx=\"{x_position(index):.2f}\" cy=\"{y_position(estimate):.2f}\" "
            f"r=\"4\" fill=\"{color}\"><title>{tooltip}</title></circle>"
        )

    label_low = escape(f"{lower:.1f}")
    label_high = escape(f"{upper:.1f}")
    return (
        f"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{width}\" height=\"{height}\" "
        f"viewBox=\"0 0 {width} {height}\" role=\"img\" aria-label=\"Robustness surface\">"
        "<rect width=\"100%\" height=\"100%\" fill=\"#ffffff\"/>"
        f"<line x1=\"{padding}\" x2=\"{width - padding}\" y1=\"{zero_y:.2f}\" y2=\"{zero_y:.2f}\" "
        "stroke=\"#555\" stroke-dasharray=\"4 4\"/>"
        f"<text x=\"{padding}\" y=\"24\" font-family=\"Arial\" font-size=\"14\" fill=\"#111\">"
        "SpecCurve robustness surface (raw re78 scale)</text>"
        f"<text x=\"{padding}\" y=\"{height - 14}\" font-family=\"Arial\" font-size=\"11\" "
        f"fill=\"#555\">{label_low}</text>"
        f"<text x=\"{width - padding - 52}\" y=\"{padding}\" font-family=\"Arial\" font-size=\"11\" "
        f"fill=\"#555\">{label_high}</text>"
        + "".join(points)
        + "</svg>"
    )
