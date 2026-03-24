#!/usr/bin/env python3
"""
Spider - Web image scraper
Recursively downloads images from a website
"""

import argparse
import sys
import os
from pathlib import Path
import requests
from urllib.parse import urlparse, urljoin
import time
from bs4 import BeautifulSoup


class Spider:
    """Web scraper for downloading images"""

    VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    DEFAULT_PATH = './data/'
    DEFAULT_DEPTH = 5

    def __init__(self, url, recursive=False, depth=DEFAULT_DEPTH, path=DEFAULT_PATH):
        self.url = url
        self.recursive = recursive
        self.depth = depth
        self.path = path
        self.downloaded = set()
        self.visited_urls = set()

        # HTTP configuration
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.session.timeout = 10  # 10 second timeout


    def validate_url(self, url):
        """
        Validate URL format and return normalized URL.

        Returns:
            str: Normalized URL or None if invalid
        """
        try:
            parsed = urlparse(url)

            # Check if scheme exists, add http:// if missing
            if not parsed.scheme:
                url = 'http://' + url
                parsed = urlparse(url)

            # Valid schemes only
            if parsed.scheme not in ['http', 'https']:
                print(f"❌ Error: Invalid URL scheme '{parsed.scheme}'. Only http/https allowed.")
                return None

            # Check if netloc (domain) exists
            if not parsed.netloc:
                print(f"❌ Error: Invalid URL - missing domain.")
                return None

            return url
        except Exception as e:
            print(f"❌ Error: Invalid URL format - {e}")
            return None

    def fetch_page(self, url):
        """
        Fetch a webpage and return the HTML content.

        Args:
            url (str): URL to fetch

        Returns:
            str: HTML content or None if failed
        """
        try:
            response = self.session.get(url, allow_redirects=True)

            # Handle status codes
            if response.status_code == 200:
                return response.text
            elif response.status_code == 404:
                print(f"⚠️  Warning: Page not found (404) - {url}")
                return None
            elif response.status_code == 403:
                print(f"⚠️  Warning: Access forbidden (403) - {url}")
                return None
            elif response.status_code == 429:
                print(f"⚠️  Warning: Too many requests (429) - Rate limited. Waiting...")
                time.sleep(5)
                return None
            elif 500 <= response.status_code < 600:
                print(f"⚠️  Warning: Server error ({response.status_code}) - {url}")
                return None
            else:
                print(f"⚠️  Warning: Unexpected status code ({response.status_code}) - {url}")
                return None

        except requests.exceptions.Timeout:
            print(f"❌ Error: Request timeout - {url}")
            return None
        except requests.exceptions.ConnectionError:
            print(f"❌ Error: Connection failed - {url}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: Request failed - {e}")
            return None

    def is_valid_image(self, url):
        """
        Check if URL points to a valid image file.

        Args:
            url (str): URL to check

        Returns:
            bool: True if valid image extension, False otherwise
        """
        try:
            # Remove query parameters and fragments
            path = urlparse(url).path.lower()
            # Check if any valid extension is in the path
            return any(path.endswith(ext) for ext in self.VALID_EXTENSIONS)
        except Exception:
            return False

    def resolve_url(self, img_url, base_url):
        """
        Convert relative URLs to absolute URLs.

        Args:
            img_url (str): Image URL (can be relative or absolute)
            base_url (str): Base URL for resolving relative URLs

        Returns:
            str: Absolute URL or None if invalid
        """
        try:
            # Use urljoin to handle both absolute and relative URLs
            absolute_url = urljoin(base_url, img_url)

            # Validate the result
            parsed = urlparse(absolute_url)
            if parsed.scheme in ['http', 'https'] and parsed.netloc:
                return absolute_url
            return None
        except Exception:
            return None

    def extract_images(self, html_content, base_url):
        """
        Parse HTML and extract all valid image URLs.

        Args:
            html_content (str): HTML page content
            base_url (str): Base URL for resolving relative URLs

        Returns:
            list: List of absolute image URLs with valid extensions
        """
        image_urls = []

        try:
            soup = BeautifulSoup(html_content, 'lxml')

            # Find all <img> tags
            img_tags = soup.find_all('img')

            if not img_tags:
                print("   ℹ️  No images found on this page")
                return image_urls

            print(f"   Found {len(img_tags)} <img> tags")

            for img in img_tags:
                # Get src attribute
                src = img.get('src')
                if not src:
                    continue

                # Also check srcset for responsive images (use first one)
                if not src and img.get('srcset'):
                    srcset = img.get('srcset').split(',')[0].strip().split()[0]
                    src = srcset

                if not src:
                    continue

                # Resolve relative URLs to absolute
                absolute_url = self.resolve_url(src, base_url)
                if not absolute_url:
                    continue

                # Filter by valid extensions
                if not self.is_valid_image(absolute_url):
                    continue

                # Avoid duplicates
                if absolute_url not in image_urls:
                    image_urls.append(absolute_url)

            print(f"   ✅ Extracted {len(image_urls)} valid image URLs")
            return image_urls

        except Exception as e:
            print(f"   ❌ Error parsing HTML: {e}")
            return image_urls

    def run(self):
        """Main execution"""
        print(f"🕷️  Spider starting...")
        print(f"   URL: {self.url}")
        print(f"   Recursive: {self.recursive}, Depth: {self.depth}, Path: {self.path}")
        print()

        # Phase 1: Validate URL
        print("📋 Phase 1: Validating URL...")
        validated_url = self.validate_url(self.url)
        if not validated_url:
            print("❌ Spider failed: Invalid URL")
            sys.exit(1)
        print(f"✅ URL valid: {validated_url}")
        print()

        # Phase 1: Fetch page
        print("📋 Phase 1: Fetching page...")
        html_content = self.fetch_page(validated_url)
        if not html_content:
            print("❌ Spider failed: Could not fetch page")
            sys.exit(1)
        print(f"✅ Page fetched successfully ({len(html_content)} bytes)")
        print()

        # Phase 2: Extract images
        print("📋 Phase 2: Extracting images...")
        image_urls = self.extract_images(html_content, validated_url)
        if not image_urls:
            print("⚠️  No images found to download")
        print()

        print("ℹ️  Phases 3-5: Implementation pending...")


def main():
    parser = argparse.ArgumentParser(
        description='Spider - Download images from websites',
        usage='./spider [-rlp] URL'
    )

    parser.add_argument('URL', help='Website URL to scrape')
    parser.add_argument('-r', action='store_true',
                        help='recursively download images')
    parser.add_argument('-l', type=int, default=Spider.DEFAULT_DEPTH,
                        help=f'maximum depth level (default: {Spider.DEFAULT_DEPTH})')
    parser.add_argument('-p', type=str, default=Spider.DEFAULT_PATH,
                        help=f'path to save files (default: {Spider.DEFAULT_PATH})')

    args = parser.parse_args()

    # Validate arguments
    if not args.URL:
        parser.print_help()
        sys.exit(1)

    # Alert if -l is used without -r
    if '-l' in sys.argv and not args.r:
        print("⚠️  Warning: -l (depth level) only applies when using -r (recursive mode)")
        print("   The depth limit will be ignored since recursive mode is not enabled.")
        print()

    # Create Spider instance and run
    spider = Spider(
        url=args.URL,
        recursive=args.r,
        depth=args.l,
        path=args.p
    )

    spider.run()


if __name__ == '__main__':
    main()
