# All required libraries import
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph import START
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
import os
from dotenv import load_dotenv

# Getting env variables
load_dotenv()
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')
os.environ['TAVILY_API_KEY'] = os.getenv('TAVILY_API_KEY')
os.environ['LANGSMITH_API_KEY'] = os.getenv('LANGSMITH_API_KEY')
os.environ['LANGSMITH_TRACING'] = os.getenv('LANGSMITH_TRACING')
os.environ['LANGSMITH_PROJECT'] = os.getenv('LANGSMITH_PROJECT')

# State
class State(TypedDict):
  messages: Annotated[list[BaseMessage], add_messages]

# Tool Graph Function
def make_tool_graph():
  tavily = TavilySearchResults(max_search_results = 3)

  @tool
  def add(a: float, b: float) -> float:
    """Add two numbers correctly."""
    return a + b


  llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0
  )

  tools = [tavily, add]

  llm_with_tools = llm.bind_tools(tools = tools)


  def calling_llm(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


  graph_builder = StateGraph(State)

  graph_builder.add_node('calling_llm', calling_llm)
  graph_builder.add_node('tools', ToolNode(tools))

  graph_builder.add_edge(START, 'calling_llm')
  graph_builder.add_conditional_edges(
    'calling_llm',
    tools_condition
  )
  graph_builder.add_edge('tools', 'calling_llm')

  graph = graph_builder.compile()
  return graph


tool_agent = make_tool_graph()
