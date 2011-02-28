__author__ = "Ben Homnick <bhomnick@gmail.com>"

from django.conf.urls.defaults import *

urlpatterns = patterns('follow.views',
	url(r'^(?P<action>follow|unfollow)/(?P<content_type_id>\w+)' \
		r'/(?P<object_id>\w+)/$', 'process', name="follow_process"
	),
)