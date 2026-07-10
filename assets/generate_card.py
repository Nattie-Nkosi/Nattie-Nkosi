"""Generate a neofetch-style profile card SVG for the GitHub README.

Converts the Memoji avatar screenshot into ASCII art and lays it out next to a
colored "system info" panel. Re-run to regenerate assets/neofetch-card.svg:

    python assets/generate_card.py
"""

from pathlib import Path
from xml.sax.saxutils import escape
from PIL import Image, ImageDraw, ImageEnhance

ROOT = Path(__file__).resolve().parent
SRC = r"C:/Users/nkosi/Pictures/Screenshots/Screenshot 2026-07-10 124934.png"
OUT = ROOT / "neofetch-card.svg"

# ---------------------------------------------------------------- ASCII art ---
def build_ascii(width=48):
    im = Image.open(SRC).convert("RGB")
    crop = im.crop((350, 152, 622, 424))
    d = ImageDraw.Draw(crop)
    d.rectangle((222, 196, 272, 272), fill=crop.getpixel((10, 10)))  # hide octocat badge
    crop = ImageEnhance.Contrast(crop).enhance(1.25)
    w, h = crop.size
    height = int(width * (h / w) * 0.5)
    g = crop.convert("L").resize((width, height))
    px = g.load()
    T, MX = 33, 235
    ramp = ".:-=+*oe%@"
    cx, cy, rx, ry = width / 2, height / 2, width / 2, height / 2
    lines = []
    for y in range(height):
        row = ""
        for x in range(width):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 > 1.03:
                row += " "
                continue
            v = px[x, y]
            if v <= T:
                row += " "
                continue
            t = min(1.0, (v - T) / (MX - T))
            row += ramp[int(t * (len(ramp) - 1))]
        lines.append(row.rstrip())
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


# ---------------------------------------------------------------- palette ----
C = {
    "bg": "#0b0e14",
    "bar": "#11151c",
    "border": "#1c2430",
    "dim": "#3b4261",
    "user": "#7aa2f7",
    "at": "#565f89",
    "header": "#f7768e",
    "label": "#e0af68",
    "cyan": "#7dcfff",
    "green": "#9ece6a",
    "blue": "#7aa2f7",
    "magenta": "#bb9af7",
    "orange": "#ff9e64",
    "fg": "#c0caf5",
}

# content: field rows carry (label, value, value-color)
B = ("blank",)
CONTENT = [
    ("user", "nattie", "nkosi"),
    B,
    ("field", "OS", "Windows 11 · Arch Linux", "cyan"),
    ("field", "Host", "Johannesburg, South Africa", "cyan"),
    ("field", "Role", "Senior Software Engineer · IT Specialist", "cyan"),
    ("field", "Editor", "VS Code · Neovim", "cyan"),
    ("field", "Shell", "bash · pwsh", "cyan"),
    ("field", "Uptime", "5+ years coding", "cyan"),
    B,
    ("header", "Languages"),
    ("field", "Programming", "TypeScript, JavaScript, C#, Go", "green"),
    ("field", "Frontend", "React, Next.js, Angular, Tailwind", "green"),
    ("field", "Backend", "Node.js, NestJS, ASP.NET, EF Core", "green"),
    ("field", "Data & Ops", "PostgreSQL, Prisma, Docker, Vercel", "green"),
    B,
    ("header", "Currently"),
    ("field", "Learning", "Go, AI / LLMs", "magenta"),
    ("field", "Building", "Full-stack web applications", "magenta"),
    B,
    ("header", "Contact"),
    ("field", "Email", "nkosin361@gmail.com", "blue"),
    ("field", "Portfolio", "portfolio-v2-gamma-one.vercel.app", "blue"),
    ("field", "LinkedIn", "in/nkosinathi-nkosi", "blue"),
    ("field", "X / Twitter", "@NattieNkosi", "blue"),
    B,
    ("header", "GitHub Stats"),
    ("field", "Repos", "146   ·   Stars   12", "orange"),
    ("field", "Community", "23 followers   ·   17 following", "orange"),
]

VAL_START = 15  # column (chars) where values begin


def esc(s):
    return escape(s)


def tspan(text, fill, extra=""):
    return f'<tspan fill="{fill}"{extra}>{esc(text)}</tspan>'


def build_info(x, y0, line_h, char_w):
    total_cols = 46
    out = []
    y = y0
    for row in CONTENT:
        kind = row[0]
        if kind == "blank":
            y += line_h * 0.55
            continue
        if kind == "user":
            _, u, host = row
            head = f"{u}@{host}"
            dashes = "-" * max(2, total_cols - len(head) - 1)
            spans = (
                tspan(u, C["user"]) + tspan("@", C["at"]) + tspan(host, C["user"])
                + tspan(" " + dashes, C["dim"])
            )
        elif kind == "header":
            text = row[1]
            dashes = "-" * max(2, total_cols - len(text) - 1)
            spans = tspan(text + " ", C["header"]) + tspan(dashes, C["dim"])
        else:  # field
            _, label, value, color = row
            fill = VAL_START - len(label)
            if fill >= 2:
                leader = " " + "." * (fill - 2) + " "
            else:
                leader = " "
            spans = (
                tspan(label, C["label"]) + tspan(leader, C["dim"])
                + tspan(value, C[color])
            )
        out.append(
            f'<text x="{x}" y="{y:.1f}" xml:space="preserve">{spans}</text>'
        )
        y += line_h
    return "\n".join(out), y


def main():
    art = build_ascii(48)

    # geometry
    pad = 26
    bar_h = 34
    art_fs, art_lh = 12.5, 13.0
    art_x = pad + 8
    art_char_w = art_fs * 0.62

    info_fs, info_lh = 15.0, 20.5
    info_char_w = info_fs * 0.60
    art_w = max(len(l) for l in art) * art_char_w
    info_x = art_x + art_w + 44
    info_y0 = bar_h + 40

    info_svg, info_end_y = build_info(info_x, info_y0, info_lh, info_char_w)

    width = 940
    height = int(info_end_y + pad)

    # vertically center the portrait against the info panel
    art_block_h = len(art) * art_lh
    art_y0 = bar_h + max(30, (height - bar_h - art_block_h) / 2)

    # art tspans
    art_spans = []
    for i, line in enumerate(art):
        dy = "0" if i == 0 else f"{art_lh}"
        art_spans.append(
            f'<tspan x="{art_x}" dy="{dy}" xml:space="preserve">{esc(line) or " "}</tspan>'
        )
    art_text = (
        f'<text y="{art_y0}" font-size="{art_fs}" fill="url(#skin)" '
        f'font-family="ui-monospace, \'Cascadia Code\', \'Courier New\', monospace">'
        + "".join(art_spans)
        + "</text>"
    )

    dots = (
        f'<circle cx="{pad + 8}" cy="{bar_h/2}" r="5.5" fill="#ff5f57"/>'
        f'<circle cx="{pad + 26}" cy="{bar_h/2}" r="5.5" fill="#febc2e"/>'
        f'<circle cx="{pad + 44}" cy="{bar_h/2}" r="5.5" fill="#28c840"/>'
    )
    title = (
        f'<text x="{width/2}" y="{bar_h/2 + 4}" text-anchor="middle" '
        f'font-size="12.5" fill="#565f89" '
        f'font-family="ui-monospace, monospace">nattie@nkosi: ~</text>'
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="ui-monospace, 'Cascadia Code', 'Courier New', monospace">
  <defs>
    <linearGradient id="skin" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ffe0b0"/>
      <stop offset="0.55" stop-color="#e8a56a"/>
      <stop offset="1" stop-color="#b76f3c"/>
    </linearGradient>
  </defs>
  <rect x="1" y="1" width="{width-2}" height="{height-2}" rx="14" fill="{C['bg']}" stroke="{C['border']}" stroke-width="1.5"/>
  <path d="M1 15 a14 14 0 0 1 14 -14 h{width-30} a14 14 0 0 1 14 14 v{bar_h-15} h-{width-2} z" fill="{C['bar']}"/>
  <line x1="1" y1="{bar_h}" x2="{width-1}" y2="{bar_h}" stroke="{C['border']}" stroke-width="1"/>
  {dots}
  {title}
  {art_text}
  <g font-size="{info_fs}">
{info_svg}
  </g>
</svg>
'''
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT}  ({width}x{height}, {len(art)} art lines)")


if __name__ == "__main__":
    main()
