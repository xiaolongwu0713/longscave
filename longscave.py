from app import create_app, db, cli
from app.models import User, Role, Post, Message, Notification, Task, MessageToMe
from flaskext.markdown import Markdown
from datetime import timedelta
from app.alipay.routes import init_alipay_cfg, qr_img_generator, qr_generator, cancel_order, query_order
from flask_user import UserManager


app = create_app()
cli.register(app)
Markdown(app)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
app.config['CKEDITOR_FILE_UPLOADER'] = 'main.upload'
#enable blow will use flask_user to do auth work instead of flask_login
#user_manager = UserManager(app, db, User)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Role': Role, 'Post': Post, 'Message': Message, 'Messagetome': MessageToMe,
            'Notification': Notification, 'Task': Task, 'init_alipay_cfg': init_alipay_cfg,
            'qr_img_generator': qr_img_generator, 'qr_generator': qr_generator,
            'cancel_order': cancel_order, 'query_order': query_order}


'''
1, test generating alipay qr-code image
qr_generator('test', 'product-name-something', amount-of-money)
qr_generator('prd', 'product-name-something', amount-of-money)
2, cancel alipay order
cancel a test env order: cancel_order('testproduct1587008785', 'test')
cancel a prd env order: cancel_order('testproduct1587008785', 'prd')
'''