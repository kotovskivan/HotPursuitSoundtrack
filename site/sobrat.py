# -*- coding: utf-8 -*-
"""
Сборка сайта Hot Pursuit Soundtrack — NFS Hot Pursuit 2010 + Remastered (по образцу сайта Heat Soundtrack, 21.11.2026).
  До выпуска (released = no): первый экран «Скоро», разделы «Что будет уметь» / «Что нужно» / «Как дела». К выпуску — добавить
  в shablon.html скрины, «Как пользоваться», помощь, «Что нового» (как у Heat) и окно «Скачать».

  shablon.html  — разметка и стиль (одна на все языки)
  teksty/*.txt  — тексты, по файлу на язык (ключ = текст)
  sajt.txt      — общее: выпуск (released), версия, размер zip, ссылки, языки, адрес сайта
  static/       — картинки, шрифт, иконка (копируются как есть)
  -> gotovo/    — готовый сайт: /index.html (главный язык), /en/, /de/, ... + sitemap.xml  (= ветка gh-pages)

  py sobrat.py               собрать
  py sobrat.py --prosmotr    собрать и открыть в браузере (http://localhost:8768/)
  py sobrat.py --opublikovat собрать и отправить на GitHub: исходник сайта (папка site) -> main, gotovo/ -> gh-pages
"""
import datetime
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "gotovo"
PORT = 8768
APP = "Hot Pursuit Soundtrack"
LABEL = {"uk": "UA"}                      # подпись кнопки языка (остальные — код большими буквами)
HTML_LANG = {"zh": "zh-Hans"}             # lang="" в html; в адресе и hreflang — код как есть
CJK = {"zh", "ja", "ko"}                  # без курсива
TICKER = "HOT PURSUIT SOUNDTRACK / 2010 + REMASTERED / FAN-MADE / NOT AFFILIATED WITH EA / KITIVSKI + CLAUDE / "

warnings = []


def fail(msg):
    print("ОШИБКА: " + msg)
    sys.exit(1)


def read_kv(path):
    data = {}
    for n, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if " = " in s:
            k, v = s.split(" = ", 1)
        elif s.endswith(" ="):
            k, v = s[:-2], ""
        else:
            fail(f"{path.name}, строка {n}: нет « = » — {s[:70]}")
        k = k.strip()
        if k in data:
            warnings.append(f"{path.name}: ключ «{k}» записан дважды — беру последний")
        data[k] = v.strip()
    return data


def esc(s):
    return html.escape(s, quote=True)


def main():
    if not (ROOT / "sajt.txt").exists():
        fail("нет sajt.txt рядом со скриптом")
    cfg = read_kv(ROOT / "sajt.txt")
    released = cfg.get("released", "no").lower() in ("yes", "да", "1", "true")
    langs = [x.strip() for x in cfg["languages"].split(";") if x.strip()]
    main_lang = langs[0]
    base = cfg["base_url"].rstrip("/") + "/"
    size = cfg["size"]
    subst = {"version": cfg["version"], "size": size, "size_c": size.replace(".", ",")}
    versions = []
    for item in cfg["versions"].split(";"):
        parts = item.split()
        if len(parts) != 2:
            fail(f"sajt.txt, versions: «{item.strip()}» — нужно «версия дата»")
        versions.append(parts)

    texts = {}
    for L in langs:
        p = ROOT / "teksty" / f"{L}.txt"
        if not p.exists():
            fail(f"нет файла teksty/{L}.txt")
        texts[L] = read_kv(p)

    template = (ROOT / "shablon.html").read_text(encoding="utf-8")
    need = sorted(set(re.findall(r"\{\{([\w .-]+?)(?:\|attr)?\}\}", template)) |
                  ({f"log {v}" for v, _ in versions} if released else set()) |   # «Что нового» — только после выпуска
                  {"seo_title", "seo_desc", "og_locale", "lang_name", "suggest",
                   "soon", "download", "source", "guide", "hubReady", "hubSoon"})

    def path_of(L):
        return "" if L == main_lang else f"{L}/"

    def url_of(L):
        return base + path_of(L)

    def md(text, L, key):
        def ph(m):
            k = m.group(1)
            if k in subst:
                return subst[k]
            warnings.append(f"{L}.txt, «{key}»: неизвестная вставка {{{k}}}")
            return m.group(0)
        t = re.sub(r"\{(\w+)\}", ph, text)
        t = html.escape(t, quote=False)
        t = t.replace("\\n", "<br>")
        t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)

        def link(m):
            label, target = m.group(1), m.group(2)
            u = cfg.get(target, target)
            if not u.startswith(("http://", "https://")):
                fail(f"{L}.txt, «{key}»: ссылка [{label}]({target}) — нет такого ключа в sajt.txt и это не адрес")
            return f'<a href="{esc(u)}" target="_blank" rel="noopener">{label}</a>'
        return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, t)

    def plain(h):
        return html.unescape(re.sub(r"<[^>]+>", "", h))

    def get_text(L, key):
        for src in (L, "en", main_lang):
            if src in texts and texts[src].get(key):
                if src != L:
                    warnings.append(f"{L}.txt: нет «{key}» — взял из {src}.txt")
                return md(texts[src][key], L, key)
        fail(f"текста «{key}» нет ни в {L}.txt, ни в en.txt, ни в {main_lang}.txt")

    # чистим gotovo/, но не трогаем .git (это ветка gh-pages для публикации)
    OUT.mkdir(exist_ok=True)
    for p in OUT.iterdir():
        if p.name == ".git":
            continue
        shutil.rmtree(p) if p.is_dir() else p.unlink()
    shutil.copytree(ROOT / "static", OUT, dirs_exist_ok=True)

    newest_date = max(d for _, d in versions)
    today = datetime.date.today().isoformat()
    og_img = f"{base}img/og.jpg"

    for L in langs:
        T = {k: get_text(L, k) for k in need if not k.startswith(("!", "@"))}
        rel = "" if L == main_lang else "../"
        me = url_of(L)
        title, desc = plain(T["seo_title"]), plain(T["seo_desc"])

        def href_to(X):
            return (rel + path_of(X)) or "./"

        # --- SEO в <head> ---
        head = [
            f"<title>{esc(title)}</title>",
            f'<meta name="description" content="{esc(desc)}">',
            f'<link rel="canonical" href="{esc(me)}">',
        ]
        head += [f'<link rel="alternate" hreflang="{X}" href="{esc(url_of(X))}">' for X in langs]
        head.append(f'<link rel="alternate" hreflang="x-default" href="{esc(url_of(cfg.get("x_default", main_lang)))}">')
        head += [
            '<meta property="og:type" content="website">',
            f'<meta property="og:site_name" content="{APP}">',
            f'<meta property="og:title" content="{esc(title)}">',
            f'<meta property="og:description" content="{esc(desc)}">',
            f'<meta property="og:url" content="{esc(me)}">',
            f'<meta property="og:image" content="{esc(og_img)}">',
            '<meta property="og:image:width" content="1200">',
            '<meta property="og:image:height" content="630">',
            f'<meta property="og:locale" content="{esc(plain(T["og_locale"]))}">',
        ]
        head += [f'<meta property="og:locale:alternate" content="{esc(plain(get_text(X, "og_locale")))}">'
                 for X in langs if X != L]
        head += [
            '<meta name="twitter:card" content="summary_large_image">',
            f'<meta name="twitter:title" content="{esc(title)}">',
            f'<meta name="twitter:description" content="{esc(desc)}">',
            f'<meta name="twitter:image" content="{esc(og_img)}">',
        ]
        if cfg.get("google_verify"):
            head.append(f'<meta name="google-site-verification" content="{esc(cfg["google_verify"])}">')
        ld = {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": APP,
            "alternateName": "Hot Pursuit Soundtrack — NFS Hot Pursuit / Hot Pursuit Remastered custom music mod",
            "description": desc,
            "url": me,
            "inLanguage": HTML_LANG.get(L, L),
            "applicationCategory": "GameApplication",
            "applicationSubCategory": "Game mod tool",
            "operatingSystem": "Windows 10, Windows 11",
            "isAccessibleForFree": True,
            "license": "https://www.gnu.org/licenses/gpl-3.0.html",
            "image": og_img,
            "author": {"@type": "Person", "name": "Kitivski", "url": cfg["kitivski"]},
            "creditText": "Kitivski + Claude",
            "isPartOf": {"@type": "WebSite", "name": "NFS Own Music", "url": cfg["hub"]},
            "sameAs": [cfg["github"]],
        }
        if released:
            ld.update({"softwareVersion": cfg["version"], "fileSize": f"{size} MB", "downloadUrl": cfg["download"],
                       "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
                       "datePublished": min(d for _, d in versions), "dateModified": newest_date})
        ld_txt = json.dumps(ld, ensure_ascii=False, indent=1).replace("</", "<\\/")
        head.append(f'<script type="application/ld+json">\n{ld_txt}\n</script>')

        langs_nav = "".join(
            f'<a href="{href_to(X)}" hreflang="{X}" lang="{HTML_LANG.get(X, X)}"'
            + (' aria-current="page"' if X == L else "")
            + f'><b>{LABEL.get(X, X.upper())}</b>{esc(plain(get_text(X, "lang_name")))}</a>'
            for X in langs)
        cur_label = f'{LABEL.get(L, L.upper())}<span class="ln"> · {esc(plain(T["lang_name"]))}</span>'   # 16.11: на телефоне .ln прячется — только «UA»
        pages = {X: {"t": plain(get_text(X, "suggest")), "href": href_to(X)} for X in langs}

        if released:
            cta = (f'<a class="btn main" href="{esc(cfg["download"])}" target="_blank" rel="noopener">{T["download"]}'
                   f'<small>v{esc(cfg["version"])} · {esc(size)} MB</small></a>'
                   f'<a class="btn" href="{esc(cfg["github"])}" target="_blank" rel="noopener">{T["source"]}</a>')
        else:
            cta = f'<span class="btn soon">{T["soon"]}</span>'   # до выпуска кода нет — кнопки «Исходный код» тоже нет
        # 18.11: кнопка в шапке, как у Unbound: до выпуска — «Скоро», после — «Скачать»
        cta_mini = (f'<a class="dl-mini" href="{esc(cfg["download"])}" target="_blank" rel="noopener">{plain(T["download"])}</a>' if released
                    else f'<span class="dl-mini soon">{plain(T["soon"])}</span>')

        # 18.11: плитки под кнопками (только те, у кого есть ссылка в sajt.txt), ролик или скрин справа, раздел скринов
        tiles = [("guide", T["guide"], "UA · EN"), ("nfsmods", "NFSMods", "nfsmods.xyz"),
                 ("nfsaddons", "NFSAddons", "nfsaddons.com"), ("nexus", "Nexus Mods", "nexusmods.com")]
        tiles = [f'<a class="btn" href="{esc(cfg[k])}" target="_blank" rel="noopener"><span>{n}</span><small>{s}</small></a>'
                 for k, n, s in tiles if cfg.get(k)]
        more = f'<div class="cta-more">{"".join(tiles)}</div>' if tiles else ""

        special = {
            "more": more, "cta_mini": cta_mini,
            "hp_st": "ready" if released else "soon", "hp_st_txt": T["hubReady"] if released else T["hubSoon"],
            "ticker": esc(TICKER * 12), "hubTicker": esc(f"NFS OWN MUSIC → {plain(T['hubStrip'])} / " * 12),
            "lang": HTML_LANG.get(L, L), "code": L, "cls": "cjk" if L in CJK else "", "rel": rel, "home": href_to(L),
            "head": "\n".join(head), "langs": langs_nav, "cur_label": cur_label, "cta": cta,
            "hub_href": esc(cfg["hub"].rstrip("/") + "/" + path_of(L)),
            "unbound_href": esc(cfg["unbound"].rstrip("/") + "/" + path_of(L)),
            "heat_href": esc(cfg["heat"].rstrip("/") + "/" + path_of(L)),
            "pages_json": json.dumps(pages, ensure_ascii=False).replace("</", "<\\/"),
        }

        def fill(m):
            kind, key, attr = m.group(1), m.group(2), m.group(3)
            if kind == "!":
                if key not in special:
                    fail(f"shablon.html: неизвестное {{{{!{key}}}}}")
                return special[key]
            if kind == "@":
                if key not in cfg:
                    fail(f"shablon.html: {{{{@{key}}}}} — нет такого ключа в sajt.txt")
                return esc(cfg[key])
            v = T[key]
            return esc(plain(v)) if attr else v
        page = re.sub(r"\{\{([!@]?)([\w .-]+?)(\|attr)?\}\}", fill, template)
        if "{{" in page:
            fail(f"{L}: в странице остались {{{{...}}}} — проверь shablon.html")
        dest = OUT / path_of(L) / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        page = page.replace("▶", "▶︎")   # 18.11: ▶ на iPhone рисовался смайликом — FE0E = «рисуй как текст»
        dest.write_text(page, encoding="utf-8")
        print(f"  {L:3} -> gotovo/{path_of(L)}index.html   «{title}»")

    # --- sitemap.xml (отдать в Google Search Console / Bing Webmaster) ---
    xdef = cfg.get("x_default", main_lang)
    rows = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for L in langs:
        rows.append(f"  <url>\n    <loc>{esc(url_of(L))}</loc>\n    <lastmod>{today}</lastmod>")
        rows += [f'    <xhtml:link rel="alternate" hreflang="{X}" href="{esc(url_of(X))}"/>' for X in langs]
        rows.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{esc(url_of(xdef))}"/>')
        rows.append("  </url>")
    rows.append("</urlset>")
    (OUT / "sitemap.xml").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print("  sitemap.xml   (robots.txt не нужен: для адреса с /HotPursuitSoundtrack/ поисковики его не читают)")

    seen = set()
    for w in warnings:
        if w not in seen:
            seen.add(w)
            print("  ! " + w)
    print(f"Готово: {len(langs)} страниц, версия {cfg['version']}, " + ("выпущена" if released else "«Скоро» (released = no)")
          + f". Папка: {OUT}")
    return cfg


def prosmotr():
    import functools
    import http.server
    import webbrowser
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler)
    print(f"Просмотр: http://localhost:{PORT}/  (закрой это окно — просмотр остановится)")
    webbrowser.open(f"http://localhost:{PORT}/")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


def opublikovat(cfg):
    if not (OUT / ".git").exists():
        fail("gotovo/ не подключена к GitHub (нет .git) — попроси Claude подключить ветку gh-pages")

    def git(where, *args, check=True):
        r = subprocess.run(["git", "-C", str(where), *args], capture_output=True, text=True, encoding="utf-8")
        if check and r.returncode != 0:
            fail("git " + " ".join(args) + "\n" + (r.stderr or r.stdout))
        return r
    # 1) исходник сайта (только папка site, код программы не трогаем) -> main
    git(ROOT, "add", "-A", ".")
    if git(ROOT, "diff", "--cached", "--quiet", "--", ".", check=False).returncode:
        git(ROOT, "commit", "-q", "-m", "Site source update", "--", ".")
        git(ROOT, "push", "-q", "origin", "HEAD:main")
        print("Исходник сайта -> GitHub (main)")
    # 2) готовый сайт -> gh-pages
    git(OUT, "add", "-A")
    if not git(OUT, "status", "--porcelain").stdout.strip():
        print("Сайт не изменился — на GitHub отправлять нечего.")
        return
    git(OUT, "commit", "-q", "-m", f"Site update (v{cfg['version']})")
    git(OUT, "push", "-q", "origin", "gh-pages")
    print("Отправлено на GitHub. Сайт обновится через 1-2 минуты: " + cfg["base_url"])


if __name__ == "__main__":
    c = main()
    if "--prosmotr" in sys.argv:
        prosmotr()
    elif "--opublikovat" in sys.argv:
        opublikovat(c)
