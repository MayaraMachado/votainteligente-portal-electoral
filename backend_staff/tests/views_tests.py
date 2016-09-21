# coding=utf-8
from django.core.urlresolvers import reverse
from elections.tests import VotaInteligenteTestCase as TestCase
from django.contrib.auth.models import User
from popular_proposal.models import ProposalTemporaryData, PopularProposal, Commitment
from popular_proposal.forms import RejectionForm
from elections.models import Area
from elections.models import Election, Candidate
from preguntales.models import Message
from django.core import mail
from backend_staff.views import Stats
from backend_candidate.models import CandidacyContact, Candidacy


NON_STAFF_PASSWORD = 'gatito'
STAFF_PASSWORD = 'perrito'


class StaffHomeViewTest(TestCase):
    def setUp(self):
        super(StaffHomeViewTest, self).setUp()
        self.non_staff = User.objects.create_user(username='non_staff',
                                                  email='nonstaff@perrito.com',
                                                  password=NON_STAFF_PASSWORD)
        self.fiera = User.objects.get(username='fiera')
        self.fiera.set_password(STAFF_PASSWORD)
        self.fiera.save()
        self.feli = User.objects.get(username='feli')
        self.arica = Area.objects.get(id='arica-15101')
        self.data = {
            'problem': u'A mi me gusta la contaminación de Santiago y los autos y sus estresantes ruedas',
            'solution': u'Viajar a ver al Feli una vez al mes',
            'when': u'1_year',
            'allies': u'El Feli y el resto de los cabros de la FCI'
        }
        self.election = Election.objects.get(id=1)
        self.election.position = 'alcalde'
        self.election.save()
        self.candidate1 = Candidate.objects.get(id=1)
        self.candidate2 = Candidate.objects.get(id=2)
        self.candidate3 = Candidate.objects.get(id=3)
        self.election2 = Election.objects.get(id=2)
        self.election2.position = 'concejal'
        self.election2.save()
        self.candidate4 = Candidate.objects.get(id=4)
        self.candidate5 = Candidate.objects.get(id=5)
        self.candidate6 = Candidate.objects.get(id=6)

    def is_reachable_only_by_staff(self, url, url_kwargs=None):
        url = reverse(url, kwargs=url_kwargs)

        # I'm not logged in
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

        # I'm logged in but I'm not staff
        self.client.login(username=self.non_staff.username,
                          password=NON_STAFF_PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

        # I'm logged in and I'm staff
        self.client.login(username=self.fiera.username,
                          password=STAFF_PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        return response

    def test_home_view_only_reachable_by_staff_members(self):
        response = self.is_reachable_only_by_staff('backend_staff:index')
        self.assertTemplateUsed(response, 'backend_staff/index.html')

    def test_get_comments_staff_form_for_popular_proposal(self):
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              area=self.arica,
                                                              data=self.data)
        response = self.is_reachable_only_by_staff('backend_staff:popular_proposal_comments',
                                                   url_kwargs={'pk': temporary_data.id})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['temporary_data'], temporary_data)
        self.assertTemplateUsed(response, 'backend_staff/popular_proposal_comments.html')

    def test_post_comments_on_popular_proposals(self):
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              area=self.arica,
                                                              data=self.data)
        data = {'problem': u'',
                'when': u'el plazo no está tan weno',
                'solution': u'',
                'allies': u'Los aliados podrían ser mejores'}

        url = reverse('backend_staff:popular_proposal_comments', kwargs={'pk': temporary_data.id})
        self.client.login(username=self.fiera.username,
                          password=STAFF_PASSWORD)
        response = self.client.post(url, data=data, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'backend_staff/index.html')
        self.assertEquals(len(mail.outbox), 1)
        the_mail = mail.outbox[0]
        self.assertIn(self.fiera.email, the_mail.to)
        self.assertEquals(len(the_mail.to), 1)
        self.assertIn(self.fiera.first_name, the_mail.body)

    def test_context(self):
        data = {
            'problem': u'A mi me gusta la contaminación de Santiago y los autos y sus estresantes ruedas',
            'solution': u'Viajar a ver al Feli una vez al mes',
            'when': u'1_year',
            'allies': u'El Feli y el resto de los cabros de la FCI'
        }
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.feli,
                                                              area=self.arica,
                                                              data=data)
        temporary_data2 = ProposalTemporaryData.objects.create(proposer=self.feli,
                                                               area=self.arica,
                                                               data=data)
        temporary_data3 = ProposalTemporaryData.objects.create(proposer=self.feli,
                                                               status=ProposalTemporaryData.Statuses.InTheirSide,
                                                               area=self.arica,
                                                               data=data)

        # Temporary datas are listed in the index so we can moderate them
        # or update them.
        message = Message.objects.create(election=self.election,
                                         author_name='author',
                                         author_email='author@email.com',
                                         subject='Perrito',
                                         content='content',
                                         )
        # Messages are listed as well

        url = reverse('backend_staff:index')
        self.client.login(username=self.fiera.username,
                          password=STAFF_PASSWORD)

        response = self.client.get(url)

        self.assertIn(temporary_data, response.context['proposals'])
        self.assertIn(temporary_data2, response.context['proposals'])
        self.assertIn(temporary_data3, response.context['proposals'])
        self.assertIn(message, response.context['needing_moderation_messages'].all())

    def test_get_proposal_moderation_view(self):
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.feli,
                                                              area=self.arica,
                                                              data=self.data)
        url = reverse('backend_staff:moderate_proposal', kwargs={'pk': temporary_data.id})
        # Credentials checking
        self.assertEquals(self.client.post(url).status_code, 302)
        self.client.login(username=self.non_staff.username,
                          password=NON_STAFF_PASSWORD)
        response = self.client.post(url)
        self.assertEquals(response.status_code, 302)
        self.assertTemplateNotUsed('backend_staff/index.html')

        self.client.login(username=self.fiera.username,
                          password=STAFF_PASSWORD)
        # It does have a get method
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'backend_staff/proposal_moderation.html')
        form = response.context['form']
        self.assertIsInstance(form, RejectionForm)
        self.assertEquals(form.temporary_data, temporary_data)
        self.assertEquals(form.moderator, self.fiera)

    def test_accept_popular_proposal(self):
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.feli,
                                                              area=self.arica,
                                                              data=self.data)
        url = reverse('backend_staff:accept_proposal', kwargs={'pk': temporary_data.id})
        # Credentials checking
        self.assertEquals(self.client.post(url).status_code, 302)
        self.client.login(username=self.non_staff.username,
                          password=NON_STAFF_PASSWORD)
        response = self.client.post(url)
        self.assertEquals(response.status_code, 302)
        self.assertTemplateNotUsed('backend_staff/index.html')
        self.client.login(username=self.fiera.username,
                          password=STAFF_PASSWORD)
        # It does not have a get method
        response = self.client.get(url)
        self.assertEquals(response.status_code, 405)

        response = self.client.post(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('backend_staff/index.html')
        proposal = PopularProposal.objects.get(data=self.data,
                                               proposer=self.feli,
                                               area=self.arica
                                               )
        self.assertTrue(proposal)

    def test_reject_popular_proposal(self):
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.feli,
                                                              area=self.arica,
                                                              data=self.data)
        url = reverse('backend_staff:reject_proposal', kwargs={'pk': temporary_data.id})
        # Credentials checking
        self.assertEquals(self.client.post(url).status_code, 302)
        self.client.login(username=self.non_staff.username,
                          password=NON_STAFF_PASSWORD)
        response = self.client.post(url)
        self.assertEquals(response.status_code, 302)
        self.assertTemplateNotUsed('backend_staff/index.html')
        self.client.login(username=self.fiera.username,
                          password=STAFF_PASSWORD)
        # It does not have a get method
        response = self.client.get(url)
        self.assertEquals(response.status_code, 405)
        data = {'reason': 'es muy mala'}
        response = self.client.post(url, data=data, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'backend_staff/index.html')
        temporary_data = ProposalTemporaryData.objects.get(id=temporary_data.id)
        self.assertEquals(temporary_data.status, ProposalTemporaryData.Statuses.Rejected)
        self.assertEquals(temporary_data.rejected_reason, data['reason'])

    def test_view_all_commitments(self):
        data = {
            'clasification': 'educacion',
            'title': u'Fiera a Santiago',
            'problem': u'A mi me gusta la contaminación de Santiago y los autos\
 y sus estresantes ruedas',
            'solution': u'Viajar a ver al Feli una vez al mes',
            'when': u'1_year',
            'causes': u'La super distancia',
            'terms_and_conditions': True
        }
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          area=self.arica,
                                                          data=self.data,
                                                          title=u'This is a title',
                                                          clasification=u'education'
                                                          )
        commitment = Commitment.objects.create(candidate=self.candidate1,
                                               proposal=popular_proposal,
                                               detail=u'Yo me comprometo',
                                               commited=True)
        url = reverse('backend_staff:all_commitments')

        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

        # I'm logged in but I'm not journalist
        self.client.login(username=self.non_staff.username,
                          password=NON_STAFF_PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

        # I'm logged in and I'm staff
        self.fiera.profile.is_journalist = True
        self.fiera.profile.save()
        self.client.login(username=self.fiera.username,
                          password=STAFF_PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIn(commitment, response.context['commitments'])

    def test_stats_get(self):

        self.is_reachable_only_by_staff('backend_staff:stats')
        
        url = reverse('backend_staff:stats')
        self.client.login(username=self.fiera.username,
                          password=STAFF_PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIsInstance(response.context['stats'], Stats)
        self.assertTemplateUsed(response, 'backend_staff/stats.html')

    def test_stats_mixin(self):
        User.objects.all().delete()
        stats = Stats()
        self.assertTrue(Candidate.objects.count())
        self.assertEquals(stats.total_candidates(), Candidate.objects.count())
        self.assertEquals(stats.total_candidates_alcalde(),
                          Election.objects.get(position='alcalde').candidates.count())
        self.assertEquals(stats.total_candidates_concejal(),
                          Election.objects.get(position='concejal').candidates.count())

        candidates_in_alcaldes_ids = []
        for c in Election.objects.get(position='alcalde').candidates.all():
            candidates_in_alcaldes_ids.append(c.id)

        for c in Election.objects.get(position='concejal').candidates.all():
            self.assertNotIn(c.id, candidates_in_alcaldes_ids)

        # Candidate one has connected
        user1 = User.objects.create_user(username='user1', password='password')
        self.client.login(username=user1.username, password='password')

        candidacy1 = Candidacy.objects.create(user=user1, candidate=self.candidate1)
        CandidacyContact.objects.create(candidate=self.candidate1,
                                        used_by_candidate=True,
                                        candidacy=candidacy1)

        # Candidate 2 got an email but hasn't read it
        user2 = User.objects.create_user(username='user2', password='password')

        candidacy2 = Candidacy.objects.create(user=user2, candidate=self.candidate2)
        CandidacyContact.objects.create(candidate=self.candidate2,
                                        used_by_candidate=False,
                                        candidacy=candidacy2
                                        )
        # Candidate 3 we have no contact with her
        user3 = User.objects.create_user(username='user3')

        Candidacy.objects.create(user=user3, candidate=self.candidate3)

        # Candidate four has connected
        user4 = User.objects.create_user(username='user4', password='password')
        self.client.login(username=user4.username, password='password')

        candidacy4 = Candidacy.objects.create(user=user4, candidate=self.candidate4)
        CandidacyContact.objects.create(candidate=self.candidate4,
                                        used_by_candidate=True,
                                        candidacy=candidacy4)

        # Candidate 5 got an email but hasn't read it
        user5 = User.objects.create_user(username='user5')

        candidacy5 = Candidacy.objects.create(user=user5, candidate=self.candidate5)
        CandidacyContact.objects.create(candidate=self.candidate5,
                                        used_by_candidate=False,
                                        candidacy=candidacy5
                                        )
        # Candidate 6 we have no contact with her
        user6 = User.objects.create_user(username='user6')

        Candidacy.objects.create(user=user6, candidate=self.candidate6)

        self.assertEquals(stats.participation().with_us, 2)
        self.assertEquals(stats.participation().got_email, 2)
        self.assertGreater(stats.participation().no_contact, 2)

        self.assertEquals(stats.participation_alcalde().with_us, 1)
        self.assertEquals(stats.participation_alcalde().got_email, 1)
        self.assertEquals(stats.participation_alcalde().no_contact, 1)

        self.assertEquals(stats.participation_concejal().with_us, 1)
        self.assertEquals(stats.participation_concejal().got_email, 1)
        self.assertEquals(stats.participation_concejal().no_contact, 1)

        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          area=self.arica,
                                                          data=self.data,
                                                          title=u'This is a title',
                                                          clasification=u'education'
                                                          )
        PopularProposal.objects.create(proposer=self.fiera,
                                       area=self.arica,
                                       data=self.data,
                                       title=u'This is a title',
                                       clasification=u'education'
                                       )
        PopularProposal.objects.create(proposer=self.fiera,
                                       area=self.arica,
                                       data=self.data,
                                       title=u'This is a title',
                                       clasification=u'education',
                                       for_all_areas=True
                                       )
        Commitment.objects.create(candidate=self.candidate1,
                                  proposal=popular_proposal,
                                  detail=u'Yo me comprometo',
                                  commited=True)
        self.assertEquals(stats.proposals(), 2)
        self.assertEquals(stats.commitments(), 1)

