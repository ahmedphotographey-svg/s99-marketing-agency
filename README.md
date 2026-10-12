# S99 Marketing — Website

Static bilingual (English / Arabic) website for S99 Marketing Agency.

## Structure
- `content.py` — all page text (EN + AR)
- `src/data/work.json` — reels, films, social posts, production work, influencers
- `src/assets/` — CSS, JS, fonts, images, videos
- `build.py` — generates the site into `dist/`
- `dist/` — the ready-to-upload website (already built)

## Deploy
**Any hosting (cPanel / Hostinger / etc.):** upload the contents of `dist/` to `public_html`.

**Cloudflare Pages / Netlify / Vercel (connected to this repo):**
- Build command: `python3 build.py`
- Output directory: `dist`

Before going live, set `SITE_URL` in `build.py` to the real domain and rebuild.

See `README-AR.md` for the Arabic guide.
