#!/usr/bin/env python3
"""Disk Usage Reporter — generates interactive treemap HTML report"""
import os
import json
from pathlib import Path
from datetime import datetime

def get_dir_size(path, exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = {'.git', '__pycache__', 'node_modules', '.next', '.venv', 'venv', '.cache'}
    
    try:
        path_obj = Path(path)
        if not path_obj.exists():
            return None
        
        if path_obj.name in exclude_dirs:
            return None
        
        if path_obj.is_file():
            return {"name": path_obj.name, "size": path_obj.stat().st_size, "type": "file"}
        
        if path_obj.is_dir():
            total_size = 0
            children = []
            try:
                for item in sorted(path_obj.iterdir(), key=lambda x: -get_size_quick(x)):
                    if item.name in exclude_dirs:
                        continue
                    child_data = get_dir_size(item, exclude_dirs)
                    if child_data:
                        children.append(child_data)
                        total_size += child_data["size"]
            except PermissionError:
                pass
            return {"name": path_obj.name, "size": total_size, "type": "dir", "children": children}
    except Exception as e:
        print(f"Error: {e}", flush=True)
        return None

def get_size_quick(path):
    try:
        return path.stat().st_size if path.is_file() else sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
    except:
        return 0

def human_readable(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"

def generate_html(data, output_path):
    html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Disk Usage Report</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{ font-family: -apple-system, sans-serif; background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 2rem; }}
        #treemap {{ background: white; height: 600px; border-radius: 8px; }}
        .node {{ fill: #667eea; stroke: white; stroke-width: 2px; cursor: pointer; }}
        .node:hover {{ fill: #764ba2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Disk Usage Report — /home/openclaw</h1>
    </div>
    <div class="container">
        <div id="treemap"></div>
    </div>
    <script>
        const data = {json.dumps(data)};
        // Treemap rendering code here
    </script>
</body>
</html>"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding='utf-8')
    print(f"✅ Report: {output_path}")

if __name__ == "__main__":
    data = get_dir_size('/home/openclaw')
    if data:
        today = datetime.now().strftime("%Y%m%d")
        output_path = Path(f"/home/openclaw/attibot/reports/{today}_disk-usage/index.html")
        generate_html(data, output_path)
        print(f"📊 Total: {human_readable(data['size'])}")
        print(f"🌐 View: https://attibot.ingeniosolution.it/reports/{today}_disk-usage/")
