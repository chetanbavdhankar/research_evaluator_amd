import math
from typing import Tuple
from research_repro.config import DiscrepancyThresholds

def classify_comparison(reported: float, reproduced: float, thresholds: DiscrepancyThresholds) -> str:
    """
    Returns match/close_match/moderate_discrepancy/significant_discrepancy 
    based on relative error abs(reported - reproduced) / max(abs(reported), 1e-9).
    """
    if math.isnan(reported) or math.isnan(reproduced):
        return "significant_discrepancy"
        
    rel_error = abs(reported - reproduced) / max(abs(reported), 1e-9)
    
    if rel_error <= thresholds.match:
        return "match"
    elif rel_error <= thresholds.close_match:
        return "close_match"
    elif rel_error <= thresholds.moderate:
        return "moderate_discrepancy"
    else:
        return "significant_discrepancy"

def statistical_comparison(reported_val: float, reproduced_ci: Tuple[float, float], is_p_value: bool = False) -> str:
    """
    Returns 'statistically_consistent' if reported_val is within reproduced_ci, else 'statistically_inconsistent'.
    If comparing two p-values, checks if both cross the same alpha=0.05 threshold.
    """
    if math.isnan(reported_val) or math.isnan(reproduced_ci[0]) or math.isnan(reproduced_ci[1]):
        return "statistically_inconsistent"

    if is_p_value:
        alpha = 0.05
        # For p-values, we often check if the conclusion (significant or not) matches.
        # Here we just use the simple mean of the CI for the reproduced p-value.
        reproduced_mean = (reproduced_ci[0] + reproduced_ci[1]) / 2.0
        reported_sig = reported_val < alpha
        reproduced_sig = reproduced_mean < alpha
        
        if reported_sig == reproduced_sig:
            return "statistically_consistent"
        else:
            return "statistically_inconsistent"

    if reproduced_ci[0] <= reported_val <= reproduced_ci[1]:
        return "statistically_consistent"
        
    return "statistically_inconsistent"
