#!/usr/bin/env python
from agents import Agent, Runner, set_default_openai_api
from playwright.async_api import async_playwright
import asyncio
import logging
import random
import uuid
import os

# Set up basic configuration for logging
logging.basicConfig(
    level=logging.WARNING,  # This enables WARNING level and higher (ERROR, CRITICAL, etc.)
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


async def grab_links(page):
    # make sure the container is in the DOM (adjust timeout if needed)
    await page.wait_for_selector("#contentScrollPaginator", timeout=15000)

    # `locator` is the modern API
    link_locator = page.locator("#contentScrollPaginator a")

    # list of element handles (if you need to click or screenshot each one)
    handles = await link_locator.element_handles()

    # or collect structured data in one go
    links = []
    count = await link_locator.count()
    for i in range(count):
        href  = await link_locator.nth(i).get_attribute("href")
        text  = await link_locator.nth(i).inner_text()
        links.append(dict(text=text.strip(), href=href))

    return links


def find_unique_links(links):
    result = set()
    for link in links:
        result.add(link["href"].split("?")[0])
    return sorted(result)


async def search_ozon(query):
    result = []
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222", slow_mo=random.randint(300, 500))
        context = await browser.new_context()
        page = await context.new_page()

        # Go to Ozon main page
        await page.goto("https://www.ozon.ru")
        
        # Fill search field and submit
        await page.mouse.move(200, 300)
        await page.wait_for_timeout(random.randint(100, 500))
        await page.fill("input[placeholder='Искать на Ozon']", query)
        await page.wait_for_timeout(random.randint(100, 500))
        await page.keyboard.press("Enter")

        # Selectors for titles and prices
        prefix = uuid.uuid4().hex
        for idx, link in enumerate(find_unique_links(await grab_links(page))):
            url = "https://www.ozon.ru{}".format(link)
            target_path = os.path.abspath("workdir/{}_{}.pdf".format(prefix, idx))
            await page.goto(url, wait_until="networkidle")
            await page.mouse.move(200, 300)
            await page.wait_for_timeout(random.randint(100, 500))
            await page.emulate_media(media="print")
            await page.pdf(path=target_path, format="A4", print_background=True)
            result.append(dict(url=url, path=target_path))
        await browser.close()
    return result


async def main():
    result = await Runner.run(triage_agent, input="Hi, how are you today?")
    print(result.final_output)
    # ¡Hola! Estoy bien, gracias por preguntar. ¿Y tú, cómo estás?


if __name__ == "__main__":
    asyncio.run(search_ozon("планшет"))
    #asyncio.run(main())
