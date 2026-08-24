# AGENTS.md

## Project Overview

This is a personal blog/website built with **Jekyll** using the [Chirpy](https://github.com/cotes2020/jekyll-theme-chirpy) theme (version ~> 7.6). The site is named **RoooyHe** and is configured for Chinese (`zh-CN`). It is deployed on **GitHub Pages**.

The project follows the Chirpy Starter template structure. The site owner's information is configured in `_config.yml` (name: RoooyHe, email: roooyhe@163.com). The repository also uses a git submodule (`assets/lib`) to reference the Chirpy static assets.

## Technology Stack

- **Static Site Generator**: Jekyll
- **Theme**: jekyll-theme-chirpy (~> 7.6)
- **Ruby Version**: 3.4 (as specified in GitHub Actions)
- **Dependency Management**: Bundler
- **Hosting**: GitHub Pages
- **CI/CD**: GitHub Actions (`pages-deploy.yml`)
- **HTML Validation**: html-proofer (~> 5.0)

## Project Structure

```
.
├── _config.yml            # Main site configuration
├── _data/                 # Site-wide data files
│   ├── contact.yml        # Contact/social links
│   └── share.yml          # Social sharing platforms
├── _plugins/              # Custom Jekyll plugins
│   └── posts-lastmod-hook.rb  # Git-based last modification date hook
├── _posts/                # Blog posts (Markdown)
│   └── .placeholder       # Placeholder to keep directory
├── _tabs/                 # Custom navigation tabs
│   ├── about.md           # About page
│   ├── archives.md        # Archives page
│   ├── categories.md      # Categories page
│   └── tags.md            # Tags page
├── _sass/                 # Custom Sass styles (vendored by theme)
├── assets/                # Static assets
│   ├── img/               # Images (favicons, etc.)
│   └── lib/               # Third-party libraries (git submodule)
├── tools/                 # Development helper scripts
│   ├── run.sh             # Local dev server launcher
│   └── test.sh            # Build and test script
├── index.html             # Home page (layout: home)
├── Gemfile                # Ruby gem dependencies
├── .github/workflows/     # CI/CD workflows
│   └── pages-deploy.yml   # GitHub Pages deployment workflow
├── .editorconfig          # Editor code style settings
├── .gitmodules            # Git submodule definitions
├── .nojekyll              # Jekyll processing flag
└── .gitignore             # Git ignore rules
```

## Build and Test Commands

### Local Development

```bash
# Start local Jekyll server with live reload
bash tools/run.sh

# Start in production mode
bash tools/run.sh --production

# Start on a specific host
bash tools/run.sh --host 0.0.0.0
```

### Build and Test

```bash
# Build the site and run html-proofer
bash tools/test.sh

# Build with custom config
bash tools/test.sh --config "_config.yml,_config_dev.yml"

# Build only
JEKYLL_ENV=production bundle exec jekyll build -d "_site"

# Serve only
bundle exec jekyll serve -l
```

### CI/CD

The GitHub Actions workflow (`.github/workflows/pages-deploy.yml`) automatically builds and deploys the site to GitHub Pages when code is pushed to `main` or `master` branches. The workflow:
1. Checks out the repository
2. Sets up Ruby 3.4 with Bundler cache
3. Builds the Jekyll site in production mode
4. Runs html-proofer (external URLs disabled)
5. Uploads the `_site` artifact
6. Deploys to GitHub Pages

## Code Style Guidelines

- **Indentation**: 2 spaces, no tabs
- **Line Endings**: LF (Unix-style)
- **Encoding**: UTF-8
- **Trailing Whitespace**: Trimmed (except in Markdown files)
- **Final Newline**: Required at end of files
- **Quote Style**:
  - JavaScript/CSS/SCSS: single quotes (`'`)
  - YAML: double quotes (`"`)

## Testing

- **HTML Validation**: `html-proofer` (~> 5.0) is used in the test workflow.
- The test command disables external URL checks and ignores localhost URLs.
- Tests are run both locally via `tools/test.sh` and in CI via GitHub Actions.

## Plugin

`_plugins/posts-lastmod-hook.rb` uses `git` commands to set the `last_modified_at` metadata on posts based on their commit history. This requires the post files to be tracked by git with multiple commits.

## Data Files

- `_data/contact.yml`: Configures contact/social links (GitHub, Twitter/X, email, RSS, etc.).
- `_data/share.yml`: Configures social sharing buttons at the bottom of posts.

## Custom Tabs

Custom pages are defined in `_tabs/` with YAML front matter specifying:
- `layout`: The layout template
- `icon`: FontAwesome icon class
- `order`: Display order in navigation

## Security Considerations

- The site does not include any secrets or environment variables in the repository.
- GitHub Actions uses `permissions: contents: read, pages: write, id-token: write` following the principle of least privilege.
- External URL checks are disabled in html-proofer to avoid network-dependent test failures.
- The `_site` directory and bundle cache are gitignored.

## Writing Content

- New blog posts should be placed in `_posts/` following the naming convention `YEAR-MONTH-DAY-title.md`.
- Posts require YAML front matter. Default post settings (comments, TOC, permalink) are defined in `_config.yml` under `defaults`.
- The site uses `kramdown` with `rouge` for syntax highlighting.
- Front matter options include `last_modified_at` (can be set manually or by the git hook plugin).

## Deployment

- **Target**: GitHub Pages
- **Trigger**: Push to `main` or `master` branches, or manual `workflow_dispatch`
- **Branch**: The workflow builds and deploys the static site artifact. No repository settings branch push is configured here; GitHub Pages artifact deployment is handled by `actions/deploy-pages@v5`.
