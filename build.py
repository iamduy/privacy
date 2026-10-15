#!/usr/bin/env python3
"""Generate privacy policy pages for every game in games/*.json.

Output (committed, served by GitHub Pages from the repo root):
  <slug>/<lang>.html   policy page per game and language
  <slug>/index.html    redirect to the game's first language
  index.html           list of all games
  en.html, vi.html     legacy redirects for the game marked "legacy_root"

Usage: python3 build.py
"""
import html
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOCALES = {p.stem: json.loads(p.read_text("utf-8")) for p in sorted((ROOT / "locales").glob("*.json"))}


def fmt_date(iso, lang):
    d = date.fromisoformat(iso)
    if lang == "vi":
        return f"{d.day:02d}/{d.month:02d}/{d.year}"
    return f"{d.strftime('%B')} {d.day}, {d.year}"


def head(lang, title, css=None, extra=""):
    link = f'\n  <link rel="stylesheet" href="{css}">' if css else ""
    return f"""<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>{extra}{link}
</head>
"""


def redirect_page(target, title):
    extra = f'\n  <meta http-equiv="refresh" content="0; url={target}">\n  <link rel="canonical" href="{target}">'
    return head("en", title, extra=extra) + f"""<body>
  <p><a href="{target}">{html.escape(title)}</a></p>
</body>
</html>
"""


def policy_page(game, lang):
    L = LOCALES[lang]
    t = game["text"][lang]
    v = {
        "name": html.escape(game["name"]),
        "developer": html.escape(game["developer"]),
        "email": game["contact_email"],
        "date": fmt_date(game["effective_date"], lang),
        "min_age": game.get("min_age", 13),
        "local_data": t["local_data"],
    }
    s = lambda key: L[key].format(**v)  # noqa: E731
    ads = game.get("ads")

    others = [o for o in game["languages"] if o != lang]
    switch = " ".join(f'<a href="{o}.html" hreflang="{o}">{LOCALES[o]["lang_name"]}</a>' for o in others)

    summary = [s("summary_no_account"), s("summary_no_collect")]
    summary.append(s("summary_ads_admob") if ads == "admob" else s("summary_no_ads"))

    out = [f'<span class="lang">{switch}</span>'] if switch else []
    out += [f"<h1>{s('h1')}</h1>",
           f'<p class="meta">{s("meta")}</p>',
           "",
           f"<p>{t['intro']}</p>",
           "",
           f"<h2>{s('summary_h')}</h2>",
           '<div class="card">',
           "  <ul>",
           *[f"    <li>{x}</li>" for x in summary],
           "  </ul>",
           "</div>",
           "",
           f"<h2>{s('local_h')}</h2>",
           f"<p>{s('local_p')}" + (f" {s('local_reset')}" if game.get("reset_progress_in_app") else "") + "</p>"]

    if ads == "admob":
        choices = []
        if game.get("privacy_options_in_app"):
            choices.append(s("choices_consent"))
        choices += [s("choices_ios"), s("choices_android")]
        out += ["",
                f"<h2>{s('admob_h')}</h2>",
                f"<p>{s('admob_p')}</p>",
                "<ul>", *[f"  <li>{x}</li>" for x in L["admob_items"]], "</ul>",
                f"<p>{s('admob_policies')}</p>",
                "",
                f"<h2>{s('choices_h')}</h2>",
                "<ul>", *[f"  <li>{x}</li>" for x in choices], "</ul>",
                f"<p>{s('choices_decline')}</p>"]
    elif ads:
        raise SystemExit(f"{game['slug']}: unsupported ads provider {ads!r}")

    for sec in t.get("extra_sections", []):
        out += ["", f"<h2>{sec['heading']}</h2>", sec["html"]]

    children = s("children_p") + (" " + s("children_ads") if ads else "")
    out += ["",
            f"<h2>{s('children_h')}</h2>", f"<p>{children}</p>",
            "",
            f"<h2>{s('changes_h')}</h2>", f"<p>{s('changes_p')}</p>",
            "",
            f"<h2>{s('contact_h')}</h2>", f"<p>{s('contact_p')}</p>"]

    body = "\n".join(f"  {line}" if line else "" for line in out)
    return head(lang, s("title"), "../assets/style.css") + f"<body>\n<main>\n{body}\n</main>\n</body>\n</html>\n"


def index_page(games):
    items = []
    for g in games:
        links = " · ".join(f'<a href="{g["slug"]}/{lang}.html" hreflang="{lang}">{LOCALES[lang]["lang_name"]}</a>' for lang in g["languages"])
        items.append(f"      <li><strong>{html.escape(g['name'])}</strong> — {links}</li>")
    L = LOCALES["en"]
    return head("en", L["index_title"], "assets/style.css") + f"""<body>
<main>
  <h1>{L['index_h1']}</h1>
  <div class="card">
    <ul>
{chr(10).join(items)}
    </ul>
  </div>
</main>
</body>
</html>
"""


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, "utf-8")
    print("wrote", path.relative_to(ROOT))


def main():
    games = []
    for p in sorted((ROOT / "games").glob("*.json")):
        game = json.loads(p.read_text("utf-8"))
        game["slug"] = p.stem
        for lang in game["languages"]:
            if lang not in LOCALES:
                raise SystemExit(f"{p.name}: no locales/{lang}.json")
            if lang not in game["text"]:
                raise SystemExit(f"{p.name}: missing text.{lang}")
        games.append(game)

    for g in games:
        for lang in g["languages"]:
            write(ROOT / g["slug"] / f"{lang}.html", policy_page(g, lang))
        write(ROOT / g["slug"] / "index.html", redirect_page(f"{g['languages'][0]}.html", f"{g['name']} Privacy Policy"))
        if g.get("legacy_root"):
            for lang in g["languages"]:
                write(ROOT / f"{lang}.html", redirect_page(f"{g['slug']}/{lang}.html", f"{g['name']} Privacy Policy"))

    write(ROOT / "index.html", index_page(games))


if __name__ == "__main__":
    main()
