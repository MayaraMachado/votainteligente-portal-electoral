# coding=utf-8
from django.test import TestCase, override_settings
from merepresenta.match.forms import QuestionsCategoryForm
from merepresenta.match.tests.match_tests import MeRepresentaMatchBase
from django.core.urlresolvers import reverse
import json



@override_settings(ROOT_URLCONF='merepresenta.stand_alone_urls')
class QuestionCategoryForm(TestCase, MeRepresentaMatchBase):
    def setUp(self):
        super(QuestionCategoryForm, self).setUp()
        self.set_data()

    def test_instanciate_form(self):
        data = {'categories': [self.cat1.id, self.cat2.id]}
        form = QuestionsCategoryForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertIn(self.cat1, form.cleaned_data['categories'])
        self.assertIn(self.cat2, form.cleaned_data['categories'])

    def test_get_the_view(self):
        url = reverse('match')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIsInstance(response.context['form'], QuestionsCategoryForm)

    def test_get_post(self):
        url = reverse('match')
        data = {'categories': [self.cat1.id, self.cat2.id]}
        response = self.client.post(url, data=data)
        self.assertEquals(response.status_code, 200)
        candidatos = response.context['candidatos']
        c_as_dict = json.dumps(candidatos)
        self.assertTrue(c_as_dict)
