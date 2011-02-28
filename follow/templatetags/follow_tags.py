__author__ = "Ben Homnick <bhomnick@gmail.com>"

from django import template
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

register = template.Library()

def get_kwargs(content_object):
	kwargs = {
		'content_type_id': ContentType.objects.get_for_model(
			content_object).id,
		'object_id': content_object.pk,
	}
	return kwargs

@register.simple_tag
def get_follow_process_url(action, content_object):
	""" Gets the POST URL to process a follow/unfollow request.
	
	Args:
		action: Either "follow" or "unfollow"
		content_object: Object to follow
	
	Example:
		To follow an object:
		{% get_follow_process_url "follow" obj %}
		or unfollow an object:
		{% get_follow_process_url "unfollow" obj %}
	"""
	
	kwargs = get_kwargs(content_object)
	kwargs["action"] = action
	return reverse('follow.views.process', kwargs=kwargs)

