from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq
from langchain.agents import create_agent

from dotenv import load_dotenv
import asyncio
import os
load_dotenv()

FILE_DIR = os.path.join(os.path.dirname(__file__), '..', 'server', 'mathserver.py')
FILE_DIR = os.path.abspath(FILE_DIR)

async def main():
  client = MultiServerMCPClient(
    {
      "math": {
        "command": "python",
        "args": [FILE_DIR],
        "transport": 'stdio',
      },
      "weather": {
        "url": "http://localhost:8000/mcp",
        "transport": 'streamable-http',
      }
    }
  )

  os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')

  tools = await client.get_tools()
  model = ChatGroq(model_name="qwen/qwen3-32b", temperature=0)

  agent = create_agent(
    model, tools
  )

  math_response = await agent.ainvoke(
    {"messages": [{"role": "user", "content": "What's (14 X 3) + 13"}]}
  )

  response = math_response['messages'][-1].content
  print("Math's response is:", response)

  weather_response = await agent.ainvoke(
    {"messages": [{"role": "user", "content": "What's the weather in Lahore, Pakistan?"}]}
  )

  response = weather_response['messages'][-1].content

  print("Weather's response is:", response)

asyncio.run(main())

