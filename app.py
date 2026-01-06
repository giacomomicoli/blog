from flask import Flask, render_template, request, g, Response
import markdown
import frontmatter
import logging
import os

app = Flask(__name__, static_folder='assets', static_url_path='/assets')
default_language = 'en'
# Basic logging configuration
logging.basicConfig(level=logging.INFO)
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

@app.route('/sitemap.xml')
def sitemap():
    # Return the existing sitemap.xml file from the root folder
    return Response(open('sitemap.xml').read(), mimetype='application/xml')
