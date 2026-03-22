# -*- coding: utf-8 -*-
import json
import aiohttp
import logging
import asyncio

from typing import Tuple
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup, _IncomingMarkup
from prettytable import PrettyTable

from config import GATE_DOMAIN, BROWSER_DOMAIN


async def gate_req(
    url: str,
    # _type: Literal["get", "post"],
    **kwargs,
):
    _data = json.dumps(kwargs if kwargs else {})
    while True:
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(5 * 30)
            ) as session:
                logging.info(f"Request to {url}, data: {_data}")
                async with session.post(
                    url,
                    data=_data,
                    headers={"content-type": "application/json"},
                ) as response:
                    try:
                        if response.status == 429:
                            logging.info(f"Too Many Requests to {url}, data: {_data}")
                            await asyncio.sleep(5)
                            continue
                        _json = await response.json()
                    except aiohttp.client_exceptions.ContentTypeError as err:
                        logging.error(f"ContentTypeError occurred for {url}: {err}")
                        logging.error(
                            f"Received Content-Type: {err.headers.get('Content-Type')}"
                        )
                        _json = {}
                    return _json
        except asyncio.TimeoutError:
            logging.error(f"Timeout from API to {url}, data: {_data}")
            raise


def formation_info_by_commands(info_commands: dict) -> str:

    text = f"There's commands: \n"
    for key, data in info_commands.items():
        text += f"/{key} - {data['info']}\n"
        if "commands" in data:
            for key, data_2 in data["commands"].items():
                text += f"\t\t\t\t/{key} - {data_2['info']}\n"
    return text


def formation_total_balance_table(total_balance: dict | object) -> Tuple[str, str]:

    details = f"Details:\n\n"
    _dict = (
        total_balance.model_dump()
        if not isinstance(total_balance, dict)
        else total_balance
    )
    del _dict["total"]["unrealised_pnl"]
    for key, data in _dict["details"].items():
        if "unrealised_pnl" in data:
            del data["unrealised_pnl"]
        details += f"{key}\n"
        table = PrettyTable()
        table.field_names = [k for k in data.keys()]
        table.add_row([d for d in data.values()])
        details += f"{table.get_string()}\n"
    total = "Total:\n"
    table = PrettyTable()
    table.field_names = [k for k in _dict["total"].keys()]
    table.add_row([d for d in _dict["total"].values()])
    total += table.get_string()
    return total, details


class ParseGateIoHTML:

    @staticmethod
    async def get_page_by_request(url):

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                text = await response.text()
                return text

    @staticmethod
    def get_page_by_selenium(url):

        browser_options = Options()
        # browser_options.add_argument("--headless")
        driver = webdriver.Remote(
            command_executor=BROWSER_DOMAIN,
            options=browser_options,  # Use options or capabilities depending on Selenium version
        )
        try:
            driver.get(f"{url}")  # Замените на ваш URL
            WebDriverWait(driver, 60)  # Ждать до 2 секунд
            return driver.page_source
        finally:
            driver.quit()

    def __init__(self, html: _IncomingMarkup = None):
        self.html = html
        self.core = BeautifulSoup(
            html,
            features="html.parser",
        )

    async def get_announce(self) -> list[str]:

        article_list_info_content = self.core.find_all(
            attrs={
                "class": "overflow-hidden no-underline transition-colors text-text-text-primary hover:text-text-text-brand"
            }
        )
        info = []
        for i in range(len(article_list_info_content)):
            url = GATE_DOMAIN + article_list_info_content[i].get("href")
            title = article_list_info_content[i].find("div", class_="inline")
            timer = article_list_info_content[i].find(name="span")
            info.append(f"<b>{timer.text}</b> <a href='{url}'>{title.text}</a>")
        return info

    async def get_p2p(self) -> list[str]:

        mantine_1et1bcq_content = self.core.find_all(
            class_=lambda x: x and "w-full" in x and "mantine-1et1bcq" in x
        )
        info = []
        for i in range(len(mantine_1et1bcq_content)):
            info.append(mantine_1et1bcq_content[i].get_text(strip=True, separator=" "))
        return info
