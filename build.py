"""
ElectroGame Fuengirola: static site builder.

  src/pages/<name>.html   page content; first line is a metadata comment:
      <!--META {"title": "...", "description": "...", "path": "/zona-gaming/", "nav": "zona"} -->
  src/partials/           shared pieces (icon sprite)
  src/assets/             css/, js/, img/ (copied as-is)

This script wraps every page in the shared layout (head, top bar, header,
footer) and writes the finished site to docs/ (rebuilt from scratch each time):
  docs/index.html, docs/zona-gaming/index.html, ..., docs/assets/, sitemap.xml, robots.txt
docs/ is the folder GitHub Pages publishes.

Usage:
  python build.py --preview   copy for GitHub Pages: pages carry noindex so Google
                              doesn't index it as a duplicate of electrogame.es
  python build.py             final version for the real hosting (indexable)
"""
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
OUT = ROOT / "docs"
PREVIEW = "--preview" in sys.argv[1:]
SITE = "https://www.electrogame.es"
WA_DEFAULT = "https://wa.me/34613725715"

NAV = [
    ("reparacion", "/reparacion-consolas/", "Reparación"),
    ("zona", "/zona-gaming/", "Zona gaming"),
    ("talleres", "/gamers-curiosos/", "Talleres"),
    ("nosotros", "/quienes-somos/", "Quiénes somos"),
    ("blog", "/blog/", "Blog"),
    ("contacto", "/contacto/", "Contacto"),
]
MOBILE_EXTRA = [
    ("reserva", "/reserva-espacio/", "Reservar espacio"),
    ("ubicacion", "/ubicacion/", "Cómo llegar"),
    ("tienda", "/tienda/", "Tienda y servicios"),
]

SCHEMA = {
    "@context": "https://schema.org",
    "@type": "ElectronicsStore",
    "name": "ElectroGame Fuengirola",
    "description": "Taller de reparación de consolas, mandos, gafas VR, ordenadores y equipos electrónicos en Fuengirola. Zona gaming, talleres formativos y punto GLS.",
    "url": SITE + "/",
    "telephone": "+34613725715",
    "email": "electrogamefuengirola@gmail.com",
    "image": SITE + "/assets/img/tienda-local-o5.webp",
    "logo": SITE + "/assets/img/logo-electrogame.webp",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "Área Comercial Las Palmeras, C/ Jacinto Benavente, 7, Local O-5",
        "addressLocality": "Fuengirola",
        "addressRegion": "Málaga",
        "postalCode": "29640",
        "addressCountry": "ES",
    },
    "openingHoursSpecification": [
        {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "10:00", "closes": "13:30"},
        {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "16:00", "closes": "19:30"},
        {"@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "10:00", "closes": "14:00"},
    ],
    "areaServed": ["Fuengirola", "Mijas", "Benalmádena", "Costa del Sol"],
    "sameAs": [
        "https://www.instagram.com/electrogamefuengirola",
        "https://www.tiktok.com/@electrogamefuengirola",
        "https://www.facebook.com/profile.php?id=61592217069320",
    ],
}


def esc(s):
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def head(m):
    url = SITE + m["path"]
    og_img = SITE + m.get("og_image", "/assets/img/tienda-local-o5.webp")
    preload = f'<link rel="preload" as="image" href="{m["preload"]}">\n' if m.get("preload") else ""
    schema = ""
    if m.get("schema"):
        schema = '<script type="application/ld+json">\n' + json.dumps(SCHEMA, ensure_ascii=False, indent=2) + "\n</script>\n"
    robots = '<meta name="robots" content="noindex">\n' if (m.get("noindex") or PREVIEW) else ""
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(m["title"])}</title>
<meta name="description" content="{esc(m["description"])}">
{robots}<link rel="canonical" href="{url}">
<meta property="og:type" content="{m.get("og_type", "website")}">
<meta property="og:site_name" content="ElectroGame Fuengirola">
<meta property="og:title" content="{esc(m.get("og_title", m["title"]))}">
<meta property="og:description" content="{esc(m["description"])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og_img}">
<meta property="og:locale" content="es_ES">
<meta name="theme-color" content="#0a0d18">
<link rel="icon" type="image/png" href="/assets/img/favicon.png">
{preload}<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/styles.css">
<script src="/assets/js/main.js" defer></script>
{schema}</head>"""


def header(active):
    def link(key, href, label):
        cur = ' aria-current="page"' if key == active else ""
        return f'<a href="{href}"{cur}>{label}</a>'

    desktop = "\n      ".join(link(*n) for n in NAV)
    mobile_items = [("inicio", "/", "Inicio")] + NAV[:1] + [MOBILE_EXTRA[0]] + NAV[1:] + MOBILE_EXTRA[1:]
    mobile = "\n    ".join(link(*n) for n in mobile_items)
    sprite = (SRC / "partials" / "sprite.svg").read_text(encoding="utf-8")
    return f"""<body>

{sprite}
<a class="skip" href="#main">Saltar al contenido</a>

<div class="topbar">
  <div class="wrap">
    <span class="status" id="status"><span class="dot"></span><span id="status-text">L–V 10:00–13:30 · 16:00–19:30</span></span>
    <span><a class="addr" href="/ubicacion/">Las Palmeras, Fuengirola · </a><a href="tel:+34613725715">613 725 715</a></span>
  </div>
</div>

<header class="nav" id="nav">
  <div class="wrap">
    <a href="/" class="logo" aria-label="ElectroGame Fuengirola, inicio">
      <span class="logo-mark"><img src="/assets/img/logo-electrogame.webp" alt="" width="46" height="46"></span>
      <span>ElectroGame<small>Fuengirola</small></span>
    </a>
    <nav class="menu" aria-label="Principal">
      {desktop}
    </nav>
    <div class="nav-right">
      <a class="btn btn-wa btn-sm nav-cta" data-wa href="{WA_DEFAULT}">
        <svg><use href="#i-wa"/></svg><span class="label-long">Presupuesto por WhatsApp</span><span class="label-short">WhatsApp</span>
      </a>
      <button class="menu-btn" id="menu-btn" type="button" aria-label="Abrir menú" aria-expanded="false" aria-controls="mobile-menu"><svg><use href="#i-menu"/></svg></button>
    </div>
  </div>
  <nav class="mobile-menu" id="mobile-menu" aria-label="Menú móvil">
    {mobile}
    <a class="btn btn-wa" data-wa href="{WA_DEFAULT}"><svg><use href="#i-wa"/></svg>Escribir por WhatsApp</a>
  </nav>
</header>
"""


FOOTER = f"""
<footer class="site">
  <div class="wrap">
    <div class="foot-grid">
      <div class="foot-brand">
        <a href="/" class="logo"><span class="logo-mark"><img src="/assets/img/logo-electrogame.webp" alt="" width="46" height="46" loading="lazy"></span><span>ElectroGame<small>Fuengirola</small></span></a>
        <p>Taller de reparación de consolas, mandos, gafas VR y equipos electrónicos. Zona gaming, talleres formativos y punto GLS en Fuengirola.</p>
        <div class="socials">
          <a href="https://www.instagram.com/electrogamefuengirola" target="_blank" rel="noopener" aria-label="Instagram"><svg><use href="#i-ig"/></svg></a>
          <a href="https://www.tiktok.com/@electrogamefuengirola" target="_blank" rel="noopener" aria-label="TikTok"><svg><use href="#i-tt"/></svg></a>
          <a href="https://www.facebook.com/profile.php?id=61592217069320" target="_blank" rel="noopener" aria-label="Facebook"><svg><use href="#i-fb"/></svg></a>
        </div>
      </div>
      <div>
        <h4>Servicios</h4>
        <ul>
          <li><a href="/reparacion-consolas/">Reparación de consolas y mandos</a></li>
          <li><a href="/zona-gaming/">Zona gaming</a></li>
          <li><a href="/reserva-espacio/">Reservar espacio</a></li>
          <li><a href="/gamers-curiosos/">Talleres formativos</a></li>
          <li><a href="/tienda/">Tienda y servicios</a></li>
        </ul>
      </div>
      <div>
        <h4>ElectroGame</h4>
        <ul>
          <li><a href="/quienes-somos/">Quiénes somos</a></li>
          <li><a href="/blog/">Blog</a></li>
          <li><a href="/ubicacion/">Cómo llegar</a></li>
          <li><a href="/contacto/">Contacto</a></li>
        </ul>
      </div>
      <div>
        <h4>Horario</h4>
        <ul class="hours-mini">
          <li><span>Lunes a viernes</span><span>10:00–13:30</span></li>
          <li><span></span><span>16:00–19:30</span></li>
          <li><span>Sábado</span><span>10:00–14:00</span></li>
          <li><span>Domingo</span><span>Cerrado</span></li>
        </ul>
        <ul style="margin-top:18px">
          <li><a href="tel:+34613725715">613 725 715 · móvil y WhatsApp</a></li>
          <li><a href="tel:+34951673119">951 673 119 · fijo</a></li>
          <li><a href="mailto:electrogamefuengirola@gmail.com">electrogamefuengirola@gmail.com</a></li>
        </ul>
      </div>
    </div>
    <div class="foot-bottom">
      <span>© <span id="y">{date.today().year}</span> ElectroGame Fuengirola · Área Comercial Las Palmeras, Local O-5, 29640 Fuengirola</span>
      <nav aria-label="Legal">
        <a href="/aviso-legal/">Aviso legal</a>
        <a href="/privacidad/">Privacidad</a>
      </nav>
    </div>
  </div>
</footer>

<a class="fab" data-wa href="{WA_DEFAULT}" aria-label="Escribir por WhatsApp"><svg><use href="#i-wa"/></svg></a>
</body>
</html>
"""


def relativize(html, page_path):
    """Turn root-absolute URLs (/assets/css/x.css, /zona-gaming/) into paths relative
    to the page, so the site works both on a server and opened from disk (file://).
    Folder links get an explicit index.html, which file:// needs."""
    depth = len([p for p in page_path.strip("/").split("/") if p])
    prefix = "../" * depth

    def fix(m):
        attr, url = m.group(1), m.group(2)
        if url.startswith("//"):
            return m.group(0)
        path, sep, rest = re.match(r"([^?#]*)([?#]?)(.*)", url).groups()
        path = path.lstrip("/")
        if path == "" or path.endswith("/"):
            path += "index.html"
        return f'{attr}="{prefix}{path}{sep}{rest}"'

    return re.sub(r'\b(href|src)="(/[^"]*)"', fix, html)


def build():
    # Never wipe web/ unless the sources to rebuild it are actually there
    for needed in (SRC / "pages", SRC / "assets", SRC / "partials" / "sprite.svg"):
        if not needed.exists():
            raise SystemExit(f"No encuentro {needed.relative_to(ROOT)}: no toco docs/. Revisa la carpeta src/.")
    if not any((SRC / "pages").glob("*.html")):
        raise SystemExit("src/pages/ está vacía: no toco docs/.")

    # docs/ is generated output only: start clean so deleted pages don't linger
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SRC / "assets", OUT / "assets")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")  # GitHub Pages: serve files as-is

    pages = sorted((SRC / "pages").glob("*.html"))
    sitemap = []
    for src in pages:
        text = src.read_text(encoding="utf-8")
        m = re.match(r"<!--META\s*(\{.*?\})\s*-->\s*", text, re.S)
        if not m:
            raise SystemExit(f"{src.name}: missing <!--META {{...}} --> header")
        meta = json.loads(m.group(1))
        body = text[m.end():]
        html = head(meta) + "\n" + header(meta.get("nav", "")) + '\n<main id="main">\n' + body.rstrip() + "\n</main>\n" + FOOTER
        html = relativize(html, meta["path"])
        rel = meta["path"].strip("/")
        out = OUT / rel / "index.html" if rel else OUT / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        if not meta.get("noindex"):
            sitemap.append(meta["path"])
        print(f"  {meta['path']:<34} <- src/pages/{src.name}")

    today = date.today().isoformat()
    urls = "\n".join(f"  <url><loc>{SITE}{p}</loc><lastmod>{today}</lastmod></url>" for p in sitemap)
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n',
        encoding="utf-8")
    robots = "User-agent: *\nDisallow: /\n" if PREVIEW else f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n"
    (OUT / "robots.txt").write_text(robots, encoding="utf-8")
    mode = "PREVIEW (noindex, para GitHub Pages)" if PREVIEW else "FINAL (indexable)"
    print(f"Built {len(pages)} pages + assets + sitemap.xml + robots.txt -> docs/  [{mode}]")


if __name__ == "__main__":
    build()
