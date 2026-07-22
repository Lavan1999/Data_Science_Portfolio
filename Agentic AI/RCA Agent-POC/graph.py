from langgraph.graph import StateGraph, START, END

from state import RCAState
from agents.correlation_agent import correlation_agent
from agents.analysis_agent import analysis_agent
from agents.formatter_agent import formatter_agent

# Create the graph builder
builder = StateGraph(RCAState)

builder.add_node("correlation_agent", correlation_agent)
builder.add_node("analysis_agent", analysis_agent)
builder.add_node("formatter_agent", formatter_agent)

builder.add_edge(START, "correlation_agent")
builder.add_edge("correlation_agent", "analysis_agent")
builder.add_edge("analysis_agent", "formatter_agent")
builder.add_edge("formatter_agent", END)


workflow = builder.compile()

# builder.add_node("db_agent", database_tool)
# builder.add_node("api_agent", api_tool)
# builder.add_node("log_agent", log_tool)
# builder.add_node("correlation_agent", correlation_agent)
# builder.add_node("analysis_agent", analysis_agent)
# builder.add_node("formatter_agent", formatter_agent)


# builder.add_edge(START, "db_agent")
# builder.add_edge("database_tool", "api_agent")
# builder.add_edge("api_tool", "log_tool")
# builder.add_edge("log_tool", "correlation_agent")
# builder.add_edge("correlation_agent", "analysis_agent")
# builder.add_edge("analysis_agent", "formatter_agent")
# builder.add_edge("formatter_agent", END)

# graph = builder.compile()
