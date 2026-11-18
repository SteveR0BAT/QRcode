# Holden Caulfield Literary Atlas — GitHub Pages deployment

This repository contains an automated publisher for the uploaded Next.js project.

## One-time setup

1. Upload **`holden-caulfield-literary-atlas.zip`** to the root of this repository and commit it to `main`.
2. Open **Settings → Pages** and select **GitHub Actions** as the deployment source.
3. Open **Actions → Publish Holden Caulfield Literary Atlas** and confirm the workflow completed.

The workflow automatically extracts the ZIP, applies static-hosting adjustments, builds the site, and deploys it to GitHub Pages. Replacing the ZIP on `main` triggers a new deployment.

## Website URL

https://stever0bat.github.io/QRcode/

## Hosting notes

The original project uses Next.js and PostgreSQL APIs. GitHub Pages only serves static files, so the automation pre-renders the home page and all location dossiers, generates GeoJSON downloads in the browser, and stores reader notes in each visitor's own browser storage. Notes are not shared between visitors.

The uploaded archive does not include the local archival photographs referenced by the source data. The build supplies a labelled placeholder for missing images. The atlas data, interactive Leaflet/OpenStreetMap map, and location pages are retained.
