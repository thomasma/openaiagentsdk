from agents import function_tool
from utils.pushover import push

@function_tool
def record_unknown_question(question: str):
    """
    Records questions that cannot be answered and sends a push notification.

    Use this tool when:
    - A user asks a question you don't know the answer to
    - A user asks about topics outside of Mathew Thomas's background/experience
    - You need to flag questions for follow-up

    Args:
        question: The question that couldn't be answered
    """
    message = f"User asked a question that I couldn't answer. The question is - {question}"
    return _send_push_notification(message, "Question recorded and notification sent successfully")


@function_tool
def record_user_details(email: str, name: str="Name not provided", notes: str="not provided"):
    """
    Records user contact details and sends a push notification when a user wants to be contacted.

    Use this tool when:
    - A user provides their email address
    - A user asks to be contacted or wants to get in touch
    - A user wants to discuss opportunities, projects, or collaboration

    Args:
        email: User's email address (required)
        name: User's name (optional, defaults to "Name not provided")
        notes: Additional context or notes about the conversation (optional)
    """
    message = f"User contacted me for further comms. User with name '{name}', email '{email}' and notes: {notes}"
    return _send_push_notification(message, "Contact details recorded and notification sent successfully")


def _send_push_notification(message: str, success_message: str):
    """
    Helper function to send push notifications with consistent response format.

    Args:
        message: The notification message to send
        success_message: Message to return on success

    Returns:
        dict: Status and message indicating success or failure
    """
    success = push(message)

    if success:
        return {
            "status": "success",
            "message": success_message
        }
    else:
        return {
            "status": "error",
            "message": "Failed to send push notification. Information may not have been recorded."
        }
