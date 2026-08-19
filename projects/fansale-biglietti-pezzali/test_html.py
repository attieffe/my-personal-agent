#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def test():
    async with Stealth().use_async(async_playwright()) as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="it-IT",
            timezone_id="Europe/Rome"
        )
        page = await context.new_page()
        
        url = "https://www.fansale.it/tickets/all/max-pezzali/482766/21343715"
        await page.goto(url, wait_until="load", timeout=20000)
        await asyncio.sleep(8)
        
        # Salva HTML
        html = await page.content()
        with open("/tmp/fansale_page.html", "w") as f:
            f.write(html)
        
        print(f"HTML salvato: {len(html)} caratteri")
        print("Cerca 'Biglietti':", "Biglietti" in html)
        print("Cerca 'Carica':", "Carica" in html)
        print("Cerca 'Quantità':", "Quantità" in html)
        
        await browser.close()

asyncio.run(test())
