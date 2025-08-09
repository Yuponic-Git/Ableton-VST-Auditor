# Ableton VST Auditor

A Python tool that scans Ableton Live project files (.als) to extract and analyze VST plugin usage across your entire project library. Get insights into which plugins you use most, discover which developers/manufacturers are represented in your work, and generate comprehensive reports.

## Features

- 🎛️ **Dual Interface**: Simple GUI or command-line operation
- 📁 **Batch Processing**: Recursively scans entire directory trees
- 🌐 **Network Drive Support**: Works with network-accessible project folders
- 🏢 **Manufacturer Detection**: Identifies plugin developers/manufacturers
- 📊 **Comprehensive Reports**: Usage statistics, manufacturer breakdowns, project analysis
- ⚡ **Real-time Progress**: Live updates during scanning
- 🔍 **Cross-platform**: Works on Windows, macOS, and Linux

## How It Works

Ableton Live project files (.als) are gzipped XML files containing all project information, including VST plugin references. This tool:

1. Recursively finds all .als files in your specified directory
2. Decompresses and parses the XML content
3. Extracts VST plugin names and paths
4. Identifies manufacturers from file paths and plugin names
5. Generates detailed usage reports

## Installation

### Prerequisites

- Python 3.6 or higher
- No additional packages required (uses only Python standard library)

### Download

1. Download `ableton_vst_audit.py` from this repository
2. Save it to a convenient location on your computer

## Usage

### GUI Mode (Recommended)

**Windows:**
```cmd
python ableton_vst_audit.py
```

**macOS/Linux:**
```bash
python3 ableton_vst_audit.py
```

This opens a user-friendly interface where you can:
1. Browse and select your Ableton projects folder
2. Click "Start Scan" to begin analysis
3. View real-time progress and results
4. Save detailed reports to your chosen location

### Command Line Mode

**Windows:**
```cmd
python ableton_vst_audit.py --cli "C:\Users\YourName\Ableton\Projects" --output report.txt
```

**macOS/Linux:**
```bash
python3 ableton_vst_audit.py --cli "/Users/YourName/Music/Ableton/Projects" --output report.txt
```

**Network Drive Example:**
```cmd
python ableton_vst_audit.py --cli "\\ServerName\SharedFolder\AbletonProjects" --output network_report.txt
```

## Sample Output

### Console Output
```
Scanning directory: /Users/YourName/Music/Ableton/Projects
Finding .als files...
Found 45 .als files. Starting scan...
Processing: My Song.als
Processing: Another Track.als
...
Scan complete! Found 127 unique VSTs

Generating report: vst_report.txt
Found 127 unique VSTs across 45 projects
```

### Report Contents

The generated report includes:

#### VST Usage Summary
```
VST USAGE SUMMARY (by frequency)
----------------------------------------
 15x  LABS (64 Bit).dll                  [Spitfire Audio]
 12x  TAL-Reverb-4-64.dll               [TAL-Software]  
  8x  Ozone Imager.dll                  [iZotope]
  7x  RC-20 Retro Color.dll             [XLN Audio]
```

#### VSTs by Manufacturer
```
VSTS BY MANUFACTURER
------------------------------

iZotope:
  • Ozone Imager.dll (8x)
  • Ozone EQ.dll (3x)

Spitfire Audio:
  • LABS (64 Bit).dll (15x)

TAL-Software:
  • TAL-Reverb-4-64.dll (12x)
  • TAL-Chorus-LX.dll (2x)
```

#### Project Breakdown
```
PROJECT BREAKDOWN
-------------------------

My Song.als:
  • LABS (64 Bit).dll                    [Spitfire Audio]
  • TAL-Reverb-4-64.dll                 [TAL-Software]
  • Ozone Imager.dll                    [iZotope]

Another Track.als:
  • RC-20 Retro Color.dll               [XLN Audio]
  • Decapitator.dll                     [Soundtoys]
```

## Supported Manufacturer Detection

The tool automatically identifies manufacturers for popular plugins including:

- **Spitfire Audio** (LABS series)
- **iZotope** (Ozone, Neutron, etc.)
- **Soundtoys** (Decapitator, EchoBoy, etc.)
- **Waves** (WaveShell plugins)
- **TAL-Software** (TAL-Reverb, TAL-Chorus, etc.)
- **XLN Audio** (RC-20, Addictive series)
- **Cable Guys** (HalfTime, ShaperBox)
- **Eventide** (Blackhole, UltraReverb)
- **2getheraudio** (RICH, Abyss)
- **Cherry Audio** (Mercury-4, etc.)
- And many more...

Manufacturers are detected from:
- File path structures
- Plugin naming conventions
- Ableton's internal plugin categorization

## Troubleshooting

### Common Issues

**"No .als files found"**
- Verify the directory path is correct
- Ensure you have read permissions for the directory
- Check that .als files exist in the selected folder or subfolders

**"Permission denied" errors**
- Run with appropriate permissions (especially for network drives)
- On Windows, try running Command Prompt as Administrator
- On macOS/Linux, ensure you have read access to the directory

**GUI doesn't appear**
- Ensure you're running the script without the `--cli` flag
- Check that your system supports Tkinter (included with most Python installations)
- Try running from terminal/command prompt to see any error messages

**Network drive access issues**
- Map network drives to local drive letters (Windows)
- Use full UNC paths: `\\ServerName\ShareName\Path`
- Ensure network connectivity and permissions

### Performance Tips

- **Large Collections**: The tool processes files sequentially. Expect 1-2 seconds per project file.
- **Network Drives**: Scanning over networks will be slower. Consider copying projects locally for faster analysis.
- **Memory Usage**: The tool loads each .als file into memory during processing but releases it immediately after.

## Technical Details

- **File Format**: Ableton Live .als files are gzipped XML
- **Parsing**: Uses Python's built-in `xml.etree.ElementTree` and `gzip` modules
- **Manufacturer Detection**: Combines path analysis, naming patterns, and known plugin databases
- **Cross-platform**: Pure Python with no external dependencies

## Contributing

Found a plugin whose manufacturer isn't detected correctly? Want to add support for more manufacturers? Contributions welcome!

The manufacturer detection logic is in the `get_manufacturer_from_plugin_name()` function - feel free to add more patterns.

## License

MIT License - feel free to use, modify, and distribute.

## Changelog

### v1.1 (Latest)
- Added manufacturer/developer detection
- Enhanced reporting with manufacturer groupings
- Improved GUI with manufacturer summaries
- Better error handling for network drives

### v1.0
- Initial release
- Basic VST extraction and reporting
- Dual GUI/CLI interface
- Network drive support

---

**Note**: This tool only reads .als files and never modifies them. It's completely safe to use on your project library.