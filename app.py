from flask import Flask, render_template, request, g, Response
import markdown
import frontmatter
import logging

app = Flask(__name__, static_folder='assets', static_url_path='/assets')
default_language = 'it'

def get_posts():
    # Read from the pages directory for markdown files
    import os
    pages_dir = 'pages'
    pages = []
    if not os.path.exists(pages_dir):
        return pages
    for filename in os.listdir(pages_dir):
        if filename.endswith('.md'):
            pages.append(filename[:-3])  # Remove .md extension
    return pages

@app.route('/')
def hello_world():
    posts = get_posts()
    page = dict(
        title='Home',
        content=''
    )
    # Return a list of available posts reading markdown files from the pages directory
    # Provide every page as an excerpt reading from the excerpt meta field and provide a linnk to the full page
    # Return a message if no pages are available
    if not posts:
        page['content'] = '<h1>No pages available</h1>'
    else:
        for post in posts:
            post_content = frontmatter.load(f'pages/{post}.md')
            post_id = markdown.markdown(str(post_content['id'])) if 'id' in post_content else ''
            if not post_id:
                continue
            post_title = markdown.markdown(post_content['title']) if 'title' in post_content else ''
            post_excerpt = markdown.markdown(post_content['excerpt']) if 'excerpt' in post_content else ''
            page['content'] += f'<h2>{post_title}</h2><div>{post_excerpt}</div><a href="/post/{post}">Read more</a>'
        return render_template('base.html', page=page)

@app.route('/post/<string:post_name>')
def show_page(post_name):
    import os
    from flask import abort
    pages_dir = 'pages'
    file_path = os.path.join(pages_dir, f'{post_name}.md')
    if not os.path.exists(file_path):
        abort(404)
    with open(file_path, 'r') as file:
        content = frontmatter.load(file)
        post = {
            'content': markdown.markdown(content.content), 
            'title': post_name
        }
    # Simple rendering of markdown content as converted HTML
    return render_template('post.html', post=post)

@app.route('/sitemap.xml')
def sitemap():
    # Return the existing sitemap.xml file from the root folder
    return Response(open('sitemap.xml').read(), mimetype='application/xml')
