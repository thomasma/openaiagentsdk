"""Input guardrails for OpenAI Agent SDK."""

import os
from agents import input_guardrail, GuardrailFunctionOutput
from openai import AsyncOpenAI


# Initialize OpenAI client for moderation
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@input_guardrail(name="content_moderation")
async def check_content_moderation(context, agent, input_data):
    """
    Use OpenAI Moderation API to check for prohibited content.

    Flags content that violates OpenAI's usage policies including:
    - Hate speech
    - Harassment
    - Violence
    - Self-harm
    - Sexual content
    - Other prohibited categories
    """
    # Extract text from input
    input_text = input_data if isinstance(input_data, str) else ""

    # Skip moderation if input is empty
    if not input_text.strip():
        return GuardrailFunctionOutput(
            output_info={"reason": "empty_input"},
            tripwire_triggered=False
        )

    try:
        # Call OpenAI Moderation API
        moderation_response = await client.moderations.create(input=input_text)

        result = moderation_response.results[0]

        # Check if content is flagged
        if result.flagged:
            # Collect which categories were flagged
            flagged_categories = [
                category for category, flagged in result.categories.model_dump().items()
                if flagged
            ]

            return GuardrailFunctionOutput(
                output_info={
                    "flagged": True,
                    "categories": flagged_categories,
                    "reason": "Content violates usage policies"
                },
                tripwire_triggered=True
            )

        return GuardrailFunctionOutput(
            output_info={"flagged": False, "moderation_passed": True},
            tripwire_triggered=False
        )

    except Exception as e:
        # Log error but don't block on moderation API failures
        print(f"Moderation API error: {str(e)}")

        # Decide: fail open (allow) or fail closed (block)
        # Using fail-open approach - allow content if moderation fails
        return GuardrailFunctionOutput(
            output_info={"error": str(e), "moderation_check_failed": True},
            tripwire_triggered=False  # Change to True for fail-closed approach
        )


@input_guardrail(name="input_length_validation")
def check_input_length(context, agent, input_data):
    """
    Validate input length to prevent extremely long inputs.

    Limits input to 10,000 characters to prevent:
    - Excessive token usage
    - Performance issues
    - Potential abuse
    """
    input_text = input_data if isinstance(input_data, str) else str(input_data)

    max_length = 10000
    current_length = len(input_text)

    if current_length > max_length:
        return GuardrailFunctionOutput(
            output_info={
                "reason": "input_too_long",
                "current_length": current_length,
                "max_length": max_length
            },
            tripwire_triggered=True
        )

    return GuardrailFunctionOutput(
        output_info={"length_check_passed": True, "input_length": current_length},
        tripwire_triggered=False
    )


@input_guardrail(name="input_format_validation")
def check_input_format(context, agent, input_data):
    """
    Validate input format and encoding.

    Ensures input is:
    - Valid UTF-8
    - Not completely whitespace
    - Properly formatted
    """
    try:
        input_text = input_data if isinstance(input_data, str) else str(input_data)

        # Check for valid UTF-8 encoding
        input_text.encode('utf-8')

        # Check if input is not just whitespace
        if not input_text.strip():
            return GuardrailFunctionOutput(
                output_info={"reason": "empty_or_whitespace_only"},
                tripwire_triggered=True
            )

        return GuardrailFunctionOutput(
            output_info={"format_check_passed": True, "valid_encoding": True},
            tripwire_triggered=False
        )

    except Exception as e:
        return GuardrailFunctionOutput(
            output_info={"error": "invalid_encoding", "details": str(e)},
            tripwire_triggered=True
        )
