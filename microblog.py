from app import create_app, db, cli
from app.models import User, Post, Message, Notification, Task
from flaskext.markdown import Markdown

app = create_app()
cli.register(app)
Markdown(app)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Message': Message,
            'Notification': Notification, 'Task': Task}
