"""HealthConnect AI - No-Show Predictor Tool (Cross-track: GenAI <-> Data Science)"""
from typing import Any, Dict
from datetime import datetime
from config.logging_config import get_logger

logger = get_logger(__name__)

class NoShowPredictorTool:
    name = "predict_no_show"
    description = ("Predict no-show probability for a given appointment. "
                   "Use when the user asks about the likelihood of missing an appointment.")

    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            import joblib
            from pathlib import Path
            p = Path("models/no_show_model.pkl")
            if p.exists():
                self.model = joblib.load(p)
                logger.info(f"No-show model loaded from {p}")
            else:
                logger.warning("No-show model artifact not found. Using heuristic.")
        except Exception as e:
            logger.warning(f"No-show model load failed: {e}. Using heuristic.")

    async def run(self, **kwargs) -> Dict[str, Any]:
        lead_time = kwargs.get("lead_time_days", 7)
        hour = kwargs.get("appointment_hour", 10)
        age = kwargs.get("age", 40)
        prior = kwargs.get("prior_no_shows", 0)
        sms = kwargs.get("sms_received", True)
        if self.model is not None:
            try:
                import numpy as np
                feats = np.array([[lead_time, hour, age, prior, int(sms)]])
                prob = float(self.model.predict_proba(feats)[0][1])
                source = "model"
            except Exception as e:
                logger.error(f"Predict failed: {e}")
                prob = self._heuristic(lead_time, hour, prior, sms)
                source = "heuristic_fallback"
        else:
            prob = self._heuristic(lead_time, hour, prior, sms)
            source = "heuristic"
        band = "high" if prob >= 0.30 else "medium" if prob >= 0.15 else "low"
        return {"probability": round(prob, 3), "risk_band": band,
                "top_drivers": self._top_drivers(lead_time, hour, prior, sms),
                "source": source, "inputs": kwargs,
                "generated_at": datetime.utcnow().isoformat()}

    def _heuristic(self, lead, hour, prior, sms):
        p = 0.10
        if lead > 14: p += 0.15
        elif lead > 7: p += 0.08
        if hour < 9 or hour > 16: p += 0.05
        p += min(prior * 0.08, 0.30)
        if not sms: p += 0.06
        return min(p, 0.95)

    def _top_drivers(self, lead, hour, prior, sms):
        d = []
        if lead > 14: d.append("Long lead time (>14 days)")
        elif lead > 7: d.append("Moderate lead time (8-14 days)")
        if prior > 0: d.append(f"{prior} prior no-show(s)")
        if hour < 9 or hour > 16: d.append("Off-peak appointment hour")
        if not sms: d.append("No SMS reminder")
        return d or ["No major risk factors"]
