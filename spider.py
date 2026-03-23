#!/usr/bin/env python3
"""
Spider - Web image scraper
Recursively downloads images from a website
"""

import argparse
import sys
import os
from pathlib import Path


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

    def run(self):
        """Main execution"""
        print(f"Starting spider on: {self.url}")
        print(f"Recursive: {self.recursive}, Depth: {self.depth}, Path: {self.path}")
        # Implementation will go here
        pass


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
