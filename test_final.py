#!/usr/bin/env python3
"""Final E2E test"""
import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=200)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})

        errors = []
        page.on("console", lambda msg: errors.append(f"{msg.type}: {msg.text}") if msg.type == "error" else None)

        # First sign up a new user
        await page.goto("http://localhost:5176/signup")
        await page.wait_for_timeout(1000)

        email = await page.query_selector('input[type="email"]')
        username = await page.query_selector('input[name="username"]')
        passwords = await page.query_selector_all('input[type="password"]')

        if email:
            await email.fill("final_test@example.com")
        if username:
            await username.fill("finaltest")
        if len(passwords) >= 1:
            await passwords[0].fill("TestPass123!")
        if len(passwords) >= 2:
            await passwords[1].fill("TestPass123!")

        submit = await page.query_selector('button[type="submit"]')
        if submit:
            await submit.click()
            await page.wait_for_timeout(2000)

        # Go to finished projects page
        print("\n1. Testing Finished Projects page...")
        await page.goto("http://localhost:5176/projects/finished")
        await page.wait_for_timeout(2000)

        # Check if Farm2Table shows
        farm2table = await page.query_selector('text=Farm2Table')
        print(f"   Farm2Table on finished page: {'✓ Found' if farm2table else '✗ Not found'}")
        await page.screenshot(path="/tmp/final_1_finished.png")

        # Go to project detail
        print("\n2. Testing Project Detail page...")
        await page.goto("http://localhost:5176/projects/Farm2Table")
        await page.wait_for_timeout(2000)
        await page.screenshot(path="/tmp/final_2_project.png")

        # Find and click Assistant button
        print("\n3. Testing Assistant chat panel...")
        assistant_btn = await page.query_selector('button:has-text("Assistant")')
        if assistant_btn:
            print("   ✓ Found Assistant button")
            await assistant_btn.click()
            await page.wait_for_timeout(1500)

            # Check for chat panel
            chat_panel = await page.query_selector('text=Project Assistant')
            if chat_panel:
                print("   ✓ Chat panel appeared!")

                # Try typing a message
                chat_input = await page.query_selector('input[placeholder*="project" i]')
                if chat_input:
                    await chat_input.fill("Hello, what is this project about?")
                    print("   ✓ Typed message")

                    send_btn = await page.query_selector('button svg')
                    if send_btn:
                        parent = await send_btn.evaluate_handle("el => el.closest('button')")
                        await parent.as_element().click()
                        print("   ✓ Clicked send")
                        await page.wait_for_timeout(5000)
            else:
                print("   ✗ Chat panel NOT found")

            await page.screenshot(path="/tmp/final_3_chat.png")
        else:
            print("   ✗ Assistant button NOT found")

        if errors:
            print(f"\n   Errors: {errors[:3]}")

        print("\n=== Test Complete ===")
        print("Browser open for 90s...")
        await page.wait_for_timeout(90000)
        await browser.close()

asyncio.run(test())
