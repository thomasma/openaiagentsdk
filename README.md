# MeChat - AI-Powered Personal Website Chat Agent

A simple chatbot application that uses OpenAI Agents SDK to answer questions about your background, experience, and skills based on your resume.

## Features

- Chat interface powered by Gradio
- **Input guardrails** for content moderation and validation
- Resume parsing and summarization
- RSS feed retrieval (blog and podcast)
- Push notifications via Pushover for user inquiries
- Clean, minimal dependencies

## Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/thomasma/openaiagentsdk
   cd openaiagentsdk
   ```

2. **Install uv (if not already installed)**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Install dependencies**
   ```bash
   uv sync
   ```

4. **Set up environment variables**

   Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and configure your settings:
   ```bash
   # Required: OpenAI API key
   OPENAI_API_KEY=your_openai_api_key_here

   # Required: Pushover credentials for push notifications
   PUSHOVER_TOKEN=your_pushover_token_here
   PUSHOVER_USER=your_pushover_user_key_here

   # Optional: Your RSS feed URLs
   BLOG_RSS_URL=https://yourblog.com/feed/
   PODCAST_RSS_URL=https://yourpodcast.com/rss
   ```

   **Important Notes:**
   - Get your OpenAI API key from [platform.openai.com](https://platform.openai.com)
   - The same OpenAI API key is used for both the chat agent and content moderation guardrails
   - Get Pushover credentials from [pushover.net](https://pushover.net) (required for user contact notifications)
   - `BLOG_RSS_URL` and `PODCAST_RSS_URL` are **optional** - if not set, example feeds will be used
   - The agent uses these RSS feeds to answer questions about your latest content

5. **Add your resume**

   Place your resume PDF in the project directory:
   ```bash
   cp /path/to/your/resume.pdf resume.pdf
   ```

   Or in a subdirectory (update `RESUME_PDF_PATH` accordingly):
   ```bash
   mkdir -p me
   cp /path/to/your/resume.pdf me/resume.pdf
   ```

6. **Personalize your settings**

   Edit `me_chat.py` to customize your agent (lines 13-17):
   ```python
   NAME = "Your Name"                    # Change to your name
   RESUME_PDF_PATH = "resume.pdf"       # Path to your resume PDF
   OPENAI_MODEL = "gpt-4o-mini"         # Or use gpt-4, gpt-4-turbo, etc.
   GRADIO_SERVER_PORT = 7860            # Change port if needed
   GRADIO_SHARE = False                 # Set True for public shareable link
   ```

   **Note:** The default configuration expects `resume.pdf` in the project root. If you placed it elsewhere, update `RESUME_PDF_PATH` to match your location (e.g., `"me/resume.pdf"`).

## Running the Application

### Using uv (recommended)
```bash
uv run python me_chat.py
```

### Using standard Python
```bash
python me_chat.py
```

The application will start and be available at:
```
http://localhost:7860
```

## Project Structure

```
.
├── me_chat.py                 # Main application
├── my_agents/                 # Custom agents
│   └── content_summarizer_agent.py
├── tools/                     # Agent tools
│   ├── rss_retriever_tool.py
│   └── push_notification_tool.py
├── utils/                     # Utilities
│   ├── input_guardrails.py    # Input validation guardrails
│   └── pushover.py
└── me/                        # Your personal content (gitignored)
    └── resume.pdf
```

## How It Works

1. **Resume Loading**: On startup, the app loads your resume PDF and summarizes it using an AI agent
2. **Chat Interface**: Users interact via a web-based chat interface
3. **Input Guardrails**: All user inputs are automatically validated through three guardrails:
   - **Content Moderation**: Uses OpenAI Moderation API to block inappropriate content (hate speech, harassment, violence, etc.)
   - **Length Validation**: Ensures messages don't exceed 10,000 characters
   - **Format Validation**: Checks for valid UTF-8 encoding and non-empty inputs
4. **Agent Response**: The agent responds based on your resume content
5. **Push Notifications**: When users ask unknown questions or request contact, you receive Pushover notifications
6. **RSS Tools**: The agent can fetch and discuss your latest blog posts or podcast episodes

## Configuration Options

### Environment Variables (.env file)
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `PUSHOVER_TOKEN`: Pushover app token (required for notifications)
- `PUSHOVER_USER`: Pushover user key (required for notifications)
- `BLOG_RSS_URL`: Your blog's RSS feed URL (optional)
- `PODCAST_RSS_URL`: Your podcast's RSS feed URL (optional)

### Application Settings (me_chat.py)
- `NAME`: Your name (default: "John Doe")
- `RESUME_PDF_PATH`: Path to your resume PDF (default: "resume.pdf")
- `OPENAI_MODEL`: Model to use (default: "gpt-4o-mini")
- `GRADIO_SERVER_PORT`: Port number (default: 7860)
- `GRADIO_SHARE`: Set to `True` to create a public shareable link (default: False)

**Important:** Make sure to update `NAME` and `RESUME_PDF_PATH` to match your actual name and resume location.

### Pushover Settings
- Required for push notifications when users engage
- Get your credentials at [pushover.net](https://pushover.net)

### RSS Feed Configuration
The agent can retrieve and discuss your blog posts and podcast episodes when users ask about them.

**To configure your feeds:**
1. Add `BLOG_RSS_URL` and/or `PODCAST_RSS_URL` to your `.env` file
2. The agent will automatically use these URLs when fetching content
3. If not configured, example feeds will be used (useful for testing)

**Supported RSS formats:**
- Standard RSS 2.0
- Atom feeds
- Podcast RSS feeds with iTunes extensions

**The agent can:**
- Fetch your latest 5 posts/episodes
- Summarize content for users
- Provide links to specific posts/episodes

## Troubleshooting

**Error: PUSHOVER_TOKEN or PUSHOVER_USER not set**
- Make sure your `.env` file exists and contains the required variables
- Verify the `.env` file is in the project root directory

**Error: Resume PDF not found**
- Ensure your resume PDF exists at the path specified in `RESUME_PDF_PATH`
- Default location is `resume.pdf` in the project root
- Check that the path in `me_chat.py` matches your actual file location

**Import errors**
- Run `uv sync` to ensure all dependencies are installed

## Input Guardrails

The application implements three layers of input validation using the OpenAI Agent SDK's `@input_guardrail` decorator:

### 1. Content Moderation
- **Purpose**: Blocks inappropriate or harmful content
- **Implementation**: Uses OpenAI Moderation API
- **Detects**: Hate speech, harassment, violence, self-harm, sexual content, and other policy violations
- **Behavior**: Triggers when content is flagged, returning a polite error message to the user

### 2. Length Validation
- **Purpose**: Prevents excessively long inputs
- **Limit**: 10,000 characters maximum
- **Behavior**: Blocks messages exceeding the limit with a helpful error message

### 3. Format Validation
- **Purpose**: Ensures input is properly formatted
- **Checks**: Valid UTF-8 encoding, non-empty/non-whitespace content
- **Behavior**: Rejects malformed or empty inputs

**Technical Details:**
- Guardrails run in parallel before the agent processes input
- Failed validation raises `InputGuardrailTripwireTriggered` exception
- User receives context-specific error messages based on which guardrail triggered
- Moderation API failures use a "fail-open" approach (allows content if API is unavailable)

**Location:** All guardrail functions are defined in [utils/input_guardrails.py](utils/input_guardrails.py)

## Dependencies

- `gradio` - Web interface
- `openai` - OpenAI API client (for Moderation API)
- `openai-agents` - OpenAI Agents SDK
- `pypdf` - PDF parsing
- `python-dotenv` - Environment variable loading
- `requests` - HTTP requests