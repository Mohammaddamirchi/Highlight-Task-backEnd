def extra_insights(transcript: str) -> dict:
    hesitation_words = ["maybe", "not sure", "i think", "uh", "um"]

    risks = [w for w in hesitation_words if w in transcript.lower()]

    sentiment = (
        "positive" if len(risks) == 0 else
        "neutral" if len(risks) <= 2 else
        "negative"
    )

    confidence = round(1 - (len(risks) * 0.15), 2)
    confidence = max(confidence, 0.3)

    return {
        "sentiment": sentiment,
        "confidence": confidence,
        "risk_flags": risks,
        "hr_suggestion": "Clarify expectations earlier in the call"
        if risks else "Current call script is effective"
    }
