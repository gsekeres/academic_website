# Gabe Sekeres' Academic Website

This is a buildless static website. There is no Hugo build step and no theme dependency.

## Structure

- `site/index.html`: home page
- `site/papers/`: paper index and individual paper pages
- `site/resources/`: resource index and individual resource pages
- `site/assets/`: images, PDFs, CV files, favicon files, and CSS

## Local Preview

From the repository root:

```sh
python3 -m http.server 8000 --directory site
```

Then open:

```text
http://localhost:8000/
```

You can also open `site/index.html` directly in a browser because all internal links are relative.

## Deployment

Netlify publishes the `site/` directory directly. The `netlify.toml` file intentionally has an empty build command.
