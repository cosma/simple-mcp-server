"""Weather Alert Explainer prompt template."""

from mcp.types import GetPromptResult, Prompt, PromptArgument, PromptMessage, TextContent

WEATHER_ALERT_EXPLAINER = Prompt(
    name="weather_alert_explainer",
    description="Get simple explanations of weather alerts with safety tips and precautions",
    arguments=[
        PromptArgument(
            name="alert_type",
            description="Type of weather alert (e.g., severe thunderstorm, heat advisory, winter storm)",
            required=True,
        ),
        PromptArgument(
            name="region",
            description="Geographic region affected by the alert",
            required=True,
        ),
    ],
)


def render(alert_type: str, region: str) -> GetPromptResult:
    """Render the prompt with provided arguments."""
    return GetPromptResult(
        description=f"Weather alert explanation for {alert_type} in {region}",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=(
                        f"Explain the {alert_type} alert for {region} in simple, "
                        f"non-technical terms. What does it mean? Why is it issued? "
                        f"What precautions should people take?"
                    ),
                ),
            )
        ],
    )
