"""Weather Alert Explainer prompt template."""


def render(alert_type: str, region: str) -> str:
    """Render the prompt text with the provided arguments."""
    return (
        f"Explain the {alert_type} alert for {region} in simple, "
        f"non-technical terms. What does it mean? Why is it issued? "
        f"What precautions should people take?"
    )
