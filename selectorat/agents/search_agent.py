from agents import Agent, WebSearchTool
from agents.model_settings import ModelSettings
from ..tools.search_ozon import search_ozon

INSTRUCTIONS = (
    "Ты профессиональный ревьювер потребительских товаров, который должен помочь выбрать пользователю "
    "лучший товар на его запрос. Взяв выбранный поисковый запрос, ты должен найти товары на ozon и "
    " отранжировать их, оставив самые дешевые и самые популярные товары, удовлетворяющие запросу пользователя "
    " сверху, остальные оставь снизу. Обязательно сохрани название товара, ссылку на него, его цену, рейтинг, "
    " характеристики, описание и опиши почему каждый из товаров подходит под запрос пользователя."
)

search_agent = Agent(
    name="Search agent",
    instructions=INSTRUCTIONS,
    tools=[search_ozon],
    model_settings=ModelSettings(tool_choice="required"),
)