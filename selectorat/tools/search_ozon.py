from playwright.async_api import async_playwright
import random
import uuid
import os
from pydantic import BaseModel
from agents import function_tool
import openai
import base64

class Item(BaseModel):
    url: str
    text: str


async def extract_text_from_image(query: str, path: str):
    with open(path, 'rb') as buf:
        b64_image = base64.b64encode(buf.read()).decode("utf-8")
    prompt = "Ты профессиональный ревьювер потребительских товаров. " \
    "Сформируй описание продукта в формате ключ значение в формате markdown, но не выделят отдельным блоком. " \
    "Не перепутай количество отзывов с ценой, количество находится внизу страницы, рядом с заголовком 'Отзывы о товаре'. " \
    "Суммаризация отзывов и описания должны быть не меньше 100 слов. " \
    "Среди ключей обязательно должны быть название продукта, бренд, категория, цена, количество отзывов, рейтинг, " \
    "основные характеристики, суммаризация отзывов, суммаризация описания, плюсы, минусы. " \
    f"В конце объясни почему продукт удовлетворяет запросу пользователя '{query}'."
    client = openai.AsyncOpenAI()
    response = await client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": f"data:image/png;base64,{b64_image}"},
                ],
            }
        ],
    )
    return response.output[0].content[0].text


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


async def auto_scroll(page):
    await page.evaluate("""
        async () => {
            let tries = 0;
            await new Promise((resolve) => {
                let totalHeight = 0;
                const distance = 100;
                const timer = setInterval(() => {
                    window.scrollBy(0, distance);
                    tries += 1;
                    totalHeight += distance;
                    if (totalHeight >= document.body.scrollHeight) {
                        clearInterval(timer);
                        resolve();
                    } else if (tries > 10) {
                        resolve();
                    }
                }, 100);
            });
        }
    """)


@function_tool
async def search_ozon(query: str) -> list[Item]:
    result = []
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222", slow_mo=random.randint(300, 500))
        context = await browser.new_context()
        page = await context.new_page()
        await page.wait_for_timeout(random.randint(100, 500))

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
            path = os.path.abspath("workdir/{}_{}.png".format(prefix, idx))
            await page.goto(url, wait_until="networkidle")
            await page.mouse.move(200, 300)
            await page.wait_for_timeout(random.randint(100, 500))
            await auto_scroll(page)
            await page.evaluate("""() => {
                document.querySelectorAll('[data-widget="skuShelfGoods"]').forEach(el => el.remove());
                document.querySelectorAll('[data-widget="skuGrid"]').forEach(el => el.remove());
            }""")
            await page.screenshot(path=path, full_page=True)
            text = await extract_text_from_image(query, path)
            text = f"## {url}\n{text}\n"
            result.append(Item(url=url, text=text))
            print(f"\n=====ITEM {url}=====\n{text}\n")
        await browser.close()
    return result