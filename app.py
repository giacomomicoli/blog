from flask import Flask, render_template, make_response, request, g, Response
from flask_caching import Cache
import markdown
import frontmatter
import logging
import os

app = Flask(__name__, static_folder='assets', static_url_path='/assets')
default_language = 'en'
# Basic logging configuration
logging.basicConfig(level=logging.INFO)
# Cache configuration
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})
config = {
   'post_dir': 'post'
}
site = {
    'name': 'YARB',
    'url': os.getenv('SITE_URL'),
}
def get_posts():
    # Read from the pages directory for markdown files
    posts_dir = config.get('post_dir')
    posts = []
    if not os.path.exists(posts_dir):
        return posts
    for filename in os.listdir(posts_dir):
        if filename.endswith('.md'):
            posts.append(filename[:-3])  # Remove .md extension
            logging.info(f'Found post: {filename}')
        logging.info(f'Ignoring file: {filename}')
    return posts

@app.route('/', methods=['GET'])
def index():
    filenames = get_posts()
    posts = []
    for post in filenames:
        filepath = os.path.join(config.get('post_dir'), f"{post}.md")
        if not os.path.exists(filepath):
            continue
        with open(filepath, 'r') as p:
            post = frontmatter.load(p)
            metadata = post.metadata
            content = markdown.markdown(post.content)
            posts.append({
                'metadata': metadata,
                'content': content
            })

    return render_template('index.html', posts=posts, site_url=site['url'])

@app.route('/post/<string:slug>', methods=['GET'])
def post_detail(slug):
    from flask import abort
    filepath = os.path.join(config.get('post_dir'), f"{slug}.md")
    if not os.path.exists(filepath):
        abort(404)
    with open(filepath, 'r') as p:
        post = frontmatter.load(p)
        metadata = post.metadata
        content = markdown.markdown(post.content)
        post = {
            'metadata': {
                **metadata,
                'image': f"{os.getenv('BUCKET_ENDPOINT')}/{metadata.get('image')}" if metadata.get('image') else None
            },
            'content': content
        }
    return render_template('post.html', post=post)

@app.route('/sitemap.xml', methods=['GET'])
@cache.cached(timeout=3600)
def sitemap():
    posts_path = get_posts()
    posts = []
    bucket_endpoint = os.getenv('BUCKET_ENDPOINT')
    for post in posts_path:
        filepath = os.path.join(config.get('post_dir'), f"{post}.md")
        if not os.path.exists(filepath):
            continue
        with open(filepath, 'r') as p:
            post = frontmatter.load(p)
            metadata = post.metadata
            image_full_url = None
            if metadata.get('image'):
                image_full_url = f"{bucket_endpoint}/{metadata.get('image')}"
            posts.append({
                'lastmod': metadata.get('updated_at', metadata.get('created_at')),
                'slug': metadata.get('slug'),
                'image': image_full_url,
                'title': metadata.get('title')
            })
    sitemap_xml = render_template('sitemap_template.xml', posts=posts, site_url=site['url'])
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"

    return response

@app.route('/robots.txt', methods=['GET'])
@cache.cached(timeout=3600)
def robots():
    sitemap_url = f"{site['url']}/sitemap.xml"
    
    env = os.getenv('FLASK_ENV', 'development') 
    
    lines = []
    
    if env == 'production':
        # --- PRODUCTION RULES ---
        lines.append("User-agent: *")
        lines.append("Allow: /")
        
        # Block internal search or admin paths if you ever add them
        lines.append("Disallow: /admin/") 
        lines.append("Disallow: /search/")
        
        # Block AI Bots specifically? (Optional strategy decision)
        # lines.append("User-agent: GPTBot")
        # lines.append("Disallow: /") # Uncomment if you HATE AI scrapers (not recommended for exposure)
        
        # Point to the Sitemap
        lines.append(f"Sitemap: {sitemap_url}")
        
    else:
        # --- DEV/STAGING RULES (The Safety Net) ---
        lines.append("User-agent: *")
        lines.append("Disallow: /")
    
    response = make_response("\n".join(lines))
    response.headers["Content-Type"] = "text/plain"
    return response
