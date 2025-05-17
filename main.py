#!/usr/bin/env python
from agents import Agent, Runner, set_default_openai_api
import asyncio
import logging

# Set up basic configuration for logging
logging.basicConfig(
    level=logging.WARNING,  # This enables DEBUG level and higher (INFO, WARNING, etc.)
    format='%(asctime)s - %(levelname)s - %(message)s'
)

set_default_openai_api("chat_completions")

spanish_agent = Agent(
    name="Spanish agent",
    instructions="You only speak Spanish.",
)

english_agent = Agent(
    name="English agent",
    instructions="You only speak English",
)

triage_agent = Agent(
    name="Triage agent",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[spanish_agent, english_agent],
)


async def main():
    result = await Runner.run(triage_agent, input="Hi, how are you today?")
    print(result.final_output)
    # ¡Hola! Estoy bien, gracias por preguntar. ¿Y tú, cómo estás?

if __name__ == "__main__":
    asyncio.run(main())
