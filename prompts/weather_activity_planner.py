"""Weather Activity Planner prompt template."""


def render(location: str, activity_type: str, time_horizon: str = "soon") -> str:
    """Render the prompt text with the provided arguments."""
    return (
        f"Help me plan a {activity_type} in {location} {time_horizon}. "
        f"What should I prepare? Check the current weather and suggest "
        f"the best time and what gear/precautions I need."
    )
