#!/usr/bin/env python3
"""Quick test to click Assistant button"""

import asyncio
from playwright.async_api import async_playwright

async def test_assistant():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context(viewport={"width": 1400, "height": 900})
        page = await context.new_page()

        # Capture ALL console messages
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: console_messages.append(f"PAGE ERROR: {err}"))

        print("\n=== Testing Assistant Button ===\n")

        # Go directly to Farm2Table project
        print("1. Navigating to Farm2Table project...")
        await page.goto("http://localhost:5176/projects/Farm2Table")
        await page.wait_for_timeout(2000)
        await page.wait_for_load_state("networkidle")

        print(f"   Current URL: {page.url}")

        # Check if we're redirected to signin
        if "/signin" in page.url or page.url == "http://localhost:5176/":
            print("   Need to sign in first...")
            await page.goto("http://localhost:5176/signup")
            await page.wait_for_load_state("networkidle")

            email = await page.query_selector('input[type="email"]')
            username = await page.query_selector('input[name="username"]')
            passwords = await page.query_selector_all('input[type="password"]')

            if email:
                await email.fill("assistant_test3@example.com")
            if username:
                await username.fill("assistanttest3")
            if len(passwords) >= 1:
                await passwords[0].fill("TestPass123!")
            if len(passwords) >= 2:
                await passwords[1].fill("TestPass123!")

            submit = await page.query_selector('button[type="submit"]')
            if submit:
                await submit.click()
                await page.wait_for_timeout(2000)

            await page.goto("http://localhost:5176/projects/Farm2Table")
            await page.wait_for_timeout(3000)

        print(f"   Final URL: {page.url}")

        # Look for Assistant button
        print("\n2. Looking for Assistant button...")
        assistant_btn = await page.query_selector('button:has-text("Assistant")')

        if assistant_btn:
            print("   ✓ Found Assistant button")

            # Clear console messages before clicking
            console_messages.clear()

            print("   Clicking Assistant button...")
            await assistant_btn.click()
            await page.wait_for_timeout(1000)

            # Try clicking again if first click didn't work
            html = await page.content()
            if "Project Assistant" not in html:
                print("   First click didn't work, trying JavaScript click...")
                await page.evaluate("""() => {
                    const btn = document.querySelector('button');
                    const buttons = document.querySelectorAll('button');
                    for (const b of buttons) {
                        if (b.textContent.includes('Assistant')) {
                            b.click();
                            break;
                        }
                    }
                }""")
                await page.wait_for_timeout(1000)

            # Try to directly toggle via Vue
            print("   Trying to toggle showAssistant via JS...")
            await page.evaluate("""() => {
                // Find the Vue app instance
                const app = document.querySelector('#app').__vue_app__;
                if (app) {
                    console.log('Found Vue app');
                }
            }""")

            # Scroll down to see if panel is below
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(500)

            html = await page.content()
            if "Project Assistant" in html:
                print("   ✓ Chat panel HTML found after scroll!")
            else:
                print("   ✗ Chat panel HTML still NOT found")

            # Print any errors
            errors = [m for m in console_messages if 'error' in m.lower() or 'fail' in m.lower() or 'warn' in m.lower()]
            if errors:
                print("\n   Console errors/warnings after click:")
                for e in errors[:10]:
                    print(f"     {e[:150]}")

            # Look for the chat panel div anywhere
            chat_panel = await page.query_selector('text=Project Assistant')
            if chat_panel:
                print("   ✓ Found 'Project Assistant' text")
                is_visible = await chat_panel.is_visible()
                print(f"   Visible: {is_visible}")
            else:
                print("   ✗ 'Project Assistant' text NOT found")

            await page.screenshot(path="/tmp/assistant_debug.png", full_page=True)

        else:
            print("   ✗ Assistant button NOT found!")

        # Print all console messages
        print("\n3. Recent console messages:")
        for msg in console_messages[-15:]:
            print(f"   {msg[:120]}")

        print("\n=== Test Complete ===")
        print("Full page screenshot: /tmp/assistant_debug.png")
        print("Browser staying open for 90s - try clicking Assistant button manually...")
        await page.wait_for_timeout(90000)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_assistant())
