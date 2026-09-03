#!/usr/bin/env python3
"""
Generates the custom SVG widgets for Rashmi's GitHub profile README.

Everything here is hand built rather than pulled from a third party service,
so the profile keeps working when someone else's free tier goes down. The
animation is SMIL, which GitHub's image proxy passes through, and each file
still reads correctly on its first frame if a renderer ignores the animation.

    python make-assets.py
"""

import pathlib

OUT = pathlib.Path(__file__).parent / "assets"
OUT.mkdir(parents=True, exist_ok=True)

# purple family, shared with rashmigamage.com
INK      = "#0E0718"
INK_2    = "#160D24"
DEEP     = "#2B0A5E"
VIOLET   = "#8B2FF0"
LIT      = "#B366FF"
PALE     = "#D9C4FF"
CREAM    = "#F3ECFF"
MUTED    = "#8A7FA6"
MINT     = "#5EEAD4"

FONT = "'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', 'SF Mono', Consolas, 'Courier New', monospace"


def bars(w, h, seed=7):
    """Vertical bar texture, same motif as her website hero."""
    out, x, n = [], 0, seed
    while x < w:
        n = (n * 1103515245 + 12345) % 2147483648
        bw = 4 + (n >> 16) % 26
        n = (n * 1103515245 + 12345) % 2147483648
        op = [0.018, 0.03, 0.045, 0.062][(n >> 16) % 4]
        out.append(f'<rect x="{x}" y="0" width="{bw}" height="{h}" fill="#FFFFFF" opacity="{op}"/>')
        n = (n * 1103515245 + 12345) % 2147483648
        x += bw + 3 + (n >> 16) % 22
    return "".join(out)


# --------------------------------------------------------------------------
# 1. banner
# --------------------------------------------------------------------------

def banner():
    W, H = 1200, 330
    cx, cy, r = 985, 165, 96

    # the sweep wedge, drawn once and rotated by SMIL
    wedge = (f'M{cx} {cy} L{cx + r} {cy} '
             f'A{r} {r} 0 0 0 {cx + r * 0.906} {cy - r * 0.423} Z')

    rings = "".join(
        f'<circle cx="{cx}" cy="{cy}" r="{rr}" fill="none" stroke="{LIT}" '
        f'stroke-width="1" opacity="{op}"/>'
        for rr, op in ((r, 0.55), (r * 0.68, 0.32), (r * 0.36, 0.2))
    )

    # three detected defects, fading in one after another
    blips = ""
    for i, (bx, by, delay) in enumerate((
        (cx - 44, cy - 38, 0.0), (cx + 34, cy + 26, 1.2), (cx - 18, cy + 54, 2.4)
    )):
        blips += f'''<g>
      <circle cx="{bx}" cy="{by}" r="4.5" fill="{MINT}"/>
      <circle cx="{bx}" cy="{by}" r="4.5" fill="none" stroke="{MINT}" stroke-width="1.4">
        <animate attributeName="r" values="4.5;16" dur="3.6s" begin="{delay}s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values=".9;0" dur="3.6s" begin="{delay}s" repeatCount="indefinite"/>
      </circle>
    </g>'''

    # the pass ticks that stamp in along the bottom rule
    ticks = ""
    for i in range(6):
        tx = 64 + i * 30
        ticks += (f'<path d="M{tx} 268 l5 5 l9 -11" fill="none" stroke="{MINT}" '
                  f'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" opacity="0">'
                  f'<animate attributeName="opacity" values="0;1;1;1;0" dur="6s" '
                  f'begin="{i * 0.35}s" repeatCount="indefinite"/></path>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Rashmi Gamage, Quality Assurance Engineer">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{INK}"/>
      <stop offset="58%" stop-color="#1B0B36"/>
      <stop offset="100%" stop-color="{DEEP}"/>
    </linearGradient>
    <radialGradient id="glow" cx="82%" cy="46%" r="52%">
      <stop offset="0%" stop-color="{VIOLET}" stop-opacity=".55"/>
      <stop offset="100%" stop-color="{VIOLET}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{LIT}" stop-opacity=".55"/>
      <stop offset="100%" stop-color="{LIT}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="name" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{CREAM}"/>
      <stop offset="70%" stop-color="{PALE}"/>
      <stop offset="100%" stop-color="{LIT}"/>
    </linearGradient>
    <clipPath id="clip"><rect width="{W}" height="{H}" rx="10"/></clipPath>
  </defs>

  <g clip-path="url(#clip)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    {bars(W, H)}
    <rect width="{W}" height="{H}" fill="url(#glow)"/>

    <!-- radar -->
    <g>
      {rings}
      <path d="{wedge}" fill="url(#sweep)">
        <animateTransform attributeName="transform" type="rotate"
          from="0 {cx} {cy}" to="360 {cx} {cy}" dur="4.4s" repeatCount="indefinite"/>
      </path>
      <line x1="{cx - r}" y1="{cy}" x2="{cx + r}" y2="{cy}" stroke="{LIT}" stroke-width="1" opacity=".22"/>
      <line x1="{cx}" y1="{cy - r}" x2="{cx}" y2="{cy + r}" stroke="{LIT}" stroke-width="1" opacity=".22"/>
      {blips}
      <text x="{cx}" y="{cy + r + 26}" font-family="{MONO}" font-size="11" font-weight="600"
            letter-spacing="2.6" fill="{MUTED}" text-anchor="middle">SCANNING</text>
    </g>

    <!-- wordmark -->
    <text x="60" y="120" font-family="{FONT}" font-size="66" font-weight="800"
          letter-spacing="-1.4" fill="url(#name)">RASHMI GAMAGE</text>
    <text x="62" y="158" font-family="{MONO}" font-size="15" font-weight="600"
          letter-spacing="5.2" fill="{LIT}">QUALITY ASSURANCE ENGINEER</text>

    <text x="62" y="205" font-family="{FONT}" font-size="19" font-weight="400" fill="{PALE}">
      I find the bugs before your users do.</text>

    <line x1="60" y1="238" x2="700" y2="238" stroke="{LIT}" stroke-width="1" opacity=".28"/>
    {ticks}
    <text x="252" y="273" font-family="{MONO}" font-size="12" font-weight="600"
          letter-spacing="1.8" fill="{MUTED}">6 SUITES PASSED &#183; 0 FAILED &#183; 0 SKIPPED</text>

    <g>
      <circle cx="1126" cy="34" r="5" fill="{MINT}">
        <animate attributeName="opacity" values="1;.2;1" dur="2.4s" repeatCount="indefinite"/>
      </circle>
      <text x="1112" y="38" font-family="{MONO}" font-size="11" font-weight="600"
            letter-spacing="1.6" fill="{MINT}" text-anchor="end">OPEN TO QA ROLES</text>
    </g>

    <rect width="{W}" height="{H}" fill="none" stroke="{VIOLET}" stroke-width="1" opacity=".4" rx="10"/>
  </g>
</svg>'''


# --------------------------------------------------------------------------
# 2. coverage meters
# --------------------------------------------------------------------------

SKILLS = [
    ("Manual &amp; functional testing", 93),
    ("Test case design &amp; documentation", 90),
    ("Defect reporting &amp; tracking", 88),
    ("API testing / Postman &amp; JMeter", 84),
    ("Automation / Selenium &amp; Playwright", 80),
    ("IoT &amp; device testing", 76),
]


def coverage():
    W = 880
    top, row = 86, 46
    H = top + row * len(SKILLS) + 26
    track_x, track_w = 340, 420

    rows = ""
    for i, (label, pct) in enumerate(SKILLS):
        y = top + i * row
        fw = round(track_w * pct / 100, 1)
        rows += f'''
    <text x="30" y="{y + 4}" font-family="{FONT}" font-size="14" fill="{PALE}">{label}</text>
    <rect x="{track_x}" y="{y - 8}" width="{track_w}" height="9" rx="4.5" fill="{LIT}" opacity=".12"/>
    <rect x="{track_x}" y="{y - 8}" width="0" height="9" rx="4.5" fill="url(#fill)">
      <animate attributeName="width" from="0" to="{fw}" dur="1.15s"
               begin="{0.16 * i:.2f}s" fill="freeze" calcMode="spline"
               keySplines="0.2 0.8 0.25 1" keyTimes="0;1"/>
    </rect>
    <text x="{W - 30}" y="{y + 4}" font-family="{MONO}" font-size="13" font-weight="600"
          fill="{LIT}" text-anchor="end">{pct}%</text>'''

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Test coverage by discipline">
  <defs>
    <linearGradient id="fill" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{VIOLET}"/>
      <stop offset="100%" stop-color="{LIT}"/>
    </linearGradient>
  </defs>
  <rect width="{W}" height="{H}" rx="10" fill="{INK_2}" stroke="{VIOLET}" stroke-width="1" stroke-opacity=".38"/>

  <text x="30" y="36" font-family="{MONO}" font-size="12" font-weight="700"
        letter-spacing="3" fill="{LIT}">COVERAGE REPORT</text>
  <text x="{W - 30}" y="36" font-family="{MONO}" font-size="11" font-weight="600"
        letter-spacing="1.4" fill="{MUTED}" text-anchor="end">SELF ASSESSED</text>
  <line x1="30" y1="52" x2="{W - 30}" y2="52" stroke="{LIT}" stroke-width="1" opacity=".2"/>
  {rows}
</svg>'''


# --------------------------------------------------------------------------
# 3. defect lifecycle
# --------------------------------------------------------------------------

STAGES = [
    ("FOUND", "exploratory pass"),
    ("REPRODUCED", "twice, cleanly"),
    ("DOCUMENTED", "steps + evidence"),
    ("FILED", "jira, prioritised"),
    ("VERIFIED", "by me, not the dev"),
]


def lifecycle():
    W, H = 940, 190
    n = len(STAGES)
    pad = 88
    span = (W - pad * 2) / (n - 1)
    y = 92

    line = f'<line x1="{pad}" y1="{y}" x2="{W - pad}" y2="{y}" stroke="{LIT}" stroke-width="1.4" opacity=".3"/>'

    # a token travelling the whole path, so the graphic reads as a process
    token = f'''<circle r="6" fill="{MINT}">
    <animate attributeName="cx" values="{pad};{W - pad}" dur="5s" repeatCount="indefinite"
             calcMode="spline" keySplines="0.45 0 0.55 1" keyTimes="0;1"/>
    <animate attributeName="cy" values="{y};{y}" dur="5s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0;1;1;1;0" dur="5s" repeatCount="indefinite"/>
  </circle>'''

    nodes = ""
    for i, (name, note) in enumerate(STAGES):
        x = pad + span * i
        nodes += f'''
    <g>
      <rect x="{x - 11}" y="{y - 11}" width="22" height="22" rx="4" fill="{INK}"
            stroke="{LIT}" stroke-width="1.6" transform="rotate(45 {x} {y})"/>
      <circle cx="{x}" cy="{y}" r="4" fill="{LIT}">
        <animate attributeName="fill" values="{LIT};{MINT};{LIT}" dur="5s"
                 begin="{i * 1.0:.1f}s" repeatCount="indefinite"/>
      </circle>
      <text x="{x}" y="{y - 30}" font-family="{MONO}" font-size="11.5" font-weight="700"
            letter-spacing="1.5" fill="{CREAM}" text-anchor="middle">{name}</text>
      <text x="{x}" y="{y + 40}" font-family="{FONT}" font-size="11.5"
            fill="{MUTED}" text-anchor="middle">{note}</text>
    </g>'''

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="How a defect moves through my workflow">
  <rect width="{W}" height="{H}" rx="10" fill="{INK_2}" stroke="{VIOLET}" stroke-width="1" stroke-opacity=".38"/>
  <text x="30" y="34" font-family="{MONO}" font-size="12" font-weight="700"
        letter-spacing="3" fill="{LIT}">DEFECT LIFECYCLE</text>
  <text x="{W - 30}" y="34" font-family="{MONO}" font-size="11" font-weight="600"
        letter-spacing="1.4" fill="{MUTED}" text-anchor="end">NOTHING SKIPS A STEP</text>
  {line}
  {nodes}
  {token}
  <text x="{W / 2}" y="{H - 16}" font-family="{FONT}" font-size="12" fill="{MUTED}"
        text-anchor="middle">A bug nobody can reproduce is just a rumour.</text>
</svg>'''


for name, svg in (("banner.svg", banner()),
                  ("coverage.svg", coverage()),
                  ("lifecycle.svg", lifecycle())):
    path = OUT / name
    path.write_text(svg, encoding="utf-8")
    print(f"{name:16} {path.stat().st_size / 1024:6.1f} KB")
