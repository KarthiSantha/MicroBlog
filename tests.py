from flask import create_app,db
from app.models import User,Posts
from hashlib import md5
from datetime import datetime,timedelta

class UserModelCase(unittest.TestCase):
	def setUp(self):
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
		db.create_all()

	def teardown(self):
		db.session.remove()
		db.drop_all()

	def test_password_hashing():
		u = User(username = 'santha')
		u.set_password('cat')
		self.assertFalse(u.check_password('dog'))
		self.assertTrue(u.check_password('cat'))

		def test_avatar(self):
			u = User(username = 'john',email = 'john@gmail.com')
			digest = md5(u.email.lower().encode('utf-8')).hexdigest()
			check = 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size = 128)
			self.assertEqual(u.avatar(128),check)

		def test_follow(self):
			u1 = User(username = 'susan',email ='susan@gmail.com')
			u2 = User(username = 'john',email = 'john@gmail.com')
			db.session.add(u1)
			db.session.add(u2)
			db.session.commit()
			self.assertEqual(u1.followed.all(),[])
			self.assertEqual(u2.followed.all(),[])

			u1.follow(u2)
			db.session.commit()
			self.assertTrue(u1.is_following(u2))
			self.assertEqual(u1.followed.count(),1)
			self.assertEqual(u1.followed.first().username,'john')
			self.assertEqual(u2.followers.count(),1)
			self.assertEqual(u2.folllowers.first().username,'susan')

			u1.unfollow(u2)
			db.session.commit()
			self.assertFalse(u1.is_following(u2))
			self.assertEqual(u1.followed.count(),0)
			self.assertEqual(u2.followers.count(),0)

		def test_follow_posts(self):
			u1 = User(username = 'susan',email ='susan@gmail.com')
			u2 = User(username = 'john',email = 'john@gmail.com')
			u3 = User(username = 'mary',email ='mary@gmail.com')
			u4 = User(username = 'david',email = 'david@gmail.com')
			db.session.add_all([u1,u2,u3,u4])

			now = datetime.utcnow()
			p1 = Posts(body = 'post from susan',author = u1,timestamp = now + timedelta(seconds = 1))
			p2 = Posts(body = 'post from john',author = u2,timestamp = now + timedelta(seconds = 4))
			p3 = Posts(body = 'post from mary',author = u3,timestamp = now + timedelta(seconds = 8))
			p4 = Posts(body = 'post from david',author = u4,timestamp = now + timedelta(seconds = 10))
			db.session.add_all([p1,p2,p3,p4])
			db.session.commit()

			u1.follow(u2)
			u1.follow(u4)
			u2.follow(u3)
			u3.follow(u4)
			db.session.commit()

			f1 = u1.followed_posts().all()
			f2 = u2.followed_posts().all()
			f3 = u3.followed_posts().all()
			f4 = u4.followed_posts().all()
			self.assertEqual(f1,[p2,p4,p1])
			self.assertEqual(f2,[p3,p2])
			self.assertEqual(f3,[p4,p3])
			self.assertEqual(f4,[p4])

if __name__ == '__main__':
	unittest.main(verbosity = 2)








			
			
