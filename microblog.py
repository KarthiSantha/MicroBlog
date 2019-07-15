from app import create_app,db
from app.models import Posts,User

@app.shell_context_processor
def make_shell_context():
	return {'db':db,'User':User,'Posts':Posts}