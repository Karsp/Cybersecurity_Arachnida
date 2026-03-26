#!/usr/bin/env python3
"""
Metadata Filter & Search - Advanced filtering and searching capabilities
Search, filter, and analyze metadata across multiple images
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from metadata_parser import MetadataParser
import json
from datetime import datetime


class MetadataFilter:
    """Advanced filtering and search for metadata"""

    def __init__(self, metadata_list: List[Dict[str, Any]]):
        """
        Initialize filter with metadata list.

        Args:
            metadata_list (List[Dict]): List of metadata dictionaries
        """
        self.metadata_list = metadata_list
        self.results = metadata_list.copy()

    def filter_by_format(self, format_name: str) -> 'MetadataFilter':
        """
        Filter images by file format.

        Args:
            format_name (str): Format name (JPEG, PNG, GIF, BMP)

        Returns:
            MetadataFilter: Filtered self for chaining
        """
        self.results = [
            item for item in self.results
            if item.get('metadata', {}).get('basic', {}).get('Format', '').upper() == format_name.upper()
        ]
        return self

    def filter_by_size_range(self, min_kb: float, max_kb: float) -> 'MetadataFilter':
        """
        Filter images by file size range.

        Args:
            min_kb (float): Minimum size in KB
            max_kb (float): Maximum size in KB

        Returns:
            MetadataFilter: Filtered self for chaining
        """
        def extract_size(item):
            size_str = item.get('metadata', {}).get('basic', {}).get('File Size', '0 B')
            try:
                size_val = float(size_str.split()[0])
                return min_kb <= size_val <= max_kb
            except (ValueError, IndexError):
                return False

        self.results = [item for item in self.results if extract_size(item)]
        return self

    def filter_by_dimensions(self, min_width: int, min_height: int) -> 'MetadataFilter':
        """
        Filter images by minimum dimensions.

        Args:
            min_width (int): Minimum width in pixels
            min_height (int): Minimum height in pixels

        Returns:
            MetadataFilter: Filtered self for chaining
        """
        def check_dimensions(item):
            dims = item.get('metadata', {}).get('basic', {}).get('Dimensions', '')
            try:
                width, height = map(int, dims.replace('pixels', '').split('x'))
                return width >= min_width and height >= min_height
            except (ValueError, AttributeError):
                return False

        self.results = [item for item in self.results if check_dimensions(item)]
        return self

    def filter_by_color_mode(self, color_mode: str) -> 'MetadataFilter':
        """
        Filter images by color mode.

        Args:
            color_mode (str): Color mode (RGB, RGBA, L, P, etc.)

        Returns:
            MetadataFilter: Filtered self for chaining
        """
        self.results = [
            item for item in self.results
            if item.get('metadata', {}).get('basic', {}).get('Color Mode', '') == color_mode.upper()
        ]
        return self

    def filter_has_exif(self) -> 'MetadataFilter':
        """
        Filter images that have EXIF data.

        Returns:
            MetadataFilter: Filtered self for chaining
        """
        self.results = [
            item for item in self.results
            if any(item.get('metadata', {}).get('exif', {}).values())
        ]
        return self

    def filter_no_exif(self) -> 'MetadataFilter':
        """
        Filter images without EXIF data.

        Returns:
            MetadataFilter: Filtered self for chaining
        """
        self.results = [
            item for item in self.results
            if not any(item.get('metadata', {}).get('exif', {}).values())
        ]
        return self

    def filter_has_iptc(self) -> 'MetadataFilter':
        """
        Filter images that have IPTC data.

        Returns:
            MetadataFilter: Filtered self for chaining
        """
        self.results = [
            item for item in self.results
            if bool(item.get('metadata', {}).get('iptc', {}))
        ]
        return self

    def search_text(self, query: str, case_sensitive: bool = False) -> 'MetadataFilter':
        """
        Search for text in all metadata.

        Args:
            query (str): Text to search for
            case_sensitive (bool): Whether search is case-sensitive

        Returns:
            MetadataFilter: Filtered self for chaining
        """
        search_query = query if case_sensitive else query.lower()

        def contains_query(item):
            metadata_str = json.dumps(item, default=str)
            search_str = metadata_str if case_sensitive else metadata_str.lower()
            return search_query in search_str

        self.results = [item for item in self.results if contains_query(item)]
        return self

    def filter_by_exif_tag(self, tag_name: str, value: Optional[str] = None) -> 'MetadataFilter':
        """
        Filter by EXIF tag presence or specific value.

        Args:
            tag_name (str): EXIF tag name
            value (str, optional): Specific value to match

        Returns:
            MetadataFilter: Filtered self for chaining
        """
        def has_tag(item):
            exif_data = item.get('metadata', {}).get('exif', {})
            for ifd_data in exif_data.values():
                if tag_name in ifd_data:
                    if value is None:
                        return True
                    if str(ifd_data[tag_name]) == str(value):
                        return True
            return False

        self.results = [item for item in self.results if has_tag(item)]
        return self

    def get_results(self) -> List[Dict[str, Any]]:
        """
        Get filtered results.

        Returns:
            List[Dict]: Filtered metadata list
        """
        return self.results

    def get_count(self) -> int:
        """
        Get number of results.

        Returns:
            int: Number of filtered items
        """
        return len(self.results)

    def sort_by_size(self, ascending: bool = True) -> 'MetadataFilter':
        """
        Sort results by file size.

        Args:
            ascending (bool): Sort ascending if True, descending if False

        Returns:
            MetadataFilter: Sorted self for chaining
        """
        def extract_size(item):
            size_str = item.get('metadata', {}).get('basic', {}).get('File Size', '0 B')
            try:
                return float(size_str.split()[0])
            except (ValueError, IndexError):
                return 0

        self.results.sort(key=extract_size, reverse=not ascending)
        return self

    def sort_by_name(self, ascending: bool = True) -> 'MetadataFilter':
        """
        Sort results by filename.

        Args:
            ascending (bool): Sort ascending if True, descending if False

        Returns:
            MetadataFilter: Sorted self for chaining
        """
        def get_name(item):
            return item.get('file_path', '')

        self.results.sort(key=get_name, reverse=not ascending)
        return self

    def sort_by_dimensions(self, ascending: bool = True) -> 'MetadataFilter':
        """
        Sort results by image dimensions.

        Args:
            ascending (bool): Sort ascending if True, descending if False

        Returns:
            MetadataFilter: Sorted self for chaining
        """
        def get_area(item):
            dims = item.get('metadata', {}).get('basic', {}).get('Dimensions', '0x0')
            try:
                width, height = map(int, dims.replace('pixels', '').split('x'))
                return width * height
            except (ValueError, AttributeError):
                return 0

        self.results.sort(key=get_area, reverse=not ascending)
        return self

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about filtered results.

        Returns:
            Dict: Statistics dictionary
        """
        if not self.results:
            return {}

        # File counts
        formats = {}
        color_modes = {}
        exif_count = 0
        iptc_count = 0

        sizes = []
        widths = []
        heights = []

        for item in self.results:
            metadata = item.get('metadata', {})

            # Format count
            fmt = metadata.get('basic', {}).get('Format', 'Unknown')
            formats[fmt] = formats.get(fmt, 0) + 1

            # Color mode count
            color = metadata.get('basic', {}).get('Color Mode', 'Unknown')
            color_modes[color] = color_modes.get(color, 0) + 1

            # EXIF/IPTC count
            if any(metadata.get('exif', {}).values()):
                exif_count += 1
            if metadata.get('iptc', {}):
                iptc_count += 1

            # Sizes and dimensions
            size_str = metadata.get('basic', {}).get('File Size', '0 B')
            try:
                sizes.append(float(size_str.split()[0]))
            except (ValueError, IndexError):
                pass

            dims = metadata.get('basic', {}).get('Dimensions', '0x0')
            try:
                w, h = map(int, dims.replace('pixels', '').split('x'))
                widths.append(w)
                heights.append(h)
            except (ValueError, AttributeError):
                pass

        stats = {
            'total_count': len(self.results),
            'formats': formats,
            'color_modes': color_modes,
            'with_exif': exif_count,
            'with_iptc': iptc_count,
        }

        if sizes:
            stats['size_stats'] = {
                'total_kb': sum(sizes),
                'average_kb': sum(sizes) / len(sizes),
                'min_kb': min(sizes),
                'max_kb': max(sizes),
            }

        if widths and heights:
            stats['dimension_stats'] = {
                'avg_width': sum(widths) / len(widths),
                'avg_height': sum(heights) / len(heights),
                'max_width': max(widths),
                'max_height': max(heights),
            }

        return stats

    def reset(self) -> 'MetadataFilter':
        """
        Reset filter to original list.

        Returns:
            MetadataFilter: Self for chaining
        """
        self.results = self.metadata_list.copy()
        return self


class MetadataAnalyzer:
    """Analyze metadata patterns and generate reports"""

    @staticmethod
    def generate_report(metadata_list: List[Dict[str, Any]]) -> str:
        """
        Generate comprehensive analysis report.

        Args:
            metadata_list (List[Dict]): List of metadata dictionaries

        Returns:
            str: Formatted report
        """
        report = []
        report.append("=" * 80)
        report.append("METADATA ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"\nTotal images analyzed: {len(metadata_list)}\n")

        # Format breakdown
        formats = {}
        for item in metadata_list:
            fmt = item.get('metadata', {}).get('basic', {}).get('Format', 'Unknown')
            formats[fmt] = formats.get(fmt, 0) + 1

        report.append("Format Distribution:")
        for fmt, count in sorted(formats.items()):
            percentage = (count / len(metadata_list)) * 100
            report.append(f"  {fmt:.<20} {count:>3} ({percentage:>5.1f}%)")

        # Color mode breakdown
        color_modes = {}
        for item in metadata_list:
            color = item.get('metadata', {}).get('basic', {}).get('Color Mode', 'Unknown')
            color_modes[color] = color_modes.get(color, 0) + 1

        report.append("\nColor Mode Distribution:")
        for color, count in sorted(color_modes.items()):
            percentage = (count / len(metadata_list)) * 100
            report.append(f"  {color:.<20} {count:>3} ({percentage:>5.1f}%)")

        # Metadata coverage
        exif_count = sum(1 for item in metadata_list if any(item.get('metadata', {}).get('exif', {}).values()))
        iptc_count = sum(1 for item in metadata_list if item.get('metadata', {}).get('iptc', {}))
        other_count = sum(1 for item in metadata_list if item.get('metadata', {}).get('other', {}))

        report.append("\nMetadata Coverage:")
        report.append(f"  With EXIF" + f".<15}} {exif_count}/{len(metadata_list)} ({(exif_count/len(metadata_list)*100):.1f}%)")
        report.append(f"  With IPTC" + f".<15}} {iptc_count}/{len(metadata_list)} ({(iptc_count/len(metadata_list)*100):.1f}%)")
        report.append(f"  With Other" + f".<14}} {other_count}/{len(metadata_list)} ({(other_count/len(metadata_list)*100):.1f}%)")

        # Size statistics
        sizes = []
        for item in metadata_list:
            size_str = item.get('metadata', {}).get('basic', {}).get('File Size', '0 B')
            try:
                sizes.append(float(size_str.split()[0]))
            except (ValueError, IndexError):
                pass

        if sizes:
            report.append("\nFile Size Statistics:")
            report.append("  Total" + f".<25}} {sum(sizes):.2f} KB")
            report.append("  Average" + f".<23}} {sum(sizes)/len(sizes):.2f} KB")
            report.append("  Minimum" + f".<23}} {min(sizes):.2f} KB")
            report.append("  Maximum" + f".<23}} {max(sizes):.2f} KB")

        report.append("\n" + "=" * 80)

        return "\n".join(report)
