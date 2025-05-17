# Agent used to synthesize a final report from the individual summaries.
from pydantic import BaseModel

from agents import Agent

PROMPT = (
    "You are a senior researcher tasked with writing a cohesive report for a research query. "
    "You will be provided with the original query, and some initial research done by a research "
    "assistant.\n"
    "You should first come up with an outline for the report that describes the structure and "
    "flow of the report. Then, generate the report and return that as your final output.\n"
    "The final output should be in markdown format, and it should be lengthy and detailed. Aim "
    "for 5-10 pages of content, at least 1000 words."
)
PROMPT = (
    "Ты опытный ревьювер потребительской техники. Сначала сделай короткий суммари с выбором конкретного"
    " продукта и причинами выбора. Потом сделай сравнение всех вариантов. Должен быть использован markdown "
    " для последнего отчёта."
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
)