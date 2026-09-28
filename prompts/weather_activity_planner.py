"""Weather Activity Planner prompt template."""

from mcp.types import GetPromptResult, Prompt, PromptArgument, PromptMessage, TextContent

WEATHER_ACTIVITY_PLANNER = Prompt(
    name="weather_activity_planner",
    description="Plan outdoor activities based on weather conditions and get preparation tips",
    arguments=[
        PromptArgument(
            name="location",
            description="The location/city for activity planning",
            required=True,
        ),
        PromptArgument(
            name="activity_type",
            description="Type of activity (e.g., hiking, picnic, outdoor run)",
            required=True,
        ),
        PromptArgument(
            name="time_horizon",
            description="When you plan to do the activity (e.g., today, this weekend, next week)",
            required=False,
        ),
    ],
)


def render(location: str, activity_type: str, time_horizon: str = "soon") -> GetPromptResult:
    """Render the prompt with provided arguments."""
    return GetPromptResult(
        description=f"Activity planning prompt for {activity_type} in {location}",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=(
                        f"Help me plan a {activity_type} in {location} {time_horizon}. "
                        f"What should I prepare? Check the current weather and suggest "
                        f"the best time and what gear/precautions I need."
                    ),
                ),
            )
        ],
    )
