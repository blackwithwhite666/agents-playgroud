from agents import Agent, WebSearchTool
from agents.model_settings import ModelSettings
from ..tools.search_ozon import search_ozon

INSTRUCTIONS = (
    "You are a research assistant. Given a search term, you search the ozon for that term and "
    "produce a concise summary of each product. The summary must be 2-3 paragraphs and less than 300 "
    "words in russian. Capture the price, user reviews and product description. Write one paragraph about each "
    " product with name in header. Write succinctly, no need to have complete sentences or good "
    "grammar. This will be consumed by someone synthesizing a report, so its vital you capture the "
    "essence and ignore any fluff. Do not include any additional commentary other than the summary "
    "itself."
)

search_agent = Agent(
    name="Search agent",
    instructions=INSTRUCTIONS,
    tools=[search_ozon],
    model_settings=ModelSettings(tool_choice="required"),
)