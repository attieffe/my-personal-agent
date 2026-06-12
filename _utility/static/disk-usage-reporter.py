#!/usr/bin/env python3
"""
Disk Usage Reporter — generates interactive treemap HTML report
Scans /home/openclaw, calculates size per directory/file, outputs interactive visualization
"""

import os
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def get_dir_size(path, max_depth=None, current_depth=0, exclude_dirs=None):
    """
    Recursively calculate directory sizes.
    Returns dict: {"name": str, "size": int, "children": [...]}
    """
    if exclude_dirs is None:
        exclude_dirs = {'.git', '__pycache__', 'node_modules', '.next', '.venv', 'venv', '.cache'}

    if max_depth is not None and current_depth > max_depth:
        return None

    try:
        path_obj = Path(path)
        if not path_obj.exists():
            return None

        # Check if directory should be excluded
        if path_obj.name in exclude_dirs:
            return None

        if path_obj.is_file():
            return {
                "name": path_obj.name,
                "size": path_obj.stat().st_size,
                "type": "file"
            }

        if path_obj.is_dir():
            total_size = 0
            children = []

            try:
                for item in sorted(path_obj.iterdir(), key=lambda x: -get_size_quick(x)):
                    if item.name in exclude_dirs:
                        continue

                    child_data = get_dir_size(item, max_depth, current_depth + 1, exclude_dirs)
                    if child_data:
                        children.append(child_data)
                        total_size += child_data["size"]
            except PermissionError:
                pass

            return {
                "name": path_obj.name,
                "size": total_size,
                "type": "dir",
                "children": children
            }
    except Exception as e:
        print(f"Error processing {path}: {e}", flush=True)
        return None

def get_size_quick(path):
    """Quick size for sorting"""
    try:
        if path.is_file():
            return path.stat().st_size
        else:
            return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
    except:
        return 0

def human_readable(size):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"

def generate_html(data, output_path):
    """Generate interactive HTML with treemap + table view"""

    html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Disk Usage Report — /home/openclaw</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .header h1 {{ font-size: 1.8rem; margin-bottom: 0.5rem; }}
        .header .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }}

        .stat-card {{
            background: rgba(255,255,255,0.15);
            padding: 1rem;
            border-radius: 8px;
            backdrop-filter: blur(10px);
        }}

        .stat-value {{ font-size: 1.4rem; font-weight: bold; }}
        .stat-label {{ font-size: 0.8rem; opacity: 0.85; margin-top: 0.25rem; }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}

        .controls {{
            background: white;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }}

        .controls button {{
            background: #667eea;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.85rem;
            transition: background 0.2s;
        }}

        .controls button:hover {{ background: #5568d3; }}
        .controls button.active {{ background: #764ba2; }}

        .breadcrumb {{
            background: white;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            font-size: 0.9rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}

        .breadcrumb a {{
            color: #667eea;
            cursor: pointer;
            text-decoration: none;
        }}

        .breadcrumb a:hover {{ text-decoration: underline; }}

        .view-container {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }}

        #treemap {{
            height: 400px;
            width: 100%;
        }}

        .node {{
            fill: #667eea;
            stroke: white;
            stroke-width: 2px;
            cursor: pointer;
        }}

        .node:hover {{ fill: #764ba2; }}

        .node-label {{
            font-size: 11px;
            fill: white;
            pointer-events: none;
            font-weight: 500;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.4);
        }}

        .table-view {{
            display: none;
            max-height: 500px;
            overflow-y: auto;
        }}

        .table-view.active {{ display: block; }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th {{
            background: #f8f9fa;
            padding: 0.75rem;
            text-align: left;
            font-size: 0.85rem;
            font-weight: 600;
            color: #333;
            border-bottom: 2px solid #ddd;
            cursor: pointer;
            user-select: none;
        }}

        th:hover {{ background: #efefef; }}

        td {{
            padding: 0.75rem;
            border-bottom: 1px solid #eee;
            font-size: 0.9rem;
        }}

        tr:hover {{
            background: #f9f9f9;
        }}

        .name-cell {{
            color: #667eea;
            cursor: pointer;
            text-decoration: none;
        }}

        .name-cell:hover {{ text-decoration: underline; }}

        .size-cell {{
            text-align: right;
            font-family: 'Monaco', monospace;
            color: #666;
        }}

        .percent-cell {{
            text-align: right;
            font-weight: 500;
        }}

        .bar {{
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            height: 4px;
            border-radius: 2px;
            margin-top: 0.25rem;
        }}

        .timestamp {{
            text-align: center;
            color: #999;
            font-size: 0.8rem;
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid #eee;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Disk Usage Report</h1>
        <p>/home/openclaw — Smart Explorer</p>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value" id="total-size">—</div>
                <div class="stat-label">Total Size</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="item-count">—</div>
                <div class="stat-label">Items Shown</div>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="controls">
            <button id="treemap-btn" class="active">📊 Treemap</button>
            <button id="table-btn">📋 Table</button>
            <button id="reset-btn">🔄 Reset</button>
            <button id="export-btn">📥 JSON</button>
        </div>

        <div class="breadcrumb" id="breadcrumb">
            <strong>📂 Path:</strong> <a onclick="resetView()">/home/openclaw</a>
        </div>

        <div class="view-container">
            <div id="treemap"></div>
            <div class="table-view" id="table-view">
                <table id="items-table">
                    <thead>
                        <tr>
                            <th onclick="sortTable('name')">Name</th>
                            <th onclick="sortTable('size')">Size</th>
                            <th style="width: 150px;" onclick="sortTable('percent')">%</th>
                        </tr>
                    </thead>
                    <tbody id="table-body"></tbody>
                </table>
            </div>
        </div>

        <div class="timestamp">
            Generated on 2026-06-12 at 07:31 (Europe/Rome) | Auto-regenerated via SKILL
        </div>
    </div>

    <script>
        const fullData = {json.dumps(data)};
        let currentNode = fullData;
        let history = [fullData];
        let sortBy = 'size';

        function humanReadable(bytes) {{
            const units = ['B', 'KB', 'MB', 'GB', 'TB'];
            let size = bytes;
            let unitIdx = 0;
            while (size >= 1024 && unitIdx < units.length - 1) {{
                size /= 1024;
                unitIdx++;
            }}
            return size.toFixed(1) + ' ' + units[unitIdx];
        }}

        function renderTreemap() {{
            const width = document.getElementById('treemap').offsetWidth;
            const height = 400;

            d3.select("#treemap").selectAll("*").remove();

            const svg = d3.select("#treemap")
                .append("svg")
                .attr("width", width)
                .attr("height", height);

            const hierarchy = d3.hierarchy(currentNode)
                .sum(d => d.size)
                .sort((a, b) => b.value - a.value);

            const treemap = d3.treemap()
                .size([width, height])
                .paddingTop(30)
                .paddingRight(2)
                .paddingBottom(2)
                .paddingLeft(2);

            treemap(hierarchy);

            const g = svg.selectAll("g")
                .data(hierarchy.leaves())
                .enter()
                .append("g")
                .attr("transform", d => `translate(${{d.x0}},${{d.y0}})`);

            g.append("rect")
                .attr("width", d => Math.max(0, d.x1 - d.x0))
                .attr("height", d => Math.max(0, d.y1 - d.y0))
                .attr("class", "node")
                .style("fill", (d, i) => d3.interpolateSpectral(i / Math.max(1, hierarchy.leaves().length - 1)))
                .on("click", (e, d) => {{
                    if (d.data.children) {{
                        history.push(d.data);
                        updateView();
                    }}
                }});

            g.append("text")
                .attr("class", "node-label")
                .attr("x", 4)
                .attr("y", 16)
                .text(d => {{
                    const w = d.x1 - d.x0;
                    const h = d.y1 - d.y0;
                    if (w < 40 || h < 30) return '';
                    const label = d.data.name;
                    const size = humanReadable(d.value);
                    return label.length > 15 ? label.substring(0, 12) + '...' : label;
                }});

            updateStats();
        }}

        function renderTable() {{
            const items = (currentNode.children || [])
                .map(d => ({{name: d.name, size: d.size, type: d.type, data: d}}))
                .sort((a, b) => {{
                    if (sortBy === 'size') return b.size - a.size;
                    if (sortBy === 'name') return a.name.localeCompare(b.name);
                    return 0;
                }});

            const totalSize = currentNode.size || items.reduce((s, i) => s + i.size, 0);
            let html = '';

            items.forEach(item => {{
                const pct = ((item.size / totalSize) * 100).toFixed(1);
                const icon = item.type === 'dir' ? '📁' : '📄';
                html += `<tr>
                    <td><span class="name-cell" onclick="drillDown('${{item.name.replace(/'/g, "\\\\'")}}')">${{icon}} ${{item.name}}</span></td>
                    <td class="size-cell">${{humanReadable(item.size)}}</td>
                    <td class="percent-cell">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <div class="bar" style="width: ${{pct * 2}}px;"></div>
                            <span>${{pct}}%</span>
                        </div>
                    </td>
                </tr>`;
            }});

            document.getElementById('table-body').innerHTML = html;
            updateStats();
        }}

        function updateView() {{
            updateBreadcrumb();

            const treemapBtn = document.getElementById('treemap-btn');
            const tableBtn = document.getElementById('table-btn');

            if (treemapBtn.classList.contains('active')) {{
                renderTreemap();
            }} else {{
                renderTable();
            }}
        }}

        function updateBreadcrumb() {{
            const parts = history.map((n, i) =>
                `<a onclick="goToHistory(${{i}})">${{n.name}}</a>`
            ).join(' / ');
            document.getElementById('breadcrumb').innerHTML =
                '<strong>📂 Path:</strong> ' + parts;
        }}

        function goToHistory(idx) {{
            history = history.slice(0, idx + 1);
            currentNode = history[history.length - 1];
            updateView();
        }}

        function drillDown(name) {{
            if (currentNode.children) {{
                const child = currentNode.children.find(c => c.name === name);
                if (child) {{
                    history.push(child);
                    currentNode = child;
                    updateView();
                }}
            }}
        }}

        function resetView() {{
            history = [fullData];
            currentNode = fullData;
            updateView();
        }}

        function updateStats() {{
            const size = currentNode.size;
            const count = (currentNode.children || []).length;
            document.getElementById('total-size').textContent = humanReadable(size);
            document.getElementById('item-count').textContent = count;
        }}

        function sortTable(by) {{
            sortBy = by;
            renderTable();
        }}

        document.getElementById('treemap-btn').onclick = () => {{
            document.getElementById('treemap-btn').classList.add('active');
            document.getElementById('table-btn').classList.remove('active');
            document.getElementById('treemap').style.display = 'block';
            document.getElementById('table-view').classList.remove('active');
            renderTreemap();
        }};

        document.getElementById('table-btn').onclick = () => {{
            document.getElementById('table-btn').classList.add('active');
            document.getElementById('treemap-btn').classList.remove('active');
            document.getElementById('treemap').style.display = 'none';
            document.getElementById('table-view').classList.add('active');
            renderTable();
        }};

        document.getElementById('reset-btn').onclick = resetView;

        document.getElementById('export-btn').onclick = () => {{
            const json = JSON.stringify(fullData, null, 2);
            const blob = new Blob([json], {{ type: 'application/json' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'disk-usage-' + new Date().toISOString().split('T')[0] + '.json';
            a.click();
        }};

        renderTreemap();
        updateBreadcrumb();
    </script>
</body>
</html>"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ Report generated: {output_path}", flush=True)

if __name__ == "__main__":
    print("🔍 Scanning /home/openclaw...", flush=True)

    data = get_dir_size('/home/openclaw', max_depth=None)

    if data:
        today = datetime.now().strftime("%Y%m%d")
        output_path = Path(f"/home/openclaw/attibot/reports/{today}_disk-usage/index.html")

        generate_html(data, output_path)

        print(f"📊 Total size: {human_readable(data['size'])}", flush=True)
        print(f"🌐 View at: https://attibot.ingeniosolution.it/reports/{today}_disk-usage/", flush=True)
    else:
        print("❌ Failed to scan directory", flush=True)
