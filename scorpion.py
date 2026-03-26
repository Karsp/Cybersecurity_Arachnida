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
from metadata_modifier import MetadataModifier
from metadata_filter import MetadataFilter, MetadataAnalyzer


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
        description='Scorpion - Extract and modify image metadata',
        usage='./scorpion [-f FORMAT] [-o FILE] FILE1 [FILE2 ...]\n       ./scorpion --modify [OPTIONS] FILE1 [FILE2 ...]'
    )

    parser.add_argument('files', nargs='+', 
                        help='Image files to analyze or modify')
    
    parser.add_argument('-f', '--format', 
                        choices=['console', 'json', 'csv'],
                        default='console',
                        help='Output format (default: console)')
    
    parser.add_argument('-o', '--output',
                        help='Output file path (required for json/csv formats)')

    # Modification options
    parser.add_argument('--modify', action='store_true',
                        help='Enable modification mode')
    
    parser.add_argument('--strip-exif', action='store_true',
                        help='Remove all EXIF data from JPEG images')
    
    parser.add_argument('--strip-all', action='store_true',
                        help='Remove all metadata from images')
    
    parser.add_argument('--remove-tags', nargs='+', metavar='TAG',
                        help='Remove specific EXIF tags (space-separated)')
    
    parser.add_argument('--add-comment', metavar='TEXT',
                        help='Add a comment to the image')
    
    parser.add_argument('--backup', action='store_true', default=True,
                        help='Create backup before modification (default: True)')
    
    parser.add_argument('--no-backup', action='store_false', dest='backup',
                        help='Do not create backup')
    
    parser.add_argument('--restore', action='store_true',
                        help='Restore image from backup')

    # Analysis and filter options
    parser.add_argument('--analyze', action='store_true',
                        help='Analyze and generate report for all files')
    
    parser.add_argument('--filter-format', metavar='FORMAT',
                        help='Filter by image format (JPEG, PNG, GIF, BMP)')
    
    parser.add_argument('--filter-size', nargs=2, type=float, metavar=('MIN_KB', 'MAX_KB'),
                        help='Filter by file size range in KB')
    
    parser.add_argument('--filter-exif', action='store_true',
                        help='Filter only images with EXIF data')

    args = parser.parse_args()

    # Validate input
    if not args.files:
        parser.print_help()
        sys.exit(1)

    # Modification mode
    if args.modify:
        modify_metadata(args)
    # Analysis mode
    elif args.analyze or args.filter_format or args.filter_size or args.filter_exif:
        analyze_metadata(args)
    else:
        # Extract mode
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


def modify_metadata(args):
    """
    Handle metadata modification operations.

    Args:
        args: Parsed command-line arguments
    """
    print("🔧 Scorpion metadata modifier")
    print(f"   Files to modify: {len(args.files)}")
    print()

    valid_files = []
    for file_path in args.files:
        path = Path(file_path)
        if not path.exists():
            print(f"❌ File not found: {file_path}")
        elif not path.is_file():
            print(f"❌ Not a file: {file_path}")
        else:
            valid_files.append(path)

    if not valid_files:
        print("❌ No valid files to modify")
        sys.exit(1)

    print(f"✅ Processing {len(valid_files)} file(s)")
    print()

    # Process each file
    for idx, file_path in enumerate(valid_files, 1):
        print(f"📝 Modifying [{idx}/{len(valid_files)}]: {file_path.name}")
        print("-" * 70)

        modifier = MetadataModifier(file_path, create_backup=args.backup)

        # Perform requested modifications
        operations_count = 0

        if args.strip_exif:
            print("   → Removing EXIF data...")
            if modifier.remove_exif():
                print("   ✅ EXIF data removed")
                operations_count += 1
            else:
                print("   ⚠️  Failed to remove EXIF")

        if args.strip_all:
            print("   → Stripping all metadata...")
            if modifier.strip_all_metadata():
                print("   ✅ All metadata removed")
                operations_count += 1
            else:
                print("   ⚠️  Failed to strip metadata")

        if args.remove_tags:
            print(f"   → Removing tags: {', '.join(args.remove_tags)}")
            if modifier.remove_specific_exif_tags(args.remove_tags):
                operations_count += 1
            else:
                print("   ⚠️  Failed to remove tags")

        if args.add_comment:
            print(f"   → Adding comment: {args.add_comment[:50]}...")
            if modifier.add_comment(args.add_comment):
                print("   ✅ Comment added")
                operations_count += 1
            else:
                print("   ⚠️  Failed to add comment")

        if args.restore:
            print("   → Restoring from backup...")
            if modifier.restore_backup():
                print("   ✅ Image restored")
                operations_count += 1
            else:
                print("   ⚠️  Failed to restore backup")

        if operations_count == 0:
            print("   ⚠️  No modifications performed")

        status = modifier.get_modification_status()
        if status['backup_path']:
            print(f"   📦 Backup: {Path(status['backup_path']).name}")

        print()

    print("✅ Modification complete")


def analyze_metadata(args):
    """
    Handle metadata analysis and filtering operations.

    Args:
        args: Parsed command-line arguments
    """
    print("📊 Scorpion metadata analyzer")
    print(f"   Files to analyze: {len(args.files)}")
    print()

    # Load metadata from all files
    metadata_list = []
    for file_path in args.files:
        path = Path(file_path)
        if not path.exists():
            print(f"❌ File not found: {file_path}")
            continue
        if not path.is_file():
            print(f"❌ Not a file: {file_path}")
            continue

        try:
            parser = MetadataParser(path)
            metadata = parser.extract_all()
            metadata_list.append({
                'file_path': str(path),
                'metadata': metadata
            })
        except Exception as e:
            print(f"⚠️  Error reading {file_path}: {e}")

    if not metadata_list:
        print("❌ No valid files to analyze")
        sys.exit(1)

    print(f"✅ Loaded metadata from {len(metadata_list)} file(s)")
    print()

    # Apply filters
    filter_obj = MetadataFilter(metadata_list)

    if args.filter_format:
        filter_obj.filter_by_format(args.filter_format)
        print(f"Filter: Format = {args.filter_format} → {filter_obj.get_count()} results")

    if args.filter_size:
        min_kb, max_kb = args.filter_size
        filter_obj.filter_by_size_range(min_kb, max_kb)
        print(f"Filter: Size {min_kb}-{max_kb} KB → {filter_obj.get_count()} results")

    if args.filter_exif:
        filter_obj.filter_has_exif()
        print(f"Filter: Has EXIF → {filter_obj.get_count()} results")

    filtered_results = filter_obj.get_results()
    print()

    # Generate report
    if args.analyze or not (args.filter_format or args.filter_size or args.filter_exif):
        print(MetadataAnalyzer.generate_report(filtered_results))
    else:
        # Show filtered results
        print("📋 FILTERED RESULTS")
        print("=" * 80)
        for item in filtered_results:
            basic = item.get('metadata', {}).get('basic', {})
            print(f"  {item['file_path']}")
            print(f"    Format: {basic.get('Format', 'N/A')}")
            print(f"    Size: {basic.get('File Size', 'N/A')}")
            print(f"    Dimensions: {basic.get('Dimensions', 'N/A')}")
        print("=" * 80)

        # Show statistics
        stats = filter_obj.get_statistics()
        print(f"\n📊 Statistics for {stats.get('total_count', 0)} files:")
        if 'size_stats' in stats:
            size_stats = stats['size_stats']
            print(f"  Total size: {size_stats['total_kb']:.2f} KB")
            print(f"  Average size: {size_stats['average_kb']:.2f} KB")


if __name__ == '__main__':
    main()