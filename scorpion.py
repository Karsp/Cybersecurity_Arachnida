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


class Scorpion:
    """Image metadata extractor and analyzer"""

    VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}

    def __init__(self):
        """Initialize Scorpion metadata extractor"""
        self.files = []
        self.metadata_results = {}

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
            print("-" * 70)
            
            parser = MetadataParser(file_path)
            metadata = parser.extract_all()
            self.metadata_results[str(file_path)] = metadata
            
            # Display extracted metadata
            self._display_metadata(metadata)
            print()

    def _display_metadata(self, metadata: Dict[str, Any]):
        """
        Display metadata in organized format.

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
        usage='./scorpion FILE1 [FILE2 ...]'
    )

    parser.add_argument('files', nargs='+', 
                        help='Image files to analyze')

    args = parser.parse_args()

    # Validate input
    if not args.files:
        parser.print_help()
        sys.exit(1)

    # Create Scorpion instance and run
    scorpion = Scorpion()
    if scorpion.load_files(args.files):
        scorpion.run()
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()