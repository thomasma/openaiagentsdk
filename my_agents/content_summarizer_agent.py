from agents import Agent, function_tool
import re

@function_tool
def summarize_content(content: str, content_type: str = "linkedin"):
    """
    Summarize content by normalizing whitespace and reducing verbosity

    Args:
        content: The content to summarize
        content_type: Type of content ("linkedin" or "summary")
    """
    try:
        original_length = len(content)

        # Remove excessive whitespace and normalize
        content = re.sub(r'\s+', ' ', content)
        content = content.strip()

        # Remove duplicate consecutive sentences
        sentences = content.split('. ')
        seen = set()
        unique_sentences = []
        for sentence in sentences:
            normalized = sentence.strip().lower()
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique_sentences.append(sentence.strip())
        content = '. '.join(unique_sentences)
        if content and not content.endswith('.'):
            content += '.'

        return {
            "status": "success",
            "original_length": original_length,
            "summarized_content": content,
            "content_type": content_type,
            "reduction_percentage": round((1 - len(content) / original_length) * 100, 1) if original_length > 0 else 0
        }

    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to summarize content: {str(e)}",
            "content_type": content_type
        }

INSTRUCTIONS = """You are a specialized content summarizer agent. Your job is to intelligently condense LinkedIn profiles and summary content while preserving all essential information and details.

Your summarization process should:
1. Keep all company names, dates, locations, and specific details intact
2. Remove duplicate or redundant information
3. Normalize whitespace and formatting
4. Preserve the core professional information, skills, experience, and achievements
5. Maintain readability and flow
6. Keep all relevant context and specifics

Focus on conciseness without losing important details or context."""

content_summarizer_agent = Agent(
    name="Content Summarizer Agent",
    instructions=INSTRUCTIONS,
    tools=[summarize_content],
    model="gpt-4o-mini",
)
