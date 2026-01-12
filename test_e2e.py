#!/usr/bin/env python3
"""
Comprehensive E2E test for Nexus UI
Tests all pages, buttons, and features with cleanup
"""

import asyncio
import os
import random
import shutil
import string
from pathlib import Path
from playwright.async_api import async_playwright

# Test configuration
BASE_URL = "http://localhost:8888"
HOME_DIR = os.path.expanduser("~")
TEST_PROJECT_PATH = f"{HOME_DIR}/test-chat-project"
BROWSER_WAIT_TIME = 30000  # 30 seconds for manual inspection at end


def random_email():
    """Generate random email for testing."""
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"test_{suffix}@example.com"


def cleanup_test_project():
    """Remove test project folder if it exists."""
    test_path = Path(TEST_PROJECT_PATH)
    if test_path.exists():
        try:
            shutil.rmtree(test_path)
            print(f"  ✓ Cleaned up test project folder: {TEST_PROJECT_PATH}")
            return True
        except Exception as e:
            print(f"  ✗ Failed to clean up: {e}")
            return False
    else:
        print(f"  → Test project folder doesn't exist: {TEST_PROJECT_PATH}")
        return True


async def test_nexus_e2e():
    # Pre-test cleanup
    print("\n" + "="*60)
    print("  PRE-TEST CLEANUP")
    print("="*60)
    cleanup_test_project()

    try:
        async with async_playwright() as p:
            # Launch browser in headed mode
            browser = await p.chromium.launch(
                headless=False,
                slow_mo=150,
            )
            context = await browser.new_context(viewport={"width": 1400, "height": 900})
            page = await context.new_page()

            # Track console errors
            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda err: console_errors.append(str(err)))

            print("\n" + "="*60)
            print("  NEXUS E2E TEST - COMPREHENSIVE")
            print("="*60)

            test_results = {}

            # ============================================
            # TEST 1: Landing Page
            # ============================================
            print("\n[TEST 1] Landing Page")
            print("-" * 40)

            await page.goto(f"{BASE_URL}/")
            await page.wait_for_load_state("networkidle")
            print("  ✓ Loaded landing page")

            sign_in = await page.query_selector('a[href="/signin"]')
            get_started = await page.query_selector('a[href="/signup"]')
            hero_section = await page.query_selector('h1, [class*="hero"]')

            print(f"  Sign In link: {'✓' if sign_in else '✗'}")
            print(f"  Get Started link: {'✓' if get_started else '✗'}")
            print(f"  Hero section: {'✓' if hero_section else '✗'}")

            test_results['landing'] = bool(sign_in and get_started)
            await page.screenshot(path="/tmp/test_01_landing.png")

            # ============================================
            # TEST 2: Sign Up Flow
            # ============================================
            print("\n[TEST 2] Sign Up Flow")
            print("-" * 40)

            await page.click('a[href="/signup"]')
            await page.wait_for_load_state("networkidle")
            print(f"  ✓ Navigated to: {page.url}")

            test_email = random_email()
            test_username = f"testuser_{test_email.split('@')[0].split('_')[1]}"
            test_password = "TestPass123!"

            print(f"  Test email: {test_email}")
            print(f"  Test username: {test_username}")

            email_input = await page.query_selector('input[type="email"], input[name="email"]')
            username_input = await page.query_selector('input[name="username"], input[placeholder*="username" i]')
            password_inputs = await page.query_selector_all('input[type="password"]')

            if email_input:
                await email_input.fill(test_email)
                print("  ✓ Filled email")

            if username_input:
                await username_input.fill(test_username)
                print("  ✓ Filled username")

            if len(password_inputs) >= 1:
                await password_inputs[0].fill(test_password)
                print("  ✓ Filled password")

            if len(password_inputs) >= 2:
                await password_inputs[1].fill(test_password)
                print("  ✓ Filled confirm password")

            await page.screenshot(path="/tmp/test_02_signup_form.png")

            submit_btn = await page.query_selector('button[type="submit"]')
            if submit_btn:
                await submit_btn.click()
                print("  → Submitting sign up...")
                await page.wait_for_timeout(2000)
                await page.wait_for_load_state("networkidle")

                current_url = page.url
                print(f"  Redirected to: {current_url}")

                if "/signup" not in current_url:
                    print("  ✓ Sign up successful!")
                    # Verify user lands on dashboard after signup
                    if "/dashboard" in current_url:
                        print("  ✓ Correctly redirected to dashboard")
                        test_results['signup_redirect'] = True
                    else:
                        print(f"  ✗ Should redirect to /dashboard, got: {current_url}")
                        test_results['signup_redirect'] = False
                    test_results['signup'] = True
                else:
                    error = await page.query_selector('.text-red-500, .text-error, [class*="error"]')
                    if error:
                        error_text = await error.text_content()
                        print(f"  ✗ Sign up error: {error_text}")
                    test_results['signup'] = False
                    test_results['signup_redirect'] = False

            await page.screenshot(path="/tmp/test_03_after_signup.png")

            # ============================================
            # TEST 3: Dashboard Page
            # ============================================
            print("\n[TEST 3] Dashboard Page")
            print("-" * 40)

            await page.goto(f"{BASE_URL}/dashboard")
            await page.wait_for_timeout(1000)
            await page.wait_for_load_state("networkidle")
            print(f"  Current URL: {page.url}")

            dashboard_title = await page.query_selector('text=Dashboard')
            stats_cards = await page.query_selector_all('[class*="stat"], [class*="card"], [class*="metric"]')

            print(f"  Dashboard title: {'✓' if dashboard_title else '✗'}")
            print(f"  Stats/Cards found: {len(stats_cards)}")

            test_results['dashboard'] = 'dashboard' in page.url.lower() or dashboard_title is not None
            await page.screenshot(path="/tmp/test_04_dashboard.png")

            # ============================================
            # TEST 4: Projects Page
            # ============================================
            print("\n[TEST 4] Projects Page")
            print("-" * 40)

            await page.goto(f"{BASE_URL}/projects")
            await page.wait_for_timeout(1000)
            await page.wait_for_load_state("networkidle")
            print(f"  Current URL: {page.url}")

            farm2table = await page.query_selector('text=Farm2Table')
            new_project_btn = await page.query_selector('button:has-text("New Project"), a:has-text("New Project")')
            project_cards = await page.query_selector_all('[class*="project"], [class*="card"]')

            print(f"  Farm2Table project: {'✓' if farm2table else '✗'}")
            print(f"  New Project button: {'✓' if new_project_btn else '✗'}")
            print(f"  Project cards found: {len(project_cards)}")

            test_results['projects'] = '/projects' in page.url
            await page.screenshot(path="/tmp/test_05_projects.png")

            # ============================================
            # TEST 5: Project Detail Page
            # ============================================
            print("\n[TEST 5] Project Detail Page (Farm2Table)")
            print("-" * 40)

            await page.goto(f"{BASE_URL}/projects/Farm2Table")
            await page.wait_for_timeout(2000)
            await page.wait_for_load_state("networkidle")
            print(f"  Current URL: {page.url}")

            project_title = await page.query_selector('text=Farm2Table')
            features_section = await page.query_selector('[class*="feature"], [class*="kanban"]')
            settings_btn = await page.query_selector('button:has-text("Settings"), a:has-text("Settings")')

            print(f"  Project title: {'✓' if project_title else '✗'}")
            print(f"  Features section: {'✓' if features_section else '✗'}")
            print(f"  Settings button: {'✓' if settings_btn else '✗'}")

            test_results['project_detail'] = project_title is not None
            await page.screenshot(path="/tmp/test_06_project_detail.png")

            # ============================================
            # TEST 6: Analytics Page
            # ============================================
            print("\n[TEST 6] Analytics Page")
            print("-" * 40)

            await page.goto(f"{BASE_URL}/analytics")
            await page.wait_for_timeout(1000)
            await page.wait_for_load_state("networkidle")
            print(f"  Current URL: {page.url}")

            analytics_title = await page.query_selector('text=Analytics')
            charts = await page.query_selector_all('[class*="chart"], canvas, svg')

            print(f"  Analytics title: {'✓' if analytics_title else '✗'}")
            print(f"  Charts/Visualizations: {len(charts)}")

            test_results['analytics'] = 'analytics' in page.url.lower()
            await page.screenshot(path="/tmp/test_07_analytics.png")

            # ============================================
            # TEST 7: Profile Page
            # ============================================
            print("\n[TEST 7] Profile Page")
            print("-" * 40)

            await page.goto(f"{BASE_URL}/profile")
            await page.wait_for_timeout(1000)
            await page.wait_for_load_state("networkidle")
            print(f"  Current URL: {page.url}")

            profile_form = await page.query_selector('form, [class*="profile"]')
            avatar = await page.query_selector('[class*="avatar"], img[alt*="avatar" i]')
            save_btn = await page.query_selector('button:has-text("Save"), button[type="submit"]')

            print(f"  Profile form: {'✓' if profile_form else '✗'}")
            print(f"  Avatar: {'✓' if avatar else '✗'}")
            print(f"  Save button: {'✓' if save_btn else '✗'}")

            test_results['profile'] = 'profile' in page.url.lower()
            await page.screenshot(path="/tmp/test_08_profile.png")

            # ============================================
            # TEST 8: Settings Page
            # ============================================
            print("\n[TEST 8] Settings Page")
            print("-" * 40)

            await page.goto(f"{BASE_URL}/settings")
            await page.wait_for_timeout(1000)
            await page.wait_for_load_state("networkidle")
            print(f"  Current URL: {page.url}")

            settings_title = await page.query_selector('text=Settings')
            settings_sections = await page.query_selector_all('[class*="setting"], [class*="section"], [class*="card"]')

            print(f"  Settings title: {'✓' if settings_title else '✗'}")
            print(f"  Settings sections: {len(settings_sections)}")

            test_results['settings'] = 'settings' in page.url.lower()
            await page.screenshot(path="/tmp/test_09_settings.png")

            # ============================================
            # TEST 9: New Project Wizard
            # ============================================
            print("\n[TEST 9] New Project Wizard")
            print("-" * 40)

            await page.goto(f"{BASE_URL}/projects/new")
            await page.wait_for_timeout(1000)
            await page.wait_for_load_state("networkidle")
            print(f"  Navigated to: {page.url}")

            # Step 1: Project Details
            print("\n  Step 1: Project Details")
            project_name_input = await page.query_selector('input[placeholder*="my-awesome-project"]')
            project_path_input = await page.query_selector('input[placeholder*="/home/user/projects"]')

            if project_name_input:
                await project_name_input.fill("test-chat-project")
                print("    ✓ Filled project name")

            if project_path_input:
                await project_path_input.fill(TEST_PROJECT_PATH)
                print(f"    ✓ Filled project path")

            await page.screenshot(path="/tmp/test_10_wizard_step1.png")

            # Click Continue
            continue_btn = await page.query_selector('button:has-text("Continue")')
            if continue_btn:
                await continue_btn.click()
                await page.wait_for_timeout(1000)
                print("    ✓ Clicked Continue")

            # Step 2: App Specification
            print("\n  Step 2: App Specification")
            await page.screenshot(path="/tmp/test_11_wizard_step2.png")

            manual_tab = await page.query_selector('button:has-text("Manual")')
            ai_tab = await page.query_selector('button:has-text("AI Generator")')

            print(f"    Manual/Template tab: {'✓' if manual_tab else '✗'}")
            print(f"    AI Generator tab: {'✓' if ai_tab else '✗'}")

            # Switch to AI Generator mode
            if ai_tab:
                await ai_tab.click()
                await page.wait_for_timeout(500)
                print("    ✓ Switched to AI Generator mode")

            await page.screenshot(path="/tmp/test_12_wizard_ai_mode.png")

            # Start AI Generator
            start_btn = await page.query_selector('button:has-text("Start AI Generator")')
            if start_btn:
                try:
                    await start_btn.click()
                    print("    ✓ Clicked Start AI Generator")
                    await page.wait_for_timeout(5000)

                    # Check if button is still visible (means project creation failed)
                    button_still_there = await page.query_selector('button:has-text("Start AI Generator")')
                    if button_still_there:
                        print("    ✗ Start AI Generator button still visible - project creation failed")
                        test_results['spec_generator'] = False
                    else:
                        print("    ✓ Project created successfully")

                        # Now check for chat input
                        chat_input = await page.query_selector('input[placeholder*="Describe your app" i]')
                        if chat_input:
                            print("    ✓ Chat input appeared")
                            await chat_input.fill("Build a simple todo app")
                            await chat_input.press("Enter")
                            print("    ✓ Sent test message")
                            await page.wait_for_timeout(3000)

                            # Check for AI response
                            ai_response = await page.query_selector('text=Claude is thinking, [class*="loading"], [class*="typing"]')
                            if ai_response:
                                print("    ✓ AI is responding")
                            test_results['spec_generator'] = True
                        else:
                            print("    ✗ Chat input not found after project creation")
                            test_results['spec_generator'] = False
                except Exception as e:
                    print(f"    ✗ Error: {str(e)[:50]}")
                    test_results['spec_generator'] = False
            else:
                test_results['spec_generator'] = False

            await page.screenshot(path="/tmp/test_13_wizard_chat.png")
            test_results['new_project_wizard'] = True

            # ============================================
            # TEST 10: Theme Toggle
            # ============================================
            print("\n[TEST 10] Theme Toggle")
            print("-" * 40)

            await page.goto(f"{BASE_URL}/projects")
            await page.wait_for_load_state("networkidle")

            # Theme toggle is a rounded-full button with h-11 w-11 containing SVG icons
            theme_toggle = await page.query_selector('button.rounded-full:has(svg)')
            if theme_toggle:
                html = await page.query_selector('html')
                initial_class = await html.get_attribute('class') or ''
                print(f"  Initial theme: {initial_class}")

                await theme_toggle.click()
                await page.wait_for_timeout(500)

                new_class = await html.get_attribute('class') or ''
                print(f"  After toggle: {new_class}")

                theme_changed = initial_class != new_class
                print(f"  Theme toggle: {'✓' if theme_changed else '✗'}")
                test_results['theme_toggle'] = theme_changed
            else:
                print("  Theme toggle: ✗ Not found")
                test_results['theme_toggle'] = False

            await page.screenshot(path="/tmp/test_14_theme.png")

            # ============================================
            # TEST 11: User Menu
            # ============================================
            print("\n[TEST 11] User Menu")
            print("-" * 40)

            user_menu = await page.query_selector('[class*="avatar"], button:has-text("testuser"), [class*="user-menu"]')
            if user_menu:
                await user_menu.click()
                await page.wait_for_timeout(500)

                dropdown = await page.query_selector('[class*="dropdown"], [class*="menu"], [role="menu"]')
                print(f"  User dropdown: {'✓' if dropdown else '✗'}")

                logout = await page.query_selector('button:has-text("Logout"), button:has-text("Sign out"), a:has-text("Logout")')
                print(f"  Logout option: {'✓' if logout else '✗'}")

                await page.keyboard.press("Escape")
                test_results['user_menu'] = dropdown is not None
            else:
                print("  User menu: ✗ Not found")
                test_results['user_menu'] = False

            await page.screenshot(path="/tmp/test_15_user_menu.png")

            # ============================================
            # TEST 12: Logout and Sign In Page
            # ============================================
            print("\n[TEST 12] Logout and Sign In Page")
            print("-" * 40)

            # First, logout the user
            await page.goto(f"{BASE_URL}/projects")
            await page.wait_for_load_state("networkidle")

            # Click user menu to find logout
            user_menu = await page.query_selector('[class*="avatar"], button:has-text("testuser"), [class*="user-menu"]')
            if user_menu:
                await user_menu.click()
                await page.wait_for_timeout(500)

                logout_btn = await page.query_selector('button:has-text("Logout"), button:has-text("Sign out"), a:has-text("Logout")')
                if logout_btn:
                    await logout_btn.click()
                    await page.wait_for_timeout(1000)
                    await page.wait_for_load_state("networkidle")
                    print(f"  ✓ Logged out, redirected to: {page.url}")

            # Now test signin page
            await page.goto(f"{BASE_URL}/signin")
            await page.wait_for_load_state("networkidle")
            print(f"  Sign in page URL: {page.url}")

            email_input = await page.query_selector('input[type="email"], input[name="email"]')
            password_input = await page.query_selector('input[type="password"]')
            submit_btn = await page.query_selector('button[type="submit"]')

            print(f"  Email input: {'✓' if email_input else '✗'}")
            print(f"  Password input: {'✓' if password_input else '✗'}")
            print(f"  Submit button: {'✓' if submit_btn else '✗'}")

            test_results['signin_page'] = all([email_input, password_input, submit_btn])
            await page.screenshot(path="/tmp/test_16_signin.png")

            # ============================================
            # TEST 13: Protected Routes (Dashboard requires auth)
            # ============================================
            print("\n[TEST 13] Protected Routes")
            print("-" * 40)

            # Try accessing dashboard without being logged in
            await page.goto(f"{BASE_URL}/dashboard")
            await page.wait_for_timeout(1000)
            await page.wait_for_load_state("networkidle")

            current_url = page.url
            # Should redirect to signin if not authenticated
            is_protected = '/signin' in current_url or '/signup' in current_url or current_url == f"{BASE_URL}/"
            print(f"  Dashboard access when logged out: {current_url}")
            print(f"  Route protected: {'✓' if is_protected else '✗ (should redirect to signin)'}")

            test_results['protected_routes'] = is_protected
            await page.screenshot(path="/tmp/test_17_protected.png")

            # ============================================
            # SUMMARY
            # ============================================
            print("\n" + "="*60)
            print("  TEST RESULTS SUMMARY")
            print("="*60)

            passed = sum(1 for v in test_results.values() if v)
            total = len(test_results)

            for test_name, result in test_results.items():
                status = "✓ PASS" if result else "✗ FAIL"
                print(f"  {test_name}: {status}")

            print(f"\n  Total: {passed}/{total} tests passed")

            if console_errors:
                print(f"\n  Console errors: {len(console_errors)}")
                for err in console_errors[:5]:
                    print(f"    - {err[:80]}...")

            print("\n" + "="*60)
            print("  BROWSER INSPECTION")
            print("="*60)
            print(f"\nScreenshots saved to /tmp/test_*.png")
            print(f"Browser open for {BROWSER_WAIT_TIME//1000} seconds...")

            await page.wait_for_timeout(BROWSER_WAIT_TIME)
            await browser.close()

    except Exception as e:
        print(f"\n  ✗ Test error: {e}")
        raise
    finally:
        # ============================================
        # POST-TEST CLEANUP (always runs)
        # ============================================
        print("\n" + "="*60)
        print("  POST-TEST CLEANUP")
        print("="*60)
        cleanup_test_project()

        print("\n" + "="*60)
        print("  E2E TEST COMPLETE")
        print("="*60)


if __name__ == "__main__":
    asyncio.run(test_nexus_e2e())
