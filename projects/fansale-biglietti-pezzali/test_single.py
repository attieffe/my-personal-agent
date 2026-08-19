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
        
        # Carica evento
        url = "https://www.fansale.it/tickets/all/max-pezzali/482766/21343715"
        print(f"Caricamento {url}...")
        await page.goto(url, wait_until="load", timeout=20000)
        await asyncio.sleep(8)
        
        # Cerca heading
        try:
            heading = await page.query_selector("h2")
            if heading:
                text = await heading.text_content()
                print(f"Primo h2 trovato: '{text}'")
        except Exception as e:
            print(f"Errore h2: {e}")
        
        # Cerca pulsante
        buttons = await page.query_selector_all("button")
        print(f"Pulsanti trovati: {len(buttons)}")
        for btn in buttons[:5]:
            text = await btn.text_content()
            if text:
                print(f"  - {text.strip()[:50]}")
        
        await browser.close()

asyncio.run(test())
