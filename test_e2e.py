#!/usr/bin/env python3
"""
Comprehensive E2E test for Nexus UI
Tests landing page, sign up, sign in, and main features
"""

import asyncio
import random
import string
from playwright.async_api import async_playwright

def random_email():
    """Generate random email for testing."""
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"test_{suffix}@example.com"

async def test_nexus_e2e():
    async with async_playwright() as p:
        # Launch browser in headed mode
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=200,  # Slow down for visibility
        )
        context = await browser.new_context(viewport={"width": 1400, "height": 900})
        page = await context.new_page()

        # Enable console logging for errors
        page.on("console", lambda msg: print(f"[CONSOLE] {msg.type}: {msg.text}") if msg.type in ["error"] else None)
        page.on("pageerror", lambda err: print(f"[PAGE ERROR] {err}"))

        print("\n" + "="*60)
        print("  NEXUS E2E TEST - FULL FLOW")
        print("="*60)

        # ============================================
        # TEST 1: Landing Page
        # ============================================
        print("\n[TEST 1] Landing Page")
        print("-" * 40)

        await page.goto("http://localhost:5176/")
        await page.wait_for_load_state("networkidle")
        print("  ✓ Loaded landing page")

        # Check Sign In link
        sign_in = await page.query_selector('a[href="/signin"]')
        print(f"  Sign In link: {'✓ Found' if sign_in else '✗ Not found'}")

        # Check Get Started link
        get_started = await page.query_selector('a[href="/signup"]')
        print(f"  Get Started link: {'✓ Found' if get_started else '✗ Not found'}")

        # Verify Documentation link removed from footer
        doc_link = await page.query_selector('footer a[href="/docs"], footer router-link[to="/docs"]')
        print(f"  Footer Documentation link: {'✗ Still exists!' if doc_link else '✓ Removed'}")

        await page.screenshot(path="/tmp/test_01_landing.png")

        # ============================================
        # TEST 2: Sign Up Flow
        # ============================================
        print("\n[TEST 2] Sign Up Flow")
        print("-" * 40)

        # Click Get Started
        await page.click('a[href="/signup"]')
        await page.wait_for_load_state("networkidle")
        print(f"  ✓ Navigated to: {page.url}")

        # Generate test credentials
        test_email = random_email()
        test_username = f"testuser_{test_email.split('@')[0].split('_')[1]}"
        test_password = "TestPass123!"

        print(f"  Test email: {test_email}")
        print(f"  Test username: {test_username}")

        # Fill sign up form
        email_input = await page.query_selector('input[type="email"], input[name="email"]')
        username_input = await page.query_selector('input[name="username"], input[placeholder*="username" i]')
        password_input = await page.query_selector('input[type="password"][name="password"], input[type="password"]:first-of-type')
        confirm_password = await page.query_selector('input[name="confirmPassword"], input[type="password"]:last-of-type')

        if email_input:
            await email_input.fill(test_email)
            print("  ✓ Filled email")

        if username_input:
            await username_input.fill(test_username)
            print("  ✓ Filled username")

        if password_input:
            await password_input.fill(test_password)
            print("  ✓ Filled password")

        # Check if there's a separate confirm password field
        password_inputs = await page.query_selector_all('input[type="password"]')
        if len(password_inputs) > 1:
            await password_inputs[1].fill(test_password)
            print("  ✓ Filled confirm password")

        await page.screenshot(path="/tmp/test_02_signup_form.png")

        # Submit form
        submit_btn = await page.query_selector('button[type="submit"]')
        if submit_btn:
            await submit_btn.click()
            print("  → Submitting sign up...")
            await page.wait_for_timeout(2000)
            await page.wait_for_load_state("networkidle")

            current_url = page.url
            print(f"  Current URL: {current_url}")

            if "/signup" not in current_url:
                print("  ✓ Sign up successful!")
            else:
                # Check for error message
                error = await page.query_selector('.text-red-500, .text-error, [class*="error"]')
                if error:
                    error_text = await error.text_content()
                    print(f"  ✗ Sign up error: {error_text}")

        await page.screenshot(path="/tmp/test_03_after_signup.png")

        # ============================================
        # TEST 3: Dashboard/Projects Access
        # ============================================
        print("\n[TEST 3] Dashboard Access")
        print("-" * 40)

        # Try to access projects
        await page.goto("http://localhost:5176/projects")
        await page.wait_for_timeout(1000)
        await page.wait_for_load_state("networkidle")

        current_url = page.url
        print(f"  Current URL: {current_url}")

        if "/projects" in current_url:
            print("  ✓ Accessed projects page")

            # Look for Farm2Table or any projects
            await page.wait_for_timeout(1000)
            farm2table = await page.query_selector('text=Farm2Table')
            if farm2table:
                print("  ✓ Found Farm2Table project")
            else:
                print("  → No Farm2Table found, checking for other projects...")
                projects_list = await page.query_selector_all('[class*="project"], .card, tr')
                print(f"  Found {len(projects_list)} potential project elements")
        else:
            print(f"  → Redirected to: {current_url}")
            # If redirected to sign in, try to sign in
            if "/signin" in current_url or "/" == current_url.replace("http://localhost:5176", ""):
                print("  → Need to sign in first")

        await page.screenshot(path="/tmp/test_04_projects.png")

        # ============================================
        # TEST 4: Sign In with existing user
        # ============================================
        print("\n[TEST 4] Sign In with Demo User")
        print("-" * 40)

        await page.goto("http://localhost:5176/signin")
        await page.wait_for_load_state("networkidle")

        # Try demo user credentials
        email_input = await page.query_selector('input[type="email"], input[name="email"]')
        password_input = await page.query_selector('input[type="password"]')

        if email_input and password_input:
            await email_input.fill("demo@nexus.dev")
            await password_input.fill("demo123")  # Common demo password
            print("  ✓ Filled demo credentials")

            submit = await page.query_selector('button[type="submit"]')
            if submit:
                await submit.click()
                await page.wait_for_timeout(2000)
                await page.wait_for_load_state("networkidle")

                if "/signin" not in page.url:
                    print(f"  ✓ Signed in! Redirected to: {page.url}")
                else:
                    print("  ✗ Sign in failed - trying different password")

                    # Try other common passwords
                    for pwd in ["demouser", "Demo123!", "password", "demo"]:
                        await email_input.fill("demo@nexus.dev")
                        await password_input.fill(pwd)
                        await submit.click()
                        await page.wait_for_timeout(1500)
                        if "/signin" not in page.url:
                            print(f"  ✓ Signed in with password: {pwd}")
                            break

        await page.screenshot(path="/tmp/test_05_signin.png")

        # ============================================
        # TEST 5: Navigate to Farm2Table Project
        # ============================================
        print("\n[TEST 5] Farm2Table Project")
        print("-" * 40)

        await page.goto("http://localhost:5176/projects/Farm2Table")
        await page.wait_for_timeout(2000)
        await page.wait_for_load_state("networkidle")

        print(f"  Current URL: {page.url}")
        await page.screenshot(path="/tmp/test_06_farm2table.png")

        # Check for project elements
        project_name = await page.query_selector('text=Farm2Table')
        if project_name:
            print("  ✓ Farm2Table project loaded")

        # Look for features/kanban
        features = await page.query_selector_all('[class*="feature"], [class*="kanban"], .card')
        print(f"  Found {len(features)} feature/card elements")

        # ============================================
        # TEST 6: Assistant Chat
        # ============================================
        print("\n[TEST 6] Assistant Chat")
        print("-" * 40)

        # Look for chat input
        chat_selectors = [
            'textarea[placeholder*="message" i]',
            'textarea[placeholder*="chat" i]',
            'textarea[placeholder*="Ask" i]',
            '.chat-input textarea',
            'input[placeholder*="message" i]',
        ]

        chat_input = None
        for selector in chat_selectors:
            chat_input = await page.query_selector(selector)
            if chat_input:
                break

        if chat_input:
            print("  ✓ Found chat input")
            await chat_input.fill("What is the status of this project?")
            print("  ✓ Typed test message")

            # Look for send button
            send_btn = await page.query_selector('button:has-text("Send"), button[type="submit"]:near(textarea), button svg[class*="send" i]')
            if send_btn:
                await send_btn.click()
                print("  → Sent message, waiting for response...")
                await page.wait_for_timeout(5000)
            else:
                # Try pressing Enter
                await chat_input.press("Enter")
                print("  → Pressed Enter to send")
                await page.wait_for_timeout(5000)

            await page.screenshot(path="/tmp/test_07_chat.png")
        else:
            print("  → Chat input not visible on this page")
            # List what we can see
            textareas = await page.query_selector_all('textarea')
            print(f"    Found {len(textareas)} textarea(s) on page")

        # ============================================
        # SUMMARY
        # ============================================
        print("\n" + "="*60)
        print("  TEST COMPLETE")
        print("="*60)
        print("\nScreenshots saved to /tmp/test_*.png")
        print("Browser will stay open for 120 seconds for manual inspection...")
        print("\nYou can interact with the browser now!")

        await page.wait_for_timeout(120000)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_nexus_e2e())
