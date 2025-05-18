# Agent used to synthesize a final report from the individual summaries.
from pydantic import BaseModel

from agents import Agent

PROMPT = (
    "Ты опытный ревьювер потребительской техники. Сначала сделай tl;dr с выбором конкретного "
    "продукта под запрос пользователя и мотивацией такого выбора. Потом сделай сравнение всех вариантов. "
    "Отчёт должен быть на русском языке с использованием markdown для форматирования. "
    "Не забудь добавить ссылку на товар, показать его цену, рейтинг, кол-во отзывов, краткое описание и "
    "суммаризацию отзывов. Описание должно быть детальным, чтобы было понятно в чём разница между товарами."
)


class ReportData(BaseModel):
    short_summary: str
    """A short 2-3 sentence summary of the findings."""

    markdown_report: str
    """The final report"""


writer_agent = Agent(
    name="WriterAgent",
    instructions=PROMPT,
    output_type=ReportData,
    #model="o3"
)