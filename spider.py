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
import hashlib


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

    def setup_download_dir(self):
        """
        Create download directory if it doesn't exist.

        Returns:
            str: Path to download directory or None if failed
        """
        try:
            download_path = Path(self.path)
            download_path.mkdir(parents=True, exist_ok=True)
            return str(download_path)
        except Exception as e:
            print(f"❌ Error creating directory '{self.path}': {e}")
            return None

    def get_unique_filename(self, image_url, download_path):
        """
        Generate unique filename for image to avoid duplicates.

        Args:
            image_url (str): URL of the image
            download_path (str): Path to save directory

        Returns:
            str: Absolute path to save file or None if invalid
        """
        try:
            # Extract filename from URL
            parsed_url = urlparse(image_url)
            original_filename = Path(parsed_url.path).name

            if not original_filename:
                # Generate filename from URL hash if path is empty
                url_hash = hashlib.md5(image_url.encode()).hexdigest()[:8]
                original_filename = f"image_{url_hash}.jpg"

            # Check if file already exists
            file_path = Path(download_path) / original_filename
            if file_path.exists():
                # File already downloaded, skip
                return None

            return str(file_path)
        except Exception as e:
            print(f"   ❌ Error generating filename: {e}")
            return None

    def download_image(self, image_url, file_path):
        """
        Download image from URL and save to file.

        Args:
            image_url (str): URL of image to download
            file_path (str): Path where to save the image

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = self.session.get(image_url, timeout=10)

            if response.status_code != 200:
                print(f"   ⚠️  Failed to download: {image_url} (HTTP {response.status_code})")
                return False

            # Check content type is image
            content_type = response.headers.get('Content-Type', '').lower()
            if 'image' not in content_type:
                print(f"   ⚠️  Not an image (content-type: {content_type}): {image_url}")
                return False

            # Save binary data
            with open(file_path, 'wb') as f:
                f.write(response.content)

            file_size = len(response.content) / 1024  # KB
            print(f"   ✅ Downloaded: {Path(file_path).name} ({file_size:.1f} KB)")
            return True

        except requests.exceptions.Timeout:
            print(f"   ❌ Timeout downloading: {image_url}")
            return False
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error downloading {image_url}: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Error saving file: {e}")
            return False

    def is_same_domain(self, url1, url2):
        """
        Check if two URLs belong to the same domain.

        Args:
            url1 (str): First URL
            url2 (str): Second URL

        Returns:
            bool: True if same domain, False otherwise
        """
        try:
            domain1 = urlparse(url1).netloc.lower()
            domain2 = urlparse(url2).netloc.lower()

            # Handle www prefix variations
            domain1 = domain1.replace('www.', '')
            domain2 = domain2.replace('www.', '')

            return domain1 == domain2
        except Exception:
            return False

    def extract_links(self, html_content, base_url):
        """
        Parse HTML and extract all valid links for crawling.

        Args:
            html_content (str): HTML page content
            base_url (str): Base URL for resolving relative URLs

        Returns:
            list: List of absolute URLs found on the page
        """
        links = []

        try:
            soup = BeautifulSoup(html_content, 'lxml')

            # Find all <a> tags
            a_tags = soup.find_all('a', href=True)

            for a in a_tags:
                href = a.get('href')
                if not href:
                    continue

                # Resolve relative URLs to absolute
                absolute_url = self.resolve_url(href, base_url)
                if not absolute_url:
                    continue

                # Filter out fragments and anchors (url#section)
                parsed = urlparse(absolute_url)
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if parsed.query:
                    clean_url += f"?{parsed.query}"

                # Stay on same domain
                if not self.is_same_domain(absolute_url, base_url):
                    continue

                # Avoid duplicates
                if clean_url not in links:
                    links.append(clean_url)

            return links
        except Exception as e:
            print(f"   ❌ Error extracting links: {e}")
            return links

    def crawl_recursive(self, url, current_depth, download_path):
        """
        Recursively crawl website and download images.

        Args:
            url (str): URL to crawl
            current_depth (int): Current depth level
            download_path (str): Path to save downloads
        """
        # Depth limit check
        if current_depth > self.depth:
            return

        # Already visited check
        if url in self.visited_urls:
            return

        # Mark as visited
        self.visited_urls.add(url)

        print(f"📍 Crawling (depth {current_depth}/{self.depth}): {url}")

        # Fetch page
        html_content = self.fetch_page(url)
        if not html_content:
            return

        # Extract and download images
        image_urls = self.extract_images(html_content, url)
        for image_url in image_urls:
            if image_url in self.downloaded:
                continue

            file_path = self.get_unique_filename(image_url, download_path)
            if not file_path:
                continue

            if self.download_image(image_url, file_path):
                self.downloaded.add(image_url)

            time.sleep(0.5)

        print()

        # Recursive: Extract and crawl links if not at max depth
        if current_depth < self.depth:
            print(f"   Extracting links for next level...")
            links = self.extract_links(html_content, url)
            print(f"   Found {len(links)} links on this page")
            print()

            for link in links:
                if link not in self.visited_urls:
                    self.crawl_recursive(link, current_depth + 1, download_path)

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

        # Phase 3: Setup download directory
        print("📋 Phase 3: Setting up downloads...")
        download_path = self.setup_download_dir()
        if not download_path:
            print("❌ Spider failed: Could not create download directory")
            sys.exit(1)
        print(f"✅ Download directory ready: {download_path}")
        print()

        # Phase 4: Recursive or single-page crawling
        if self.recursive:
            print("📋 Phase 4: Starting recursive crawl...")
            print()
            self.crawl_recursive(validated_url, 1, download_path)
        else:
            print("📋 Phase 2: Fetching page...")
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
                return
            print()

            # Phase 3: Download images
            print(f"📋 Phase 3: Downloading {len(image_urls)} images...")
            downloaded_count = 0
            skipped_count = 0

            for i, image_url in enumerate(image_urls, 1):
                print(f"   [{i}/{len(image_urls)}] Processing: {image_url}")

                # Get unique filename (skip if already downloaded)
                file_path = self.get_unique_filename(image_url, download_path)
                if not file_path:
                    print(f"   ⏭️  Skipped (already downloaded)")
                    skipped_count += 1
                    continue

                # Download image
                if self.download_image(image_url, file_path):
                    self.downloaded.add(image_url)
                    downloaded_count += 1

                # Small delay to be respectful to server
                time.sleep(0.5)

            print()
            print("📊 Download Summary:")
            print(f"   ✅ Downloaded: {downloaded_count}")
            print(f"   ⏭️  Skipped: {skipped_count}")
            print(f"   📁 Saved to: {download_path}")
            print()

        # Final summary for recursive mode
        if self.recursive:
            print()
            print("📊 Recursive Crawl Summary:")
            print(f"   📍 Pages visited: {len(self.visited_urls)}")
            print(f"   ✅ Images downloaded: {len(self.downloaded)}")
            print(f"   📁 Saved to: {download_path}")
            print()


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
