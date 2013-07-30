import os
import webapp2
import jinja2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), 
                               autoescape=True)
def blog_key(name='default'):
    return db.Key.from_path('blogs', name)

class Post(db.Model):
    title = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class BlogFrontPage(Handler):
    def render_front(self, title="", content=""):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")

        self.render("blog_front.html", title=title, 
                                       content=content, 
                                       posts = posts)

    def get(self):
        self.render_front()

class BlogNewPost(Handler):
    def render_newpost(self,title="",content="",error=""):
        self.render("blog_newpost.html", title=title, content=content, error=error)
    def get(self):
        self.render_newpost()
    def post(self):
        title = self.request.get('subject')
        content = self.request.get('content')

        if title and content:
            p= Post(title = title, content = content)
            p_key = p.put()
            self.redirect("/blog/%d"%p_key.id())
        else:
            error = "we need both a subject and some content!"
            self.render_newpost(title=title, error = error)

class PostPermalink(BlogFrontPage):
    def get(self, post_id):
        post = Post.get_by_id(int(post_id))
        self.render("blog_front.html", posts=[post])

app = webapp2.WSGIApplication([('/blog', BlogFrontPage),
                               ('/blog/newpost', BlogNewPost),
                               (r'/blog/(\d+)', PostPermalink)
                               ], debug=True)