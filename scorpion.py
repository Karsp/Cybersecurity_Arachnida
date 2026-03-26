#!/usr/bin/env python3
"""
Scorpion - Image metadata extractor
Extracts and displays EXIF and metadata from image files
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from metadata_parser import MetadataParser
from output_formatter import OutputFormatter, MetadataSummary


class Scorpion:
    """Image metadata extractor and analyzer"""

    VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}

    def __init__(self, output_format: str = 'console', output_file: Optional[str] = None):
        """Initialize Scorpion metadata extractor"""
        self.files = []
        self.metadata_results = []
        self.output_format = output_format
        self.output_file = output_file

    def validate_file(self, file_path: str) -> Optional[Path]:
        """
        Validate that file exists and has valid image extension.

        Args:
            file_path (str): Path to image file

        Returns:
            Path: Path object if valid, None otherwise
        """
        try:
            path = Path(file_path)

            # Check if file exists
            if not path.exists():
                print(f"❌ Error: File not found - {file_path}")
                return None

            # Check if it's a file (not directory)
            if not path.is_file():
                print(f"❌ Error: Not a file - {file_path}")
                return None

            # Check file extension
            if path.suffix.lower() not in self.VALID_EXTENSIONS:
                print(f"❌ Error: Invalid file extension '{path.suffix}' - {file_path}")
                print(f"   Supported: {', '.join(self.VALID_EXTENSIONS)}")
                return None

            return path

        except Exception as e:
            print(f"❌ Error validating file: {e}")
            return None

    def load_files(self, file_paths: list) -> bool:
        """
        Validate and load all image files.

        Args:
            file_paths (list): List of file paths to process

        Returns:
            bool: True if at least one valid file loaded
        """
        print("📋 Step 1: Validating files...")
        valid_count = 0

        for file_path in file_paths:
            validated_path = self.validate_file(file_path)
            if validated_path:
                self.files.append(validated_path)
                valid_count += 1
                print(f"   ✅ Valid: {file_path}")

        print()

        if valid_count == 0:
            print("❌ No valid image files to process")
            return False

        print(f"✅ Loaded {valid_count} valid file(s)")
        print()
        return True

    def run(self):
        """Main execution - Extract and display metadata for all files"""
        print("🦂 Scorpion metadata extractor")
        print(f"   Files to process: {len(self.files)}")
        print()

        for idx, file_path in enumerate(self.files, 1):
            print(f"📷 Processing [{idx}/{len(self.files)}]: {file_path.name}")
            
            parser = MetadataParser(file_path)
            metadata = parser.extract_all()
            self.metadata_results.append({
                'file_path': str(file_path),
                'metadata': metadata
            })
            print(f"   ✅ Metadata extracted")

        print()

        # Format and display output
        self._display_results()

    def _display_results(self):
        """Display results based on selected output format"""
        try:
            formatter = OutputFormatter(self.output_format, self.output_file)

            for result in self.metadata_results:
                formatter.add_result(result['file_path'], result['metadata'])

            # For console format, display results directly
            if self.output_format == 'console':
                formatter.display()
                MetadataSummary.print_summary(self.metadata_results)
            else:
                # For other formats, save to file
                if self.output_file:
                    formatter.save(self.output_file)
                    print(f"\n✅ Results exported successfully")
                else:
                    print("\n⚠️  No output file specified for non-console format")

        except Exception as e:
            print(f"❌ Error formatting output: {e}")

    def _display_metadata(self, metadata: Dict[str, Any]):
        """
        Display metadata in organized format (DEPRECATED - use OutputFormatter instead).

        Args:
            metadata (Dict): Metadata dictionary from parser
        """
        # Basic Metadata
        if metadata['basic']:
            print("\n📊 BASIC INFORMATION:")
            for key, value in metadata['basic'].items():
                print(f"   {key:.<25} {value}")

        # EXIF Data
        if metadata['exif']:
            print("\n📸 EXIF DATA:")
            for ifd_name, ifd_data in metadata['exif'].items():
                if ifd_data:
                    print(f"\n   [{ifd_name}]")
                    for tag_name, value in ifd_data.items():
                        # Truncate long values
                        value_str = str(value)[:60]
                        print(f"      {tag_name:.<30} {value_str}")

        # IPTC Data
        if metadata['iptc']:
            print("\n📝 IPTC DATA:")
            for key, value in metadata['iptc'].items():
                value_str = str(value)[:60]
                print(f"   {key:.<30} {value_str}")

        # Other Metadata
        if metadata['other']:
            print("\n🔖 OTHER METADATA:")
            for key, value in metadata['other'].items():
                value_str = str(value)[:60]
                print(f"   {key:.<30} {value_str}")


def main():
    parser = argparse.ArgumentParser(
        description='Scorpion - Extract image metadata',
        usage='./scorpion [-f FORMAT] [-o FILE] FILE1 [FILE2 ...]'
    )

    parser.add_argument('files', nargs='+', 
                        help='Image files to analyze')
    
    parser.add_argument('-f', '--format', 
                        choices=['console', 'json', 'csv'],
                        default='console',
                        help='Output format (default: console)')
    
    parser.add_argument('-o', '--output',
                        help='Output file path (required for json/csv formats)')

    args = parser.parse_args()

    # Validate input
    if not args.files:
        parser.print_help()
        sys.exit(1)

    # Validate output requirements
    if args.format != 'console' and not args.output:
        print("❌ Error: Output file (-o) is required for json/csv formats")
        sys.exit(1)

    # Create Scorpion instance and run
    scorpion = Scorpion(output_format=args.format, output_file=args.output)
    if scorpion.load_files(args.files):
        scorpion.run()
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()