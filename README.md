# abdullahshahab.com

Static site, deployed by Cloudflare Pages straight from this repo (no build step on Cloudflare).

## Writing a blog post
1. Add a Markdown file to `content/posts/` (copy an existing post for the front matter:
   `title`, `slug`, `description`, `date`, `category`, `cover`, `cover_alt`; add `draft: true` to hide it).
2. Run `python3 tools/build_blog.py` (needs `pip install markdown pyyaml`).
3. Commit and push. Cloudflare publishes it within a minute.

The build regenerates `blog/`, `css/main.css`, `sitemap.xml`, `robots.txt` and `blog/feed.xml`.
