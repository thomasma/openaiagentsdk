from agents import Agent, function_tool, Runner
import asyncio
from datetime import datetime


# Define a tool
@function_tool
def getcurrentdatetime() -> dict:
    """Returns the current date and time in human readable format"""
    now = datetime.now()
    date_time = now.strftime("%A, %B %d, %Y at %I:%M:%S %p")
    print("inside tool")
    return {"date_time": date_time}


# Create an agent
agent = Agent(
    name="My Agent",
    instructions="You are a helpful assistant",
    tools=[getcurrentdatetime],
    model="gpt-4o-mini"
)


# Run the agent
async def main():
    result = await Runner.run(agent, "Who are you? And what is the current date and time?")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
