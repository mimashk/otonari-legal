#!/usr/bin/env python3
"""
法務文書の Markdown を、公開する HTML に変換する。

★★**Markdown の原本はアプリのリポジトリにしかない。** ここはコピーを持たない。
   二重管理になると、実装を変えたときに片方だけ直る。

  ../fertility-med-reminder/docs/legal/*.md   ← 原本（非公開リポジトリ）
  ./*.html                                    ← 生成物（このリポジトリ・公開）

使い方:  python3 build.py
"""

import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(HERE, "..", "fertility-med-reminder", "docs", "legal")

SITE_NAME = "Otonari"
PAGES = [
    ("privacy-policy", "プライバシーポリシー"),
    ("terms-of-service", "利用規約"),
    ("support", "サポート"),
    ("account-deletion", "アカウントの削除"),
]


# --- インライン記法 -----------------------------------------------------------

def inline(text):
    """エスケープしてから **太字** / `コード` / [label](url) を戻す。"""
    out = html.escape(text)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"`(.+?)`", r"<code>\1</code>", out)

    def link(m):
        label, href = m.group(1), m.group(2)
        # ★相対リンクは .md → .html に差し替える（./privacy-policy.md など）
        href = re.sub(r"^\./", "", href)
        if href.endswith(".md"):
            href = href[:-3] + ".html"
        return '<a href="%s">%s</a>' % (href, label)

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, out)


# --- ブロック記法 -------------------------------------------------------------

BLOCK_START = re.compile(r"^(#{1,4}\s|[-*]\s|\d+\.\s|\|)")
HR = re.compile(r"^-{3,}$")


def convert(md):
    lines = md.split("\n")
    out = []
    i = 0

    while i < len(lines):
        stripped = lines[i].strip()

        if stripped == "":
            i += 1
            continue

        if HR.fullmatch(stripped):
            out.append("<hr>")
            i += 1
            continue

        heading = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if heading:
            level = len(heading.group(1))
            out.append("<h%d>%s</h%d>" % (level, inline(heading.group(2)), level))
            i += 1
            continue

        # 表（次の行が |---|---| のときだけ）
        if (
            stripped.startswith("|")
            and i + 1 < len(lines)
            and re.fullmatch(r"\|[\s\-:|]+\|", lines[i + 1].strip())
        ):
            head = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            body = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                body.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            ths = "".join("<th>%s</th>" % inline(c) for c in head)
            trs = "".join(
                "<tr>%s</tr>" % "".join("<td>%s</td>" % inline(c) for c in row)
                for row in body
            )
            out.append(
                '<div class="scroll"><table><thead><tr>%s</tr></thead>'
                "<tbody>%s</tbody></table></div>" % (ths, trs)
            )
            continue

        if re.match(r"^[-*]\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i].strip()):
                text = re.sub(r"^[-*]\s+", "", lines[i].strip())
                items.append("<li>%s</li>" % inline(text))
                i += 1
            out.append("<ul>%s</ul>" % "".join(items))
            continue

        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                text = re.sub(r"^\d+\.\s+", "", lines[i].strip())
                items.append("<li>%s</li>" % inline(text))
                i += 1
            out.append("<ol>%s</ol>" % "".join(items))
            continue

        # 段落。★日本語なので行をつなぐときに空白を入れない
        para = []
        while (
            i < len(lines)
            and lines[i].strip() != ""
            and not BLOCK_START.match(lines[i].strip())
            and not HR.fullmatch(lines[i].strip())
        ):
            para.append(lines[i].strip())
            i += 1
        out.append("<p>%s</p>" % inline("".join(para)))

    return "\n".join(out)


# --- ページの枠 ---------------------------------------------------------------

# ★アプリのパレット（apps/mobile/src/theme/palette.ts）に合わせてある。
#   アプリから開く文書なので、地続きに見えるほうがよい。
CSS = """
:root{
  --bg:#F4FAF9; --surface:#FFFFFF; --text:#12302B; --muted:#5A7370;
  --accent:#15796A; --border:#E2EEEC; --mark:#EBF4F2;
}
@media (prefers-color-scheme: dark){
  :root{
    --bg:#0E1A18; --surface:#152523; --text:#E8F2F0; --muted:#9DB5B1;
    --accent:#66D9DB; --border:#24403C; --mark:#1C302D;
  }
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0; background:var(--bg); color:var(--text);
  font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans","Hiragino Kaku Gothic ProN",
    "Noto Sans JP","Yu Gothic",Meiryo,sans-serif;
  font-size:16px; line-height:1.9;
}
.wrap{max-width:720px; margin:0 auto; padding:0 20px 80px}
header{border-bottom:1px solid var(--border); background:var(--surface)}
.head{max-width:720px; margin:0 auto; padding:18px 20px}
.brand{font-size:17px; font-weight:700; letter-spacing:.02em; text-decoration:none; color:var(--text)}
nav{margin-top:10px; display:flex; flex-wrap:wrap; gap:16px}
nav a{font-size:13px; color:var(--muted); text-decoration:none}
nav a:hover{color:var(--accent)}
nav a[aria-current]{color:var(--accent); font-weight:700}
h1{font-size:26px; line-height:1.45; margin:40px 0 8px; letter-spacing:.01em}
h2{font-size:19px; line-height:1.5; margin:44px 0 10px; padding-top:18px; border-top:1px solid var(--border)}
h3{font-size:16px; margin:28px 0 6px; color:var(--accent)}
h4{font-size:15px; margin:22px 0 4px}
p{margin:14px 0}
ul,ol{margin:14px 0; padding-left:1.4em}
li{margin:6px 0}
a{color:var(--accent)}
strong{font-weight:700}
code{
  font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.88em;
  background:var(--mark); padding:.12em .4em; border-radius:4px;
}
hr{border:0; border-top:1px solid var(--border); margin:36px 0}
.scroll{overflow-x:auto; -webkit-overflow-scrolling:touch; margin:18px 0}
table{border-collapse:collapse; width:100%; font-size:14.5px; line-height:1.75}
th,td{border:1px solid var(--border); padding:9px 12px; text-align:left; vertical-align:top}
th{background:var(--mark); font-weight:700; white-space:nowrap}
footer{
  max-width:720px; margin:0 auto; padding:28px 20px 60px;
  border-top:1px solid var(--border); color:var(--muted); font-size:13px;
}
footer a{color:var(--muted)}
"""

TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | {site}</title>
<meta name="description" content="{desc}">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="icon" href="favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="theme-color" content="#EAFBF8">
<style>{css}</style>
</head>
<body>
<header><div class="head">
<a class="brand" href="index.html">{site}</a>
<nav>{nav}</nav>
</div></header>
<main class="wrap">
{body}
</main>
<footer>
<p>お問い合わせ: <a href="mailto:otonari.app@gmail.com">otonari.app@gmail.com</a></p>
<p>&copy; {site}</p>
</footer>
</body>
</html>
"""


def nav_html(current):
    parts = []
    for slug, label in PAGES:
        mark = ' aria-current="page"' if slug == current else ""
        parts.append('<a href="%s.html"%s>%s</a>' % (slug, mark, label))
    return "".join(parts)


def render(slug, title, body, desc):
    return TEMPLATE.format(
        title=title, site=SITE_NAME, desc=html.escape(desc),
        css=CSS, nav=nav_html(slug), body=body,
    )


INDEX_BODY = """<h1>Otonari</h1>
<p>妊活・不妊治療のお薬アラーム「Otonari」に関する文書です。</p>
<ul>
<li><a href="privacy-policy.html">プライバシーポリシー</a></li>
<li><a href="terms-of-service.html">利用規約</a></li>
<li><a href="support.html">サポート</a></li>
<li><a href="account-deletion.html">アカウントの削除</a></li>
</ul>
"""


def main():
    if not os.path.isdir(SOURCE_DIR):
        sys.exit(
            "原本が見つかりません: %s\n"
            "★このリポジトリは、アプリのリポジトリと同じ階層に置く前提です。" % SOURCE_DIR
        )

    for slug, title in PAGES:
        src = os.path.join(SOURCE_DIR, slug + ".md")
        with open(src, encoding="utf-8") as f:
            md = f.read()

        body = convert(md)
        # ★原本の1行目の見出しは本文側で <h1> になるので、そのまま使う
        desc = "%s - %s" % (title, SITE_NAME)
        out = os.path.join(HERE, slug + ".html")
        with open(out, "w", encoding="utf-8") as f:
            f.write(render(slug, title, body, desc))
        print("生成: %s.html" % slug)

    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
        f.write(render("", "Otonari", INDEX_BODY, "Otonari の法務文書とサポート"))
    print("生成: index.html")


if __name__ == "__main__":
    main()
