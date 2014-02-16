from django.core.urlresolvers import resolve
from django.test import TestCase
from story.views import FrontpageView


class StoryViewsTestCase(TestCase):

	def test_root_url_resolves_to_home_page_view(self):
		found = resolve('/')
		self.assertEqual(found.func, FrontpageView.as_view())
