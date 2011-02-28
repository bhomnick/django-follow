""" Follow module unit tests """

__author__ = "Ben Homnick <bhomnick@gmail.com>"

from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.template import Context, Template
from django.test import TestCase
from django.test.client import Client

from follow.models import Follow, user_model, AnonymousUserNotAllowed

BAD_MONGODB_GUID = "000000000000000000000000"


class TestModel(models.Model):
	name = models.CharField(max_length=20)
	
	def __unicode__(self):
		return self.name


class ModelsTest(TestCase):
	""" testing models.py """
	
	def setUp(self):
		self.user1 = user_model.objects.create_user(username="test",
			email="test@test.com", password="test")
		self.obj1 = TestModel.objects.create(name="obj1")
		self.obj2 = TestModel.objects.create(name="obj2")
		self.follow1 = Follow.objects.create(user=self.user1,
			content_object=self.obj1)
		self.ctype = ContentType.objects.get_for_model(TestModel)

	def tearDown(self):
		TestModel.objects.all().delete()
		user_model.objects.all().delete()
	
	def test_is_following(self):
		self.assertTrue(Follow.objects.is_following(self.user1, self.obj1))
		self.assertFalse(Follow.objects.is_following(self.user1, self.obj2))

	def test_anonymous_follow(self):
		self.assertRaises(AnonymousUserNotAllowed,
			Follow.objects.follow, AnonymousUser(), self.obj2)
			
	def test_follow(self):
		Follow.objects.follow(self.user1, self.obj2)
		self.assertTrue(Follow.objects.is_following(self.user1, self.obj2))
		Follow.objects.follow(self.user1, self.obj1)
		self.assertTrue(Follow.objects.is_following(self.user1, self.obj1))
	
	def test_unfollow(self):
		Follow.objects.unfollow(self.user1, self.obj1)
		self.assertFalse(Follow.objects.is_following(self.user1, self.obj1))
		Follow.objects.unfollow(self.user1, self.obj2)
		self.assertFalse(Follow.objects.is_following(self.user1, self.obj2))
		

class ClientCase(TestCase):
	""" Base test case with request client """
	urls = 'follow.urls'
	
	def setUp(self):
		self.user1 = user_model.objects.create_user(username="test",
			email="test@test.com", password="test")
		self.obj1 = TestModel.objects.create(name="obj1")
		self.ctype = ContentType.objects.get_for_model(TestModel)
		self.client = Client()
		self.get_url = lambda a, cid, oid: reverse(
			'follow.views.process',
			args=(a, cid, oid),
		)
		
	def tearDown(self):
		TestModel.objects.all().delete()
		user_model.objects.all().delete()


class TagsTest(ClientCase):
	""" testing templatetags/follow.py """
	
	def get_template(self, args):
		return "{%% load follow_tags %%}{%% get_follow_process_url %s %%}" % args
	
	def test_follow(self):
		url = self.get_url("follow", self.ctype.id, self.obj1.pk)
		t = Template(self.get_template('"follow" obj'))
		c = Context({
			'obj': self.obj1,
		})
		self.assertEqual(url, t.render(c))
	
	def test_unfollow(self):
		url = self.get_url("unfollow", self.ctype.id, self.obj1.pk)
		t = Template(self.get_template('"unfollow" obj'))
		c = Context({
			'obj': self.obj1,
		})
		self.assertEqual(url, t.render(c))
	

class ViewsTest(ClientCase):
	""" testing views.py """
	
	def test_basic(self):
		self.client.login(username="test", password="test")
		response = self.client.get(
			self.get_url("follow", self.ctype.pk, self.obj1.pk))
		self.assertEquals(response.status_code, 200)
		self.assertTrue(Follow.objects.is_following(self.user1, self.obj1))

		response = self.client.get(
			self.get_url("unfollow", self.ctype.pk, self.obj1.pk))
		self.assertEquals(response.status_code, 200)
		self.assertFalse(Follow.objects.is_following(self.user1, self.obj1))

	def test_404(self):
		self.client.login(username="test", password="test")
		response = self.client.get(
			self.get_url("follow", self.ctype.pk, BAD_MONGODB_GUID))
		self.assertTrue(response.status_code, 404)
	
		response = self.client.get(
			self.get_url("unfollow", BAD_MONGODB_GUID, self.obj1.pk))
		self.assertTrue(response.status_code, 404)

	def test_redirect(self):
		self.client.login(username="test", password="test")
		response = self.client.get("%s?next=%s" % \
			(self.get_url("follow", self.ctype.id, self.obj1.pk), "/"))
		self.assertTrue(Follow.objects.is_following(self.user1, self.obj1))
		self.assertEquals(response.status_code, 302)
	
	def test_ajax(self):
		self.client.login(username="test", password="test")
		response = self.client.get("%s?next=%s" % 
			(self.get_url("follow", self.ctype.pk, self.obj1.pk), "/"), 
			HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertTrue(Follow.objects.is_following(self.user1, self.obj1))
		self.assertEquals(response.status_code, 200)
