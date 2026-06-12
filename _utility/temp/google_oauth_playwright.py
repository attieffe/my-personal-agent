"""
Script Playwright per automatizzare il login OAuth Google.
Apre l'URL auth, effettua login come myjob@ingeniosolution.it, autorizza.
La redirect andrà a localhost:8085 dove oauth_flow_local.py è in ascolto.
"""
import sys
import time
from playwright.sync_api import sync_playwright

AUTH_URL = sys.argv[1] if len(sys.argv) > 1 else ""
EMAIL = "myjob@ingeniosolution.it"
PASSWORD = "Ov@9yw0eB55%u8Wt"

if not AUTH_URL:
    print("Usage: python3 google_oauth_playwright.py <AUTH_URL>")
    sys.exit(1)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
    context = browser.new_context()
    page = context.new_page()

    print(f"Apertura URL OAuth...")
    page.goto(AUTH_URL, wait_until="networkidle", timeout=30000)
    print(f"Pagina: {page.title()}")
    print(f"URL corrente: {page.url}")

    # Inserisce email
    print("Inserendo email...")
    try:
        page.wait_for_selector('input[type="email"]', timeout=10000)
        page.fill('input[type="email"]', EMAIL)
        page.click('#identifierNext button, button:has-text("Avanti"), button:has-text("Next")')
        page.wait_for_load_state("networkidle", timeout=10000)
    except Exception as e:
        print(f"Errore step email: {e}")
        page.screenshot(path="/home/openclaw/.openclaw/workspace/_attachments/temp/oauth_debug_email.png")
        browser.close()
        sys.exit(1)

    print(f"URL dopo email: {page.url}")
    page.screenshot(path="/home/openclaw/.openclaw/workspace/_attachments/temp/oauth_debug_after_email.png")

    # Inserisce password
    print("Inserendo password...")
    try:
        page.wait_for_selector('input[type="password"]', timeout=15000)
        page.fill('input[type="password"]', PASSWORD)
        page.click('#passwordNext button, button:has-text("Avanti"), button:has-text("Next")')
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception as e:
        print(f"Errore step password: {e}")
        page.screenshot(path="/home/openclaw/.openclaw/workspace/_attachments/temp/oauth_debug_password.png")
        browser.close()
        sys.exit(1)

    print(f"URL dopo password: {page.url}")
    page.screenshot(path="/home/openclaw/.openclaw/workspace/_attachments/temp/oauth_debug_after_password.png")

    # Premi "Consenti" / "Allow" se appare la schermata di consent
    try:
        consent_btn = page.query_selector('button:has-text("Consenti"), button:has-text("Allow"), #submit_approve_access')
        if consent_btn:
            print("Cliccando Consenti...")
            consent_btn.click()
            page.wait_for_load_state("networkidle", timeout=10000)
    except Exception as e:
        print(f"Consent step: {e}")

    print(f"URL finale: {page.url}")
    page.screenshot(path="/home/openclaw/.openclaw/workspace/_attachments/temp/oauth_debug_final.png")

    # Attende redirect a localhost:8085
    if "localhost:8085" in page.url or "code=" in page.url:
        print("SUCCESS: redirect a localhost catturato")
    else:
        print(f"URL finale: {page.url}")
        print("Attendo 3s per redirect...")
        time.sleep(3)
        print(f"URL dopo attesa: {page.url}")

    browser.close()
    print("Done.")
