# teamsummitre

Static website for **Summit Real Estate Services** — Midwest industrial real estate advisory for families, private investors, and private equity groups.

## Structure

- `index.html` — Home
- `services.html` — Services detail
- `portfolio.html` — Properties we manage
- `team.html` — Leadership
- `contact.html` — Contact form & direct lines
- `assets/` — Logo, brand stylesheet, site stylesheet

## Brand System

The site is built on the official Summit brand system:

- `assets/summit-brand.css` — design tokens (colors, type, spacing, components)
- `assets/site.css` — site-only layout (header, hero, sections, footer)
- `assets/summit-logo-*.svg` — official logos

## Local preview

```bash
# from repo root
python3 -m http.server 8000
# then open http://localhost:8000
```

## Deployment

This repo is configured for **GitHub Pages** from the `main` branch. Pushing to `main` deploys automatically.
