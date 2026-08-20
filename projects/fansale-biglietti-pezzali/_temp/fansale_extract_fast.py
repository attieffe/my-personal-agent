#!/usr/bin/env python3
"""
Estrazione rapida biglietti FanSale da pagine già caricate (via browser)
Usa JavaScript per valutare il testo della pagina
"""
import json
from datetime import datetime
from pathlib import Path
import asyncio

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Install: pip install playwright")
    exit(1)


async def extract_event_data(page, event_id, data_evento):
    """Estrae biglietti da una pagina evento"""

    # Valuta il testo della pagina
    text_content = await page.evaluate(
        "() => document.body.innerText"
    )

    lines = text_content.split('\n')
    tickets = []

    for line in lines:
        if 'Ingresso' in line and 'Blocco' in line:
            tickets.append(line.strip())

    return {
        "data": data_evento,
        "evento_id": event_id,
        "biglietti_trovati": len(tickets),
        "biglietti": tickets
    }


async def main():
    # Carica config
    config_file = Path("_system/eventi_list.json")
    with open(config_file) as f:
        config = json.load(f)

    eventi = config['eventi']

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )

        page = await context.new_page()

        all_results = []

        for i, event in enumerate(eventi, 1):
            event_id = event['id']
            data = event['data']

            print(f"\n{i}. {data} (ID: {event_id})...")

            url = f"https://www.fansale.it/tickets/all/max-pezzali/482766/{event_id}"

            try:
                await page.goto(url, wait_until="load", timeout=30000)
                await asyncio.sleep(2)

                result = await extract_event_data(page, event_id, data)
                all_results.append(result)

                print(f"   ✓ {result['biglietti_trovati']} biglietti")

                # Mostra biglietti con BLOCCO B
                blocco_b = [b for b in result['biglietti'] if 'Blocco B' in b]
                if blocco_b:
                    print(f"   🔴 ALERT BLOCCO B: {len(blocco_b)} trovati")
                    for b in blocco_b[:2]:
                        print(f"      - {b[:60]}")

                await asyncio.sleep(3)

            except Exception as e:
                print(f"   ❌ Error: {str(e)[:50]}")

        await browser.close()

    # Salva risultati
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path("_logs") / f"monitor_{timestamp}.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    output_data = {
        "timestamp": datetime.now().isoformat(),
        "totale_eventi": len(all_results),
        "biglietti_per_evento": all_results,
        "alert_blocco_b": sum(1 for r in all_results if any('Blocco B' in b for b in r.get('biglietti', [])))
    }

    output_file.write_text(json.dumps(output_data, indent=2, ensure_ascii=False))
    print(f"\n✅ Report salvato: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
