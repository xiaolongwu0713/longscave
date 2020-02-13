from app import create_app, db, cli
from app.models import User, Post, Message, Notification, Task, MessageToMe
from flaskext.markdown import Markdown
from datetime import timedelta

app = create_app()
cli.register(app)
Markdown(app)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
app.config['CKEDITOR_FILE_UPLOADER'] = 'main.upload'

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Message': Message, 'Messagetome': MessageToMe,
            'Notification': Notification, 'Task': Task}
