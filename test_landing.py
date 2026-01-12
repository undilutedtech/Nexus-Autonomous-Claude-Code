#!/usr/bin/env python3
"""
E2E test for landing page buttons using Playwright
Run with: python test_landing.py
"""

import asyncio
from playwright.async_api import async_playwright

async def test_landing_page():
    async with async_playwright() as p:
        # Launch browser in headed mode so user can see
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        page = await context.new_page()

        # Enable console logging
        page.on("console", lambda msg: print(f"[CONSOLE] {msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: print(f"[PAGE ERROR] {err}"))

        print("\n=== Testing Landing Page ===\n")

        # Navigate to landing page
        print("1. Navigating to http://localhost:5176/")
        await page.goto("http://localhost:5176/")
        await page.wait_for_load_state("networkidle")

        # Take screenshot
        await page.screenshot(path="/tmp/landing_page.png")
        print("   Screenshot saved to /tmp/landing_page.png")

        # Find all buttons and links
        print("\n2. Finding buttons on page...")
        buttons = await page.query_selector_all("button")
        links = await page.query_selector_all("a")

        print(f"   Found {len(buttons)} buttons and {len(links)} links")

        for i, btn in enumerate(buttons):
            text = await btn.text_content()
            is_visible = await btn.is_visible()
            is_enabled = await btn.is_enabled()
            print(f"   Button {i+1}: '{text.strip()}' visible={is_visible} enabled={is_enabled}")

        # Look for Sign In button
        print("\n3. Looking for 'Sign In' button...")
        sign_in_btn = await page.query_selector("text=Sign In")
        if sign_in_btn:
            print("   Found 'Sign In' button")
            # Check if it has click handler
            tag = await sign_in_btn.evaluate("el => el.tagName")
            href = await sign_in_btn.evaluate("el => el.href || 'none'")
            onclick = await sign_in_btn.evaluate("el => el.onclick ? 'has onclick' : 'no onclick'")
            print(f"   Tag: {tag}, href: {href}, onclick: {onclick}")

            # Try clicking
            print("   Clicking 'Sign In'...")
            await sign_in_btn.click()
            await page.wait_for_timeout(1000)

            current_url = page.url
            print(f"   Current URL after click: {current_url}")
            await page.screenshot(path="/tmp/after_signin_click.png")
        else:
            print("   'Sign In' button not found!")

        # Go back to landing if navigated away
        if "localhost:5176" in page.url and page.url != "http://localhost:5176/":
            await page.goto("http://localhost:5176/")
            await page.wait_for_load_state("networkidle")

        # Look for Getting Started button
        print("\n4. Looking for 'Getting Started' or 'Get Started' button...")
        get_started_btn = await page.query_selector("text=Get Started")
        if not get_started_btn:
            get_started_btn = await page.query_selector("text=Getting Started")

        if get_started_btn:
            print("   Found 'Get Started' button")
            tag = await get_started_btn.evaluate("el => el.tagName")
            href = await get_started_btn.evaluate("el => el.href || 'none'")
            onclick = await get_started_btn.evaluate("el => el.onclick ? 'has onclick' : 'no onclick'")
            print(f"   Tag: {tag}, href: {href}, onclick: {onclick}")

            # Try clicking
            print("   Clicking 'Get Started'...")
            await get_started_btn.click()
            await page.wait_for_timeout(1000)

            current_url = page.url
            print(f"   Current URL after click: {current_url}")
            await page.screenshot(path="/tmp/after_getstarted_click.png")
        else:
            print("   'Get Started' button not found!")

        # Check Vue router
        print("\n5. Checking Vue Router state...")
        router_info = await page.evaluate("""() => {
            if (window.__VUE_DEVTOOLS_GLOBAL_HOOK__) {
                return 'Vue detected';
            }
            return 'Vue not detected';
        }""")
        print(f"   {router_info}")

        # Keep browser open for inspection
        print("\n=== Test Complete ===")
        print("Browser will stay open for 30 seconds for inspection...")
        print("Check /tmp/landing_page.png, /tmp/after_signin_click.png, /tmp/after_getstarted_click.png")

        await page.wait_for_timeout(30000)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_landing_page())
