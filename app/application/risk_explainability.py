from typing import Any, cast


class RiskExplainabilityService:

    def build_explanation(
        self,
        *,
        ahs: float,
        ces: float,
        cqs: float,
        dhm: float,
        ops: float,
        ves: float | None = None,
        weights: dict[str, float] | None = None,
        inputs: dict[str, Any],
        calculation_version: str,
        confidence: float,
    ) -> dict[str, Any]:

        scores = {
            "AHS": ahs,
            "CES": ces,
            "CQS": cqs,
            "DHM": dhm,
            "OPS": ops,
        }
        if ves is not None:
            scores["VES"] = ves

        factor_weights = weights or {}

        factors = []

        for factor, score in scores.items():
            weight = factor_weights.get(factor.lower(), 0.0)
            contribution = score * weight

            factors.append(
                {
                    "factor": factor,
                    "score": round(score, 2),
                    "weight": weight,
                    "contribution": round(contribution, 2),
                }
            )

        factors.sort(
            key=lambda item: float(cast(Any, item["contribution"])),
            reverse=True,
        )

        return {
            "factors": factors,
            "input_values": inputs,
            "calculation_version": calculation_version,
            "confidence": confidence,
        }