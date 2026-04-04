import os
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from flask import Flask, Response, abort

app = Flask(__name__)

LEVEL_COLORS = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]
CELL_SIZE = 11
CELL_GAP = 2


def fetch_contribution_html(username: str) -> str:
    url = f"https://github.com/users/{username}/contributions"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; GitHubContributionSnake/1.0)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return response.text


def parse_contributions(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", class_="ContributionCalendar-grid")
    if table is None:
        raise ValueError("Contribution chart not found in GitHub profile HTML")

    rows = table.find_all("tr")
    days = []
    for row_index, row in enumerate(rows):
        cols = row.find_all("td", attrs={"data-date": True})
        for col_index, td in enumerate(cols):
            date = td["data-date"]
            level = int(td.get("data-level", "0"))
            days.append(
                {
                    "date": date,
                    "level": level,
                    "col": col_index,
                    "row": row_index,
                }
            )

    if not days:
        raise ValueError("No contribution records found")

    days.sort(key=lambda item: item["date"])
    return days


def build_snake_svg(username: str, days: list[dict]) -> str:
    max_col = max(day["col"] for day in days)
    max_row = max(day["row"] for day in days)
    width = (max_col + 1) * (CELL_SIZE + CELL_GAP)
    height = (max_row + 1) * (CELL_SIZE + CELL_GAP)

    cells = []
    path_points = []
    for item in days:
        x = item["col"] * (CELL_SIZE + CELL_GAP)
        y = item["row"] * (CELL_SIZE + CELL_GAP)
        color = LEVEL_COLORS[min(max(item["level"], 0), len(LEVEL_COLORS) - 1)]
        cells.append(
            f'<rect x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" fill="{color}" rx="2" ry="2" />'
        )
        cx = x + CELL_SIZE / 2
        cy = y + CELL_SIZE / 2
        path_points.append(f"{cx},{cy}")

    snake_path = "M" + " L".join(path_points)
    latest_date = days[-1]["date"]
    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    svg = f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height + 80}' viewBox='0 0 {width} {height + 80}' role='img' aria-label='GitHub contributions snake calendar for {username}'>
  <style>
    .title {{ font: 14px sans-serif; fill: #24292f; }}
    .subtitle {{ font: 12px sans-serif; fill: #57606a; }}
    .snake-head {{ fill: #ffb400; stroke: #fff; stroke-width: 2; }}
    .snake-body {{ fill: none; stroke: #ffb400; stroke-width: 2; opacity: 0.75; }}
  </style>
  <text x='0' y='{height + 20}' class='title'>GitHub Snake Calendar — {username}</text>
  <text x='0' y='{height + 38}' class='subtitle'>Latest date: {latest_date} · Updated: {generated_at}</text>
  <g transform='translate(0,0)'>
    {' '.join(cells)}
    <path id='snakePath' d='{snake_path}' class='snake-body' />
    <circle r='5' class='snake-head'>
      <animateMotion dur='12s' repeatCount='indefinite' rotate='auto'>
        <mpath href='#snakePath' />
      </animateMotion>
    </circle>
  </g>
</svg>
"""
    return svg


def get_snake_svg(username: str) -> str:
    html = fetch_contribution_html(username)
    days = parse_contributions(html)
    return build_snake_svg(username, days)


@app.route("/")
def index():
    return (
        "<h1>GitHub Contribution Snake Service</h1>"
        "<p>Use <code>/snake/&lt;username&gt;</code> to fetch a live snake-style contribution SVG.</p>"
        "<p>Example: <a href='/snake/lucianma05-create'>/snake/lucianma05-create</a></p>"
    )


@app.route("/snake/<username>")
def snake(username: str):
    try:
        svg = get_snake_svg(username)
    except requests.HTTPError as exc:
        abort(exc.response.status_code, f"GitHub request failed: {exc}")
    except ValueError as exc:
        abort(502, str(exc))
    return Response(svg, mimetype="image/svg+xml")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
