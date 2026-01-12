#!/usr/bin/env python3
"""Quick debug test"""
import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        errors = []
        page.on("console", lambda msg: errors.append(f"{msg.type}: {msg.text}") if msg.type == "error" else None)
        page.on("pageerror", lambda err: errors.append(f"PAGE ERROR: {err}"))

        # Sign in first
        await page.goto("http://localhost:5176/signin")
        await page.wait_for_timeout(1000)

        email = await page.query_selector('input[type="email"]')
        password = await page.query_selector('input[type="password"]')
        if email and password:
            await email.fill("demo@nexus.dev")
            await password.fill("demo")
            submit = await page.query_selector('button[type="submit"]')
            if submit:
                await submit.click()
                await page.wait_for_timeout(2000)

        # Go to project
        await page.goto("http://localhost:5176/projects/Farm2Table")
        await page.wait_for_timeout(3000)

        print(f"\nURL: {page.url}")
        print(f"\nErrors: {errors}")

        # Get page text
        body = await page.query_selector('body')
        if body:
            text = await body.inner_text()
            print(f"\nPage content (first 500 chars):\n{text[:500]}")

        await page.screenshot(path="/tmp/debug_page.png")
        print("\nScreenshot: /tmp/debug_page.png")
        print("Browser open for 60s...")
        await page.wait_for_timeout(60000)
        await browser.close()

asyncio.run(test())
