#!/usr/bin/env python
"""
Script to scrape a website and download CSV data using Playwright.
"""
import os
import argparse
import asyncio
import time
from typing import Optional, Tuple

from playwright.async_api import async_playwright, Page, Browser

async def scrape_and_download(
    url: str, 
    browser_type: str = "chromium", 
    download_timeout: int = 30, 
    headless: bool = True
) -> Tuple[bool, Optional[str]]:
    """
    Scrape website and download CSV by clicking the download button using Playwright.
    
    Parameters
    ----------
    url : str
        URL of the website containing the table and download button
    browser_type : str, optional
        Browser to use ('chromium', 'firefox', or 'webkit'), default 'chromium'
    download_timeout : int, optional
        Timeout in seconds to wait for download, default 30
    headless : bool, optional
        Whether to run browser in headless mode, default True
        
    Returns
    -------
    Tuple[bool, Optional[str]]
        Success status and error message if any
    """
    async with async_playwright() as playwright:
        # Choose browser based on parameter
        if browser_type == "firefox":
            browser_class = playwright.firefox
        elif browser_type == "webkit":
            browser_class = playwright.webkit
        else:
            browser_class = playwright.chromium
        
        # Set up download directory
        downloads_path = os.path.abspath(os.path.join(os.getcwd(), "downloads"))
        os.makedirs(downloads_path, exist_ok=True)
        
        try:
            # Launch browser with specific viewport and user agent
            browser = await browser_class.launch(headless=headless)
            
            # Create a context with specific user agent and viewport
            context = await browser.new_context(
                accept_downloads=True,
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
            )
            
            page = await context.new_page()
            
            # Set default timeout to be longer
            page.set_default_timeout(60000)  # 60 seconds
            
            # Navigate to the URL
            print(f"Loading page: {url}")
            await page.goto(url, wait_until="networkidle")  # Wait for the full page to load
            
            # Wait for the data to load
            await asyncio.sleep(2)
            
            # Try to find the download button
            selectors = [
                '#download-sheet',  # ID selector
                'button#download-sheet',  # Button with ID
                'button:has-text("Download")',  # Button with text
                'button:has-text("Export")',  # Alternative text
                'a:has-text("Download")',  # Link with text
            ]
            
            download_button = None
            for selector in selectors:
                try:
                    print(f"Looking for element with selector: {selector}")
                    # Wait a bit and try to find the element
                    download_button = await page.wait_for_selector(selector, timeout=5000, state="visible")
                    if download_button:
                        print(f"Found download button with selector: {selector}")
                        break
                except Exception:
                    continue
            
            if not download_button:
                try:
                    # Try with the XPath
                    xpath = '//*[@id="download-sheet"]'
                    print(f"Looking for element with XPath: {xpath}")
                    download_button = await page.wait_for_selector(f"xpath={xpath}", timeout=5000, state="visible")
                except Exception:
                    return False, "Download button not found with any selector"
            
            if not download_button:
                return False, "Download button not found"
            
            # Wait for content to be fully loaded
            print("Waiting for page data to fully load...")
            await asyncio.sleep(3)
            
            # Make sure the page is fully rendered
            await page.wait_for_load_state("networkidle")
            
            # Set up download event
            download_event = asyncio.create_task(setup_download_handler(page, downloads_path))
            
            # Click the button
            print("Clicking download button")
            await download_button.click()
            
            # Wait for download to complete
            print(f"Waiting for download...")
            downloaded_path = await asyncio.wait_for(download_event, timeout=download_timeout)
            
            if downloaded_path:
                # Copy file to current directory
                filename = os.path.basename(downloaded_path)
                destination = os.path.join(os.getcwd(), filename)
                
                # Read and write the file to avoid permission issues
                with open(downloaded_path, 'rb') as src_file:
                    content = src_file.read()
                
                with open(destination, 'wb') as dest_file:
                    dest_file.write(content)
                
                # Verify the file has content
                file_size = os.path.getsize(destination)
                if file_size < 100:  # If file is suspiciously small
                    print(f"Warning: Downloaded file is very small ({file_size} bytes)")
                    if headless:
                        print("Retrying with non-headless mode...")
                        return await scrape_and_download(url, browser_type, download_timeout, False)
                
                print(f"Downloaded: {filename} ({os.path.getsize(destination)} bytes)")
                return True, None
            else:
                return False, "Download failed or timed out"
        
        except Exception as e:
            return False, f"Error: {str(e)}"
        
        finally:
            try:
                await browser.close()
            except Exception:
                pass

async def setup_download_handler(page: Page, download_path: str) -> str:
    """
    Set up a handler for download events.
    
    Parameters
    ----------
    page : Page
        Playwright page object
    download_path : str
        Path where downloads should be saved
        
    Returns
    -------
    str
        Path to the downloaded file
    """
    # Wait for download to start
    download = await page.wait_for_event('download')
    
    # Wait for download to complete
    path = await download.path()
    
    # Save to the specified path
    suggested_filename = download.suggested_filename
    save_path = os.path.join(download_path, suggested_filename)
    
    # Make sure the directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # Save the downloaded file
    await download.save_as(save_path)
    
    return save_path

async def verify_file_content(file_path: str) -> bool:
    """
    Verify that the downloaded CSV file has proper content.
    
    Parameters
    ----------
    file_path : str
        Path to the CSV file
        
    Returns
    -------
    bool
        True if file has proper content, False otherwise
    """
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
        # Check if we have more than just a header row
        if len(lines) <= 1:
            print(f"Warning: CSV file only has {len(lines)} lines")
            return False
            
        return True
    except Exception as e:
        print(f"Error verifying file content: {str(e)}")
        return False

async def main_async():
    """Async main function to parse arguments and run the scraper."""
    parser = argparse.ArgumentParser(description="Web scraper to download CSV using Playwright")
    parser.add_argument("url", help="URL of the website with the table and download button")
    parser.add_argument(
        "--browser", 
        choices=["chromium", "firefox", "webkit"],
        default="chromium",
        help="Browser to use (default: chromium)"
    )
    parser.add_argument(
        "--timeout", 
        type=int, 
        default=30, 
        help="Timeout in seconds to wait for download (default: 30)"
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Run browser in non-headless mode (visible)"
    )
    parser.add_argument(
        "--verify-content",
        action="store_true",
        help="Verify file has proper content and retry if needed"
    )
    
    args = parser.parse_args()
    
    headless = not args.no_headless
    success, error = await scrape_and_download(
        args.url, 
        args.browser, 
        args.timeout, 
        headless
    )
    
    # If verification is requested and we're in headless mode
    if success and args.verify_content and headless:
        filename = os.path.basename(args.url.rstrip('/')) + ".csv"
        if not os.path.exists(filename):
            # Try to find the downloaded file
            downloaded_files = [f for f in os.listdir() if f.endswith('.csv') and os.path.isfile(f)]
            if downloaded_files:
                filename = downloaded_files[0]
            else:
                filename = None
        
        if filename and not await verify_file_content(filename):
            print("Downloaded file appears to be incomplete. Retrying in non-headless mode...")
            success, error = await scrape_and_download(
                args.url, 
                args.browser, 
                args.timeout, 
                False  # Use non-headless mode
            )
    
    if success:
        print("CSV downloaded successfully!")
    else:
        print(f"Failed to download CSV: {error}")
        exit(1)

def main():
    """Main function to run the async event loop."""
    asyncio.run(main_async())

if __name__ == "__main__":
    main()

