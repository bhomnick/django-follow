__author__ = "Ben Homnick <bhomnick@gmail.com>"

from django.db import models

import datetime

from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.db import models

user_model = getattr(settings, 'CUSTOM_USER_MODEL', User)


class AnonymousUserNotAllowed(Exception):
	pass


class FollowManager(models.Manager):

	def follow(self, user, content_object):
		""" Creates a follow relationship. 
		
		Args:
			user: instance of user_model
			content_object: any DB model instance
		
		Returns:
			True if relationship created or already exists.
		
		Raises:
			AnonymousUserNotAllowed: Anonymous users can't follow.
		"""
		if user.is_anonymous():
			raise AnonymousUserNotAllowed("Anonymous users aren't allowed "
				"to follow.")
		if not self.is_following(user, content_object):
			self.create(user=user, content_object=content_object)
		return True
	
	def unfollow(self, user, content_object):
		""" Removes a follow relationship.
		
		Args:
			user: instance of user_model
			content_object: any DB model instance
		
		Returns:
			True if follow relationship removed or never existed.
		"""
		content_type = ContentType.objects.get_for_model(content_object)
		if self.is_following(user, content_object):
			like = self.get(user=user, content_type=content_type,
				object_id=content_object.id)
			like.delete()
		return True
	
	def is_following(self, user, content_object):
		""" Check if a user is already following an object.
		
		Args:
			user: instance of user_model
			content_object: any DB model instance
			
		Returns:
			True if user following content_object, False otherwise.
		"""
		content_type = ContentType.objects.get_for_model(content_object)
		return self.filter(user=user, content_type=content_type,
			object_id=content_object.id).count() > 0
		
	def get_followed_objects(self, user):
		""" Get all objects a user is following.
		
		Args:
			user: instance of user_model
	
		Returns:
			Set of all objects user is currently following.
		"""
		return set([obj.content_object for obj in self.filter(user=user)])
		

class Follow(models.Model):
	user = models.ForeignKey(user_model)
	content_type = models.ForeignKey(ContentType)
	object_id = models.CharField(max_length=32) # CharField so MongoDB is happy
	content_object = GenericForeignKey()
	created = models.DateTimeField(default=datetime.datetime.now)
	
	objects = FollowManager()
	
	class Meta:
		ordering = ['-created']
		# TODO: figure out why unique_together makes MongoDB explode
		#unique_together = ('user', 'content_type', 'object_id')
	
	def __unicode__(self):
		return "%s follows %s" % (self.user, self.content_object)
	