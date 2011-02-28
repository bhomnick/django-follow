__author__ = "Ben Homnick <bhomnick@gmail.com>"

import json

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404

from follow.models import Follow

@login_required
def process(request, action, content_type_id, object_id, redirect_field='next'):
	""" Processes a follow or unfollow request.
	
	Args:
		action: The action to take, either "follow" or "unfollow"
		content_type_id: ContentType id of the object to follow
		object_id: Id of the object to follow
		redirect_field: (optional) Name of the GET parameter containing
			the URL to redirect to after processing this request.  Not
			used in AJAX requests.
	
	Returns:
		HttpResponseRedirect to whatever URL was passed in from redirect_field.
		For AJAX requests returns HttpResponse("1") if successful.
	"""
	
	content_type = get_object_or_404(ContentType, pk=content_type_id)
	content_object = get_object_or_404(content_type.model_class(),
		pk=object_id)	
	getattr(Follow.objects, action)(request.user, content_object)
	if request.GET.get(redirect_field) and not request.is_ajax():
		return HttpResponseRedirect(request.GET[redirect_field])
	return HttpResponse("1")
