#!/usr/bin/env python3
"""
Example usage of the Ableton VST Auditor programmatically.
This shows how to use the AbletonVSTAuditor class in your own scripts.
"""

import os
from ableton_vst_audit import AbletonVSTAuditor
from collections import defaultdict

def example_basic_scan():
    """Basic example: scan a directory and print results."""
    print("=== Basic VST Scan Example ===")
    
    # Create auditor instance
    auditor = AbletonVSTAuditor()
    
    # Set up progress callback (optional)
    auditor.progress_callback = lambda msg: print(f"Progress: {msg}")
    
    # Scan directory (replace with your path)
    project_directory = "ALS"  # Example directory
    
    if not os.path.exists(project_directory):
        print(f"Directory '{project_directory}' not found!")
        return
    
    print(f"Scanning: {project_directory}")
    auditor.scan_directory(project_directory)
    
    # Print results
    print(f"\nResults:")
    print(f"- Projects scanned: {len(auditor.project_vsts)}")
    print(f"- Unique VSTs found: {len(auditor.vst_usage)}")
    
    print(f"\nTop 5 VSTs:")
    for i, (vst, count) in enumerate(auditor.vst_usage.most_common(5), 1):
        manufacturer = auditor.vst_manufacturers.get(vst, "Unknown")
        print(f"  {i}. {vst} ({count}x) [{manufacturer}]")

def example_manufacturer_analysis():
    """Example: analyze VST usage by manufacturer."""
    print("\n=== Manufacturer Analysis Example ===")
    
    auditor = AbletonVSTAuditor()
    auditor.scan_directory("ALS")  # Replace with your path
    
    if not auditor.vst_usage:
        print("No VSTs found!")
        return
    
    # Group by manufacturer
    by_manufacturer = defaultdict(list)
    for vst, count in auditor.vst_usage.items():
        manufacturer = auditor.vst_manufacturers.get(vst, "Unknown")
        by_manufacturer[manufacturer].append((vst, count))
    
    # Print manufacturer summary
    print("VSTs by Manufacturer:")
    for manufacturer in sorted(by_manufacturer.keys()):
        vst_list = by_manufacturer[manufacturer]
        total_usage = sum(count for _, count in vst_list)
        print(f"\n{manufacturer} ({len(vst_list)} plugins, {total_usage} total uses):")
        
        for vst, count in sorted(vst_list, key=lambda x: -x[1]):  # Sort by usage
            print(f"  • {vst} ({count}x)")

def example_project_analysis():
    """Example: analyze individual projects."""
    print("\n=== Project Analysis Example ===")
    
    auditor = AbletonVSTAuditor()
    auditor.scan_directory("ALS")  # Replace with your path
    
    if not auditor.project_vsts:
        print("No projects found!")
        return
    
    print("Project VST Usage:")
    for project_path, vsts in auditor.project_vsts.items():
        project_name = os.path.basename(project_path)
        unique_vsts = set(vsts)
        
        print(f"\n{project_name}:")
        print(f"  Total VST instances: {len(vsts)}")
        print(f"  Unique VSTs: {len(unique_vsts)}")
        
        # Show manufacturers used in this project
        manufacturers = set()
        for vst in unique_vsts:
            manufacturer = auditor.vst_manufacturers.get(vst, "Unknown")
            manufacturers.add(manufacturer)
        
        print(f"  Manufacturers: {', '.join(sorted(manufacturers))}")

def example_custom_report():
    """Example: generate a custom report format."""
    print("\n=== Custom Report Example ===")
    
    auditor = AbletonVSTAuditor()
    auditor.scan_directory("ALS")  # Replace with your path
    
    if not auditor.vst_usage:
        print("No VSTs found!")
        return
    
    # Create custom report
    report_lines = []
    report_lines.append("CUSTOM VST ANALYSIS REPORT")
    report_lines.append("=" * 40)
    
    # Summary stats
    total_vst_instances = sum(auditor.vst_usage.values())
    report_lines.append(f"Total VST instances across all projects: {total_vst_instances}")
    report_lines.append(f"Unique VST plugins: {len(auditor.vst_usage)}")
    report_lines.append(f"Projects analyzed: {len(auditor.project_vsts)}")
    
    # Most used VST
    if auditor.vst_usage:
        most_used = auditor.vst_usage.most_common(1)[0]
        manufacturer = auditor.vst_manufacturers.get(most_used[0], "Unknown")
        report_lines.append(f"Most used VST: {most_used[0]} ({most_used[1]}x) by {manufacturer}")
    
    # Manufacturer diversity
    manufacturers = set(auditor.vst_manufacturers.values())
    report_lines.append(f"Manufacturers represented: {len(manufacturers)}")
    
    # Print custom report
    for line in report_lines:
        print(line)

def main():
    """Run all examples."""
    print("Ableton VST Auditor - Usage Examples")
    print("=" * 50)
    
    # Check if example directory exists
    if not os.path.exists("ALS"):
        print("Note: These examples use 'ALS' directory.")
        print("Replace 'ALS' with your actual Ableton projects path.")
        print()
    
    try:
        example_basic_scan()
        example_manufacturer_analysis()
        example_project_analysis()
        example_custom_report()
        
        print("\n" + "=" * 50)
        print("Examples completed successfully!")
        print("\nTo use in your own scripts:")
        print("1. Import: from ableton_vst_audit import AbletonVSTAuditor")
        print("2. Create instance: auditor = AbletonVSTAuditor()")
        print("3. Scan: auditor.scan_directory('/path/to/projects')")
        print("4. Access results: auditor.vst_usage, auditor.vst_manufacturers")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        print("Make sure ableton_vst_audit.py is in the same directory.")

if __name__ == "__main__":
    main()