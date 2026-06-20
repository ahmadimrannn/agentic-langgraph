from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather Server")

@mcp.tool()
async def get_weather(location: str) -> str:
  """Get the weather of a location"""
  return "It Snowfalls and heavily rains in Lahore, Pakistan every week."


if __name__ == "__main__":
  mcp.run(transport="streamable-http")