from pydantic import BaseModel

from agents import Agent

PROMPT = (
    "You are a helpful research assistant. Given a query, come up with a set of ozon (it's a marketplace) searches "
    "to perform to best answer the query. Output between 1 and 2 terms to query for."
    " Queries should be in russian and simple, like 'планшет для учёбы'."
)


class WebSearchItem(BaseModel):
    reason: str
    "Your reasoning for why this search is important to the query."

    query: str
    "The search term to use for the web search."


class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem]
    """A list of searches to perform to best answer the query."""


planner_agent = Agent(
    name="PlannerAgent",
    instructions=PROMPT,
    model="gpt-4o",
    output_type=WebSearchPlan,
)