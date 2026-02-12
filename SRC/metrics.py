import numpy as np

def summarise(final_values: np.ndarray) -> dict:
    return {
        "median": float(np.median(final_values)),
        "mean": float(np.mean(final_values)),
        "p10": float(np.percentile(final_values, 10)),
        "p90": float(np.percentile(final_values, 90)),
        "min": float(np.min(final_values)),
        "max": float(np.max(final_values)),
    }

def prob_reach_goal(final_values: np.ndarray, goal: float) -> float:
    if goal <= 0:
        return 0.0
    return float((final_values >= goal).mean())
