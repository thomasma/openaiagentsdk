from agents import Runner, Agent, InputGuardrailTripwireTriggered
from tools import get_blog_rss_feed, get_podcast_rss_feed, record_unknown_question, record_user_details
from my_agents import content_summarizer_agent
from utils.input_guardrails import check_content_moderation, check_input_length, check_input_format
from pypdf import PdfReader
from dotenv import load_dotenv
import asyncio
import gradio as gr

# Load environment variables
load_dotenv()

# Configuration
NAME = "John Doe"
RESUME_PDF_PATH = "resume.pdf"
OPENAI_MODEL = "gpt-4o-mini"
GRADIO_SERVER_PORT = 7860
GRADIO_SHARE = False


class MeChat:
    def __init__(self):
        self.name = NAME

        # Load and summarize content
        self.resume = self._load_resume()

        # Build system prompt
        self.system_prompt = self._build_system_prompt()

        # Set up the Agent with the tools and input guardrails
        all_tools = [get_blog_rss_feed, get_podcast_rss_feed, record_unknown_question, record_user_details]
        self.chat_agent = Agent(
            name="Chat agent",
            instructions=self.system_prompt,
            tools=all_tools,
            model=OPENAI_MODEL,
            input_guardrails=[check_input_format, check_input_length, check_content_moderation]
        )

    def _load_pdf_content(self, file_path: str) -> str:
        """Load and extract text from PDF file."""
        reader = PdfReader(file_path)
        content = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                content += text
        return content

    def _load_and_summarize(self, file_path: str, content_type: str, loader_fn) -> str:
        """Generic content loader with error handling and summarization."""
        print(f"Loading and summarizing {content_type} content...")
        try:
            raw_content = loader_fn(file_path)
            result = asyncio.run(
                Runner.run(content_summarizer_agent, f"Summarize this {content_type} content: {raw_content}")
            )
            return result.final_output if hasattr(result, 'final_output') else str(result)
        except FileNotFoundError:
            print(f"ERROR: {content_type.capitalize()} not found at {file_path}")
            return f"{content_type.capitalize()} information not available."
        except Exception as e:
            print(f"ERROR: Failed to load {content_type} content: {e}")
            return f"{content_type.capitalize()} information temporarily unavailable."

    def _load_resume(self) -> str:
        """Load resume PDF and summarize it."""
        return self._load_and_summarize(RESUME_PDF_PATH, "resume", self._load_pdf_content)


    def _build_system_prompt(self) -> str:
        """Build the system prompt for the agent."""
        prompt = f"""You are acting as {self.name}. You are answering questions on {self.name}'s website, \
particularly questions related to {self.name}'s career, background, skills and experience. \
Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. \
You are given {self.name}'s resume which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. \
If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool.

## Resume:
{self.resume}

With this context, please chat with the user, always staying in character as {self.name}."""

        return prompt

    def chat(self, message, history):
        """
        Handle chat messages with input guardrail protection.

        Args:
            message: The user's message (str or dict)
            history: List of previous messages (required by Gradio but not used)

        Returns:
            str: The agent's response
        """
        user_message = message.get("text", "") if isinstance(message, dict) else message

        try:
            result = asyncio.run(Runner.run(self.chat_agent, user_message))
            response = result.final_output if hasattr(result, 'final_output') else str(result)
            print(f"Agent response: {response[:100]}...")
            return response
        except InputGuardrailTripwireTriggered as e:
            # Handle guardrail violations gracefully
            guardrail_name = e.guardrail_result.guardrail.get_name()
            output_info = e.guardrail_result.output.output_info

            print(f"Input guardrail triggered: {guardrail_name}, info: {output_info}")

            # Return user-friendly error messages based on the guardrail
            if guardrail_name == "content_moderation":
                return "I'm sorry, but I cannot process that message as it appears to contain content that violates our usage policies. Please rephrase your question in a respectful manner."
            elif guardrail_name == "input_length_validation":
                max_length = output_info.get('max_length', 10000)
                return f"I'm sorry, but your message is too long. Please keep your message under {max_length} characters."
            elif guardrail_name == "input_format_validation":
                reason = output_info.get('reason', 'invalid format')
                return f"I'm sorry, but your message has a formatting issue: {reason}. Please try again."
            else:
                return "I'm sorry, but I couldn't process your message. Please try rephrasing your question."
        except Exception as e:
            print(f"Error in chat: {str(e)}")
            return f"I apologize, but an error occurred while processing your message. Please try again."


if __name__ == "__main__":
    print(f"Starting MeChat for {NAME}...")
    me = MeChat()
    print("✓ MeChat initialized successfully")
    print(f"Launching Gradio interface on port {GRADIO_SERVER_PORT}...")
    gr.ChatInterface(
        me.chat,
        type="messages",
        title=f"Chat with {NAME}",
        description=f"Ask me anything about my background, experience, and interests!"
    ).launch(
        server_port=GRADIO_SERVER_PORT,
        share=GRADIO_SHARE
    )
