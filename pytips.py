from app import create_app, db
from app.models import User, HashTag, Tip, Like, Role, Permissions, Message

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Tip': Tip, 'Hashtag': HashTag, 'Like': Like,
            'Role': Role, 'Permissions': Permissions, 'Message': Message}
