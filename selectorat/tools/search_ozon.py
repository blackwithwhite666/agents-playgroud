from playwright.async_api import async_playwright
import random
import uuid
import os
from pathlib import Path
from PyPDF2 import PdfReader
from pydantic import BaseModel
from agents import function_tool

class Item(BaseModel):
    url: str
    text: str


def pdf_to_text(pdf_path: str | Path) -> str:
    """Return concatenated text from every page in `pdf_path`."""
    reader = PdfReader(pdf_path)
    parts: list[str] = []

    for page_num, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""       # returns "" on scanned pages
        parts.append(f"--- Page {page_num} ---\n{page_text}")

    return "\n".join(parts)


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


@function_tool
async def search_ozon(query: str) -> list[Item]:
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
            text = pdf_to_text(target_path)
            result.append(Item(url=url, text=text))
            print("\n\n=====ITEM {}=====\n".format(url))
            print("{}\n\n".format(text))
        await browser.close()
    return result