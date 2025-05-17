import asyncio
from agents import set_default_openai_api
from .manager import ResearchManager

set_default_openai_api("chat_completions")

async def main() -> None:
    query = input("What would you like to research? ")
    await ResearchManager().run(query)


if __name__ == "__main__":
    asyncio.run(main())