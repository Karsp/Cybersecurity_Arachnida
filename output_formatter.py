#!/usr/bin/env python3
"""
Output Formatter - Format and display metadata in various formats
Supports console display, JSON export, and CSV export
"""

import json
import csv
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


class OutputFormatter:
    """Format and display metadata in various output formats"""

    def __init__(self, output_format: str = 'console', output_file: Optional[str] = None):
        """
        Initialize output formatter.

        Args:
            output_format (str): Output format ('console', 'json', 'csv')
            output_file (str): Optional output file path
        """
        self.format = output_format.lower()
        self.output_file = output_file
        self.results = []

        if self.format not in ['console', 'json', 'csv']:
            raise ValueError(f"Invalid format: {self.format}. Choose from: console, json, csv")

    def add_result(self, file_path: str, metadata: Dict[str, Any]):
        """
        Add metadata result for formatting.

        Args:
            file_path (str): Path to the image file
            metadata (Dict): Metadata dictionary from MetadataParser
        """
        self.results.append({
            'file_path': file_path,
            'metadata': metadata
        })

    def format_output(self) -> str:
        """
        Format all results according to selected format.

        Returns:
            str: Formatted output
        """
        if self.format == 'console':
            return self._format_console()
        elif self.format == 'json':
            return self._format_json()
        elif self.format == 'csv':
            return self._format_csv()

    def _format_console(self) -> str:
        """
        Format metadata for console display with visual organization.

        Returns:
            str: Formatted console output
        """
        output = []

        for result in self.results:
            file_path = result['file_path']
            metadata = result['metadata']

            output.append(f"📷 File: {file_path}")
            output.append("=" * 80)

            # Basic Information
            if metadata.get('basic'):
                output.append("\n📊 BASIC INFORMATION:")
                output.append("-" * 80)
                for key, value in metadata['basic'].items():
                    output.append(f"   {key:.<35} {value}")

            # EXIF Data
            if metadata.get('exif') and any(metadata['exif'].values()):
                output.append("\n📸 EXIF DATA:")
                output.append("-" * 80)
                for ifd_name, ifd_data in metadata['exif'].items():
                    if ifd_data:
                        output.append(f"\n   [{ifd_name}]")
                        for tag_name, value in ifd_data.items():
                            # Truncate long values
                            value_str = str(value)[:70]
                            output.append(f"      {tag_name:.<30} {value_str}")

            # IPTC Data
            if metadata.get('iptc') and metadata['iptc']:
                output.append("\n📝 IPTC DATA:")
                output.append("-" * 80)
                for key, value in metadata['iptc'].items():
                    value_str = str(value)[:70]
                    output.append(f"   {key:.<35} {value_str}")

            # Other Metadata
            if metadata.get('other') and metadata['other']:
                output.append("\n🔖 OTHER METADATA:")
                output.append("-" * 80)
                for key, value in metadata['other'].items():
                    value_str = str(value)[:70]
                    output.append(f"   {key:.<35} {value_str}")

            output.append("\n")

        return "\n".join(output)

    def _format_json(self) -> str:
        """
        Format metadata for JSON export.

        Returns:
            str: JSON formatted output
        """
        json_data = []

        for result in self.results:
            json_data.append({
                'file_path': result['file_path'],
                'metadata': result['metadata'],
                'extracted_at': datetime.now().isoformat()
            })

        return json.dumps(json_data, indent=2, default=str)

    def _format_csv(self) -> str:
        """
        Format metadata for CSV export (flattened structure).

        Returns:
            str: CSV formatted output
        """
        output = []
        fieldnames = set()
        rows = []

        # First pass: collect all unique field names
        for result in self.results:
            file_path = result['file_path']
            metadata = result['metadata']
            row = {'file_path': file_path}

            # Flatten metadata
            flattened = self._flatten_metadata(metadata)
            row.update(flattened)
            rows.append(row)
            fieldnames.update(row.keys())

        # Sort fieldnames for consistent output
        sorted_fieldnames = sorted(list(fieldnames))

        # Write CSV
        import io
        csv_buffer = io.StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=sorted_fieldnames)
        writer.writeheader()
        writer.writerows(rows)

        return csv_buffer.getvalue()

    def _flatten_metadata(self, metadata: Dict[str, Any], parent_key: str = '') -> Dict[str, Any]:
        """
        Flatten nested metadata dictionary for CSV export.

        Args:
            metadata (Dict): Metadata dictionary
            parent_key (str): Parent key for nested items

        Returns:
            Dict: Flattened metadata
        """
        items = []

        for k, v in metadata.items():
            if k == 'basic':
                # Basic info is already flat
                for key, value in v.items():
                    items.append((f"basic_{key}", str(value)))

            elif k == 'exif':
                # EXIF has nested structure by IFD
                for ifd_name, ifd_data in v.items():
                    for tag_name, value in ifd_data.items():
                        items.append((f"exif_{ifd_name}_{tag_name}", str(value)[:100]))

            elif k == 'iptc':
                # IPTC data
                for key, value in v.items():
                    items.append((f"iptc_{key}", str(value)[:100]))

            elif k == 'other':
                # Other metadata
                for key, value in v.items():
                    items.append((f"other_{key}", str(value)[:100]))

        return dict(items)

    def display(self):
        """Display formatted output to console"""
        output = self.format_output()
        print(output)

    def save(self, file_path: Optional[str] = None):
        """
        Save formatted output to file.

        Args:
            file_path (str): Path to save file. Uses self.output_file if not provided
        """
        target_path = file_path or self.output_file

        if not target_path:
            print("❌ Error: No output file specified")
            return False

        try:
            output = self.format_output()
            Path(target_path).write_text(output)
            print(f"✅ Output saved to: {target_path}")
            return True

        except Exception as e:
            print(f"❌ Error saving output: {e}")
            return False


class MetadataSummary:
    """Generate summary statistics and reports"""

    @staticmethod
    def generate_summary(results: List[Dict[str, Any]]) -> str:
        """
        Generate a summary report of all analyzed files.

        Args:
            results (List): List of result dictionaries

        Returns:
            str: Summary report
        """
        output = []
        output.append("\n🔍 METADATA EXTRACTION SUMMARY")
        output.append("=" * 80)

        total_files = len(results)
        output.append(f"\n📊 Total files processed: {total_files}")

        # Count files with different metadata types
        files_with_exif = sum(1 for r in results if r['metadata'].get('exif'))
        files_with_iptc = sum(1 for r in results if r['metadata'].get('iptc'))
        files_with_other = sum(1 for r in results if r['metadata'].get('other'))

        output.append(f"   Files with EXIF data: {files_with_exif}/{total_files}")
        output.append(f"   Files with IPTC data: {files_with_iptc}/{total_files}")
        output.append(f"   Files with other metadata: {files_with_other}/{total_files}")

        # File format breakdown
        formats = {}
        for result in results:
            fmt = result['metadata']['basic'].get('Format', 'Unknown')
            formats[fmt] = formats.get(fmt, 0) + 1

        output.append("\n📁 File formats:")
        for fmt, count in sorted(formats.items()):
            output.append(f"   {fmt}: {count}")

        # File size statistics
        sizes = []
        for result in results:
            size_str = result['metadata']['basic'].get('File Size', '0 B')
            try:
                size_val = float(size_str.split()[0])
                sizes.append(size_val)
            except (ValueError, IndexError):
                pass

        if sizes:
            output.append(f"\n💾 File size statistics:")
            output.append(f"   Total size: {sum(sizes):.2f} KB")
            output.append(f"   Average size: {sum(sizes)/len(sizes):.2f} KB")
            output.append(f"   Min size: {min(sizes):.2f} KB")
            output.append(f"   Max size: {max(sizes):.2f} KB")

        output.append("\n" + "=" * 80)

        return "\n".join(output)

    @staticmethod
    def print_summary(results: List[Dict[str, Any]]):
        """
        Print summary report to console.

        Args:
            results (List): List of result dictionaries
        """
        print(MetadataSummary.generate_summary(results))
