#!/usr/bin/env python3
"""
Renders the profile stat cards from live GitHub data.

Why this exists: the three services most profiles lean on for stat cards
(github-readme-stats, github-readme-activity-graph, github-profile-trophy)
were all returning 503 or "payment required" when this profile was built, so
every README pointing at them shows broken images. This script fetches the
same numbers from the GitHub API and draws them locally, on a schedule, using
nothing but the standard library. Nothing to install, nothing to pay for, and
no third party that can take the profile down.

Run by .github/workflows/stats.yml. Locally:

    python scripts/build_stats.py --user RashmiGamage00
    python scripts/build_stats.py --demo        # layout check, no network
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import ssl
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

# purple family, shared with rashmigamage.com and the other widgets
INK_2  = "#160D24"
INK    = "#0E0718"
VIOLET = "#8B2FF0"
LIT    = "#B366FF"
PALE   = "#D9C4FF"
CREAM  = "#F3ECFF"
MUTED  = "#8A7FA6"
MINT   = "#5EEAD4"

FONT = "'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', 'SF Mono', Consolas, 'Courier New', monospace"

# language ramp, dark to light, so the bar reads as one family
RAMP = ["#4A1580", "#6A22B4", "#8B2FF0", "#A354F5", "#BB7CF8", "#D2A5FB", "#E4C9FD"]

GRAPHQL = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalRepositoryContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount date } }
      }
    }
  }
}
"""


# ---------------------------------------------------------------- fetching

def _get(url: str, token: str | None):
    ctx = ssl.create_default_context()
    headers = {
        "User-Agent": "rashmi-profile-stats",
        "Accept": "application/vnd.github+json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        return json.loads(r.read().decode("utf-8"))


def _graphql(login: str, token: str):
    ctx = ssl.create_default_context()
    body = json.dumps({"query": GRAPHQL, "variables": {"login": login}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "User-Agent": "rashmi-profile-stats",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        payload = json.loads(r.read().decode("utf-8"))
    if payload.get("errors"):
        raise RuntimeError(payload["errors"][0].get("message", "graphql error"))
    return payload["data"]["user"]["contributionsCollection"]


def collect(user: str, token: str | None) -> dict:
    profile = _get(f"https://api.github.com/users/{user}", token)

    repos, page = [], 1
    while True:
        chunk = _get(
            f"https://api.github.com/repos?per_page=100&page={page}".replace(
                "/repos?", f"/users/{user}/repos?"
            ),
            token,
        )
        repos.extend(chunk)
        if len(chunk) < 100:
            break
        page += 1

    own = [r for r in repos if not r.get("fork")]
    stars = sum(r.get("stargazers_count", 0) for r in own)
    forks = sum(r.get("forks_count", 0) for r in own)

    langs: dict[str, int] = {}
    for r in own:
        try:
            for name, n in _get(r["languages_url"], token).items():
                langs[name] = langs.get(name, 0) + n
        except urllib.error.HTTPError:
            continue

    data = {
        "user": user,
        "name": profile.get("name") or user,
        "repos": len(own),
        "stars": stars,
        "forks": forks,
        "followers": profile.get("followers", 0),
        "since": (profile.get("created_at") or "")[:4],
        "langs": langs,
        "commits": None,
        "prs": None,
        "issues": None,
        "contributions": None,
        "streak": None,
        "calendar": [],
    }

    if token:
        try:
            c = _graphql(user, token)
            cal = c["contributionCalendar"]
            days = [d for w in cal["weeks"] for d in w["contributionDays"]]
            data.update(
                commits=c["totalCommitContributions"],
                prs=c["totalPullRequestContributions"],
                issues=c["totalIssueContributions"],
                contributions=cal["totalContributions"],
                calendar=[d["contributionCount"] for d in days],
                streak=_streak(days),
            )
        except Exception as e:                      # noqa: BLE001
            print(f"  contribution data unavailable ({e}), card degrades", file=sys.stderr)

    return data


def _streak(days) -> int:
    """Longest run of consecutive days with at least one contribution."""
    best = run = 0
    today = dt.date.today().isoformat()
    for d in days:
        if d["date"] > today:
            break
        if d["contributionCount"] > 0:
            run += 1
            best = max(best, run)
        else:
            run = 0
    return best


# ---------------------------------------------------------------- rendering

def _fmt(v) -> str:
    if v is None:
        return "--"
    if v >= 1000:
        return f"{v / 1000:.1f}k".replace(".0k", "k")
    return f"{v:02d}" if v < 10 else str(v)


def stats_card(d: dict) -> str:
    W, H = 500, 292
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%d %b %Y").upper()

    tiles = [
        ("REPOSITORIES", _fmt(d["repos"])),
        ("STARS EARNED", _fmt(d["stars"])),
        ("COMMITS / YR", _fmt(d["commits"])),
        ("PULL REQUESTS", _fmt(d["prs"])),
        ("CONTRIBUTIONS", _fmt(d["contributions"])),
        ("LONGEST STREAK", _fmt(d["streak"])),
    ]

    cols, cw, ch = 3, 148, 66
    x0, y0 = 26, 78
    body = ""
    for i, (label, value) in enumerate(tiles):
        cx = x0 + (i % cols) * cw
        cy = y0 + (i // cols) * ch
        body += f'''
  <text x="{cx}" y="{cy + 26}" font-family="{FONT}" font-size="27" font-weight="700"
        fill="{CREAM}">{value}</text>
  <text x="{cx}" y="{cy + 44}" font-family="{MONO}" font-size="8.6" font-weight="600"
        letter-spacing="1.5" fill="{MUTED}">{label}</text>'''

    # sparkline of the contribution calendar, if the token let us have it
    spark = ""
    cal = d.get("calendar") or []
    if cal:
        recent = cal[-91:]
        peak = max(recent) or 1
        bw = (W - 52) / len(recent)
        base, tall = H - 24, 32          # baseline and maximum bar height
        bars = "".join(
            f'<rect x="{26 + i * bw:.2f}" y="{base - (v / peak) * tall:.2f}" '
            f'width="{max(bw - 0.7, 0.8):.2f}" height="{max((v / peak) * tall, 1):.2f}" '
            f'rx="0.6" fill="{LIT}" opacity="{0.28 + 0.72 * (v / peak):.2f}"/>'
            for i, v in enumerate(recent)
        )
        spark = f'''
  <line x1="26" y1="208" x2="{W - 26}" y2="208" stroke="{LIT}" stroke-width="1" opacity=".16"/>
  <text x="26" y="224" font-family="{MONO}" font-size="8.6" font-weight="600"
        letter-spacing="1.5" fill="{MUTED}">LAST 13 WEEKS</text>
  {bars}'''
    else:
        spark = f'''
  <line x1="26" y1="208" x2="{W - 26}" y2="208" stroke="{LIT}" stroke-width="1" opacity=".16"/>
  <text x="26" y="234" font-family="{MONO}" font-size="9" font-weight="600"
        letter-spacing="1.4" fill="{MUTED}">CONTRIBUTION DATA REFRESHES DAILY</text>'''

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="GitHub statistics for {d['user']}">
  <rect width="{W}" height="{H}" rx="10" fill="{INK_2}" stroke="{VIOLET}" stroke-width="1" stroke-opacity=".38"/>
  <text x="26" y="34" font-family="{MONO}" font-size="11.5" font-weight="700"
        letter-spacing="2.8" fill="{LIT}">RUN SUMMARY</text>
  <text x="{W - 26}" y="34" font-family="{MONO}" font-size="9" font-weight="600"
        letter-spacing="1.2" fill="{MUTED}" text-anchor="end">{stamp}</text>
  <line x1="26" y1="50" x2="{W - 26}" y2="50" stroke="{LIT}" stroke-width="1" opacity=".2"/>
  <text x="26" y="66" font-family="{FONT}" font-size="11" fill="{PALE}">on GitHub since {d['since']}</text>
  {body}
  {spark}
</svg>'''


def langs_card(d: dict) -> str:
    W = 380
    langs = sorted(d["langs"].items(), key=lambda kv: -kv[1])[:6]
    total = sum(n for _, n in langs) or 1
    H = max(92 + len(langs) * 24 + 14, 292)

    bar_y, bar_w, bar_h = 62, W - 52, 11
    x, seg, legend = 26.0, "", ""
    for i, (name, n) in enumerate(langs):
        share = n / total
        w = bar_w * share
        first, last = i == 0, i == len(langs) - 1
        r = 5.5
        # rounded outer ends only, so the segments read as one bar
        if first or last:
            seg += (f'<rect x="{x:.2f}" y="{bar_y}" width="{max(w, 1):.2f}" height="{bar_h}" '
                    f'rx="{r}" fill="{RAMP[i]}"/>')
            if w > r:
                patch = x + (r if first else 0)
                seg += (f'<rect x="{patch:.2f}" y="{bar_y}" width="{max(w - r, 0.5):.2f}" '
                        f'height="{bar_h}" fill="{RAMP[i]}"/>')
        else:
            seg += (f'<rect x="{x:.2f}" y="{bar_y}" width="{max(w, 1):.2f}" height="{bar_h}" '
                    f'fill="{RAMP[i]}"/>')
        x += w

        ly = 100 + i * 24
        legend += f'''
  <circle cx="32" cy="{ly - 4}" r="5" fill="{RAMP[i]}"/>
  <text x="46" y="{ly}" font-family="{FONT}" font-size="13" fill="{PALE}">{_esc(name)}</text>
  <text x="{W - 26}" y="{ly}" font-family="{MONO}" font-size="11.5" font-weight="600"
        fill="{LIT}" text-anchor="end">{share * 100:.1f}%</text>'''

    if not langs:
        legend = (f'<text x="26" y="104" font-family="{FONT}" font-size="12" '
                  f'fill="{MUTED}">No language data yet.</text>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Most used languages">
  <rect width="{W}" height="{H}" rx="10" fill="{INK_2}" stroke="{VIOLET}" stroke-width="1" stroke-opacity=".38"/>
  <text x="26" y="34" font-family="{MONO}" font-size="11.5" font-weight="700"
        letter-spacing="2.8" fill="{LIT}">LANGUAGE MIX</text>
  <text x="26" y="50" font-family="{FONT}" font-size="11" fill="{MUTED}">by bytes across public repositories</text>
  {seg}
  {legend}
  <line x1="26" y1="{H - 48}" x2="{W - 26}" y2="{H - 48}" stroke="{LIT}" stroke-width="1" opacity=".16"/>
  <text x="26" y="{H - 28}" font-family="{MONO}" font-size="8.6" font-weight="600"
        letter-spacing="1.5" fill="{MUTED}">{d['repos']} PUBLIC REPOSITORIES &#183; REFRESHED DAILY</text>
</svg>'''


def _esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


DEMO = {
    "user": "RashmiGamage00", "name": "Rashmi Gamage",
    "repos": 4, "stars": 0, "forks": 0, "followers": 0, "since": "2023",
    "langs": {"Java": 412000, "JavaScript": 268000, "CSS": 94000,
              "HTML": 61000, "Python": 18000},
    "commits": 128, "prs": 9, "issues": 4, "contributions": 164, "streak": 11,
    "calendar": [(i * 7 % 11) // 3 for i in range(91)],
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default=os.environ.get("PROFILE_USER", "RashmiGamage00"))
    ap.add_argument("--demo", action="store_true", help="render sample data, no network")
    args = ap.parse_args()

    if args.demo:
        data = DEMO
        print("rendering demo data")
    else:
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if not token:
            print("no GITHUB_TOKEN set, contribution counts will show as --")
        try:
            data = collect(args.user, token)
        except Exception as e:                      # noqa: BLE001
            print(f"could not reach the GitHub API: {e}", file=sys.stderr)
            return 1

    OUT.mkdir(parents=True, exist_ok=True)
    for name, svg in (("stats.svg", stats_card(data)), ("langs.svg", langs_card(data))):
        path = OUT / name
        path.write_text(svg, encoding="utf-8")
        print(f"{name:12} {path.stat().st_size / 1024:5.1f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
