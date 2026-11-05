# FRONTIER / AI Observatory

Free, source-grounded AI evolution and control-evidence dashboard.

**No Lovable, Node installation, npm, JavaScript server, database subscription or API key is needed to use the published site.**

## One-time publishing step

The code is already in the public repository jmed001/Websites.

1. Open https://github.com/jmed001/Websites/settings/pages
2. Under **Build and deployment → Source**, choose **GitHub Actions**.
3. Open https://github.com/jmed001/Websites/actions/workflows/ai-observatory.yml and use **Run workflow** on the main branch.
4. After GitHub shows a successful deployment, the website should be accessible at https://jmed001.github.io/Websites/ unless a custom domain has been configured.

**Publishing makes this dashboard public.** Never put passwords, private records or financial/medical information in these files.

## Dashboard features

- Executive overview with capability comparisons, source evidence, and transparent trend-availability labels.
- Capabilities & velocity with interactive developer and model filters, sortable ECI comparisons, CSV export, and credible intervals.
- Autonomy & RSI with METR time-horizon limitations and a Recursive Self-Improvement research evidence ladder.
- Safety & control with documented incidents clearly separated from controlled evaluations.
- Scenarios & sources with adjustable hypothetical capability growth and original sources.

RSI = **Recursive Self-Improvement**, NOT Rogue Severity Index. No fabricated risk scores or historical trend points.

## Updates

The workflow at .github/workflows/ai-observatory.yml executes each day and can also be run manually. It validates the incoming Epoch ECI CSV, updates model comparisons and legitimate release-date history only if the schema and rows pass strict checks, and publishes the site. If validation fails, the last valid observations are preserved and the import error is recorded.

**The ECI CSV importer is written but has not yet had a verified successful live run.** Until verified, the initial comparison remains a dated curated snapshot. METR and safety evidence are curated and do not automatically refresh yet.

Source snapshot: ai-observatory/data/snapshot.json.
Importer: ai-observatory/scripts/update_epoch.py.
Tests: ai-observatory/tests/test_update_epoch.py.
Website: ai-observatory/index.html, styles.css and app.js.

## Running costs and reliability

GitHub Pages and standard GitHub Actions can be used without a paid plan for a public repository, subject to GitHub's usage limits. Scheduled workflow runs can be delayed or disabled after prolonged inactivity. Chart.js loads from a public CDN; the remaining site is ordinary static files. No cloud database is currently needed.

## Later improvements

Verify and refine the official ECI CSV adapter; add a fully publisher-dated capability history; connect any maintained METR dataset; implement a source-review queue for ongoing safety research; preserve snapshots for longitudinal trend analyses.