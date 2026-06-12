---
name: "disk-usage-reporter"
description: "Scan /home/openclaw and generate interactive treemap report on attibot"
---

# Disk Usage Reporter SKILL

Generates an interactive treemap HTML report showing disk usage across `/home/openclaw`, published to `attibot.ingeniosolution.it`.

## Features

- **Interactive D3.js Treemap** — drill down from root to individual files
- **Real-time Stats** — total size, file count, directory count
- **Breadcrumb Navigation** — traverse hierarchy with back button
- **Export JSON** — download raw data
- **Responsive Design** — works on all devices

## Usage

Run the SKILL when you want to regenerate the disk usage report:

```
/disk-usage-reporter
```

Reports are saved to:
- **Local:** `/home/openclaw/attibot/reports/YYYYMMDD_disk-usage/index.html`
- **Web:** `https://attibot.ingeniosolution.it/reports/YYYYMMDD_disk-usage/`

## How It Works

1. Scans entire `/home/openclaw` directory recursively
2. Excludes common large folders (`.git`, `node_modules`, `__pycache__`, etc.)
3. Calculates cumulative size for each directory
4. Generates interactive HTML with D3.js treemap
5. Publishes to attibot web reports directory

## Generated Report Features

- **Treemap visualization** — size represented by rectangle area
- **Color gradient** — spectrum colors for visual distinction
- **Click to drill down** — select any rectangle to zoom into that directory
- **Hover info** — shows current selection size and item count
- **Reset button** — returns to root view
- **Export** — download raw JSON data for external analysis

## Configuration

Edit `_utility/static/disk-usage-reporter.py` to:
- Change `exclude_dirs` (line 19) to skip additional paths
- Adjust `max_depth` for faster/slower scanning
- Customize colors/styling in HTML generation

## Performance

- Full scan: ~10-30 seconds depending on fragmentation
- Excludes `.git`, `node_modules`, `__pycache__`, `.next`, `venv`, `.cache` by default
- Generates report once per day (timestamp in filename)

## Customization

### Exclude more directories

Edit `exclude_dirs` in the script:

```python
exclude_dirs = {'.git', '__pycache__', 'node_modules', '.next', '.venv', 'venv', '.cache', 'your_dir_here'}
```

### Change report location

Modify output path in `generate_html()`:

```python
output_path = Path(f"/custom/path/{today}_disk-usage/index.html")
```

### Adjust visualization

Edit HTML generation in `generate_html()` function:
- Colors: change `d3.interpolateSpectral` to other D3 color schemes
- Height: modify `height: 600px` in CSS
- Recursion depth: adjust `max_depth` parameter in `get_dir_size()`

## Related Files

- **Script:** `_utility/static/disk-usage-reporter.py`
- **Output:** `/home/openclaw/attibot/reports/`
- **Web Base:** `https://attibot.ingeniosolution.it/reports/`
