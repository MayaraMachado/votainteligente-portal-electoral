# coding=utf-8
from django import forms
from medianaranja2.forms import ProposalModelMultipleChoiceField, MediaNaranjaWizardForm, QuestionsForm
from popular_proposal.models import PopularProposal
from django.core.cache import cache
from django.conf import settings
from elections.models import Area, QuestionCategory, PersonalData
from django.contrib.sites.models import Site
from medianaranja2.proposals_getter import ByOnlySiteProposalGetter
from merepresenta.models import MeRepresentaPopularProposal, Candidate, RaceMixin, LGBTQDescription
from django.utils.safestring import mark_safe
from medianaranja2.adapters import Adapter as OriginalAdapter

GENDERS  = [
    ('F', u"Feminino"),
    ('M', u"Masculino"),
    ('outro', u"Outro gênero"),
]

SIM_OU_NAO = [
    ('sim', u"Sim"),
    ('nao', u"Nao"),
]

def get_races():
    RACES = []
    for f in RaceMixin._meta.fields:
        RACES.append((f.name, f.verbose_name))
    return RACES

RACES = get_races()

class PersonalDataForm(forms.Form):
    email = forms.EmailField(label=u"Para manter contato, quais desses e-mails você mais usa?",
                             widget=forms.EmailInput(attrs={'placeholder': 'Outro'}),
                             required=False)
    gender = forms.ChoiceField(choices=GENDERS,
                                widget=forms.RadioSelect,
                                label=u'Com qual desses gêneros você se identifica?')
    lgbt = forms.BooleanField(label=u'Sim, eu sou LGBT', required=False)
    lgbt_desc = forms.ModelMultipleChoiceField(label=u'Selecione com quais opções você se identifica:',
                                               widget=forms.CheckboxSelectMultiple(attrs={'id': 'lgbt_desc'}),
                                               queryset=LGBTQDescription.objects.all(),
                                               required=False)
    races = forms.MultipleChoiceField(label=u'Qual é a sua cor ou raça?',
                                      widget=forms.CheckboxSelectMultiple,
                                      choices=RACES,
                                      required=False,
                                      help_text=u"Você pode marcar mais de uma.")
    bio = forms.CharField(label=u"Escreva um pouco sobre você", widget=forms.Textarea, required=False)
    candidatura_coletiva = forms.BooleanField(label=u'Sim', required=False
                        )
    renovacao_politica = forms.CharField(label=u"Você faz parte de algum grupo de Renovação Política? Qual?", required=False)


    def __init__(self, *args, **kwargs):
        self.candidate = kwargs.pop('candidate')
        initial = {}
        if 'initial' in kwargs:
            kwargs['initial'].update(initial)
        else:
            kwargs['initial'] = initial
            personal_datas_as_dict = {}
            for personal_data in self.candidate.personal_datas.all():
                personal_datas_as_dict[personal_data.label] = personal_data.value

            for field  in self.__class__.base_fields:
                candidate_has_field = hasattr(self.candidate, field)
                if candidate_has_field:
                    value = getattr(self.candidate, field, None)
                    kwargs['initial'][field] = value
                else:
                    kwargs['initial'][field] = personal_datas_as_dict.get(field, None)
        ## special cases
        races = []
        for race in RACES:
            race_candidate = getattr(self.candidate, race[0])
            if race_candidate:
                races.append(race[0])
        lgbt_desc = []
        if self.candidate.lgbt:
            for desc in self.candidate.lgbt_desc.all():
                lgbt_desc.append(desc.id)
        kwargs['initial']['races'] = races
        kwargs['initial']['lgbt_desc'] = lgbt_desc
        super(PersonalDataForm, self).__init__(*args, **kwargs)
            

    def save(self):
        selected_races = self.cleaned_data.pop('races')
        lgbt_descs = self.cleaned_data.pop('lgbt_desc', [])
        for race in RACES:
            race_key = race[0]
            if race_key in selected_races:
                setattr(self.candidate, race_key, True)
            else:
                setattr(self.candidate, race_key, False)
        for f_name in self.cleaned_data:
            if hasattr(self.candidate, f_name):
                setattr(self.candidate, f_name, self.cleaned_data[f_name])
            else:
                personal_data, created = PersonalData.objects.get_or_create(candidate=self.candidate,
                                                                            label=f_name)
                personal_data.value = self.cleaned_data[f_name]
                if personal_data.value is None:
                    personal_data.value = ''
                personal_data.save()
        self.candidate.save()
        self.candidate.lgbt_desc = lgbt_descs
        return self.candidate


class MeRepresentaProposalModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    template_name = 'merepresenta/checkbox_select.html'
    option_template_name = 'merepresenta/checkbox_option.html'

    def label_from_instance(self, obj):
        return mark_safe( obj.get_one_liner() )


class WithAreaMixin(forms.Form):
    area = forms.ModelChoiceField(label=u"Em que estado você vota?",
                                    help_text=u"Se você quiser saber com que candidatura ao Congresso você é mais compatível, escolha o estado em que você vota.",
                                    empty_label=u"Selecione seu estado",
                                    required=True,
                                    queryset=Area.objects.filter(classification__in=settings.FILTERABLE_AREAS_TYPE).order_by('name'))


class MeRepresentaProposalsForm(WithAreaMixin):
    proposals = MeRepresentaProposalModelMultipleChoiceField(queryset=MeRepresentaPopularProposal.objects.none(),
                                                 widget=forms.CheckboxSelectMultiple(attrs={'class': 'proposal_option'}))

    def __init__(self, *args, **kwargs):
        self.proposals = kwargs.pop('proposals')
        super(MeRepresentaProposalsForm, self).__init__(*args, **kwargs)
        proposals_qs_cache_key = 'merepresenta_proposals_qs'
        if cache.get(proposals_qs_cache_key) is not None:
            self.fields['proposals'].queryset = cache.get(proposals_qs_cache_key)
            return
        qs = MeRepresentaPopularProposal.objects.filter(id__in=[p.id for p in self.proposals]).order_by('clasification')
        cache.set(proposals_qs_cache_key, qs)
        self.fields['proposals'].queryset = qs


class MeRepresentaMeiaLaranjaWizardForm(MediaNaranjaWizardForm):
    template_name = 'merepresenta/perguntas.html'
    done_template_name = 'merepresenta/resultado.html'
    form_list = [MeRepresentaProposalsForm]
    steps_and_functions = {
        0: 'get_proposals_form_kwargs'
    }

    def get_template_names(self):
        return self.template_name

    def get_proposal_class(self):
        return ByOnlySiteProposalGetter

    def get_proposal_getter_kwargs(self):
        site = Site.objects.get(id=settings.MEREPRESENTA_SITE_ID)
        return {'site': site, 'proposal_class': MeRepresentaPopularProposal}

    def get_element_selector_from_cleaned_data(self, cleaned_data):
        return cleaned_data.get('area', None)

    def get_proposals_form_kwargs(self, cleaned_data):
        proposal_getter_kwargs = self.get_proposal_getter_kwargs()
        getter = self.get_proposal_class()(**proposal_getter_kwargs)

        proposals = getter.get_all_proposals(self.get_element_selector_from_cleaned_data(cleaned_data))
        return {'proposals': proposals}


class MeRepresentaQuestionsForm(QuestionsForm, WithAreaMixin):

    def __init__(self, *args, **kwargs):
        kwargs['categories'] = QuestionCategory.objects.all()
        super(MeRepresentaQuestionsForm, self).__init__(*args, **kwargs)

class MeRepresentaAdapter(OriginalAdapter):
    def _get_topics_and_positions(self, election):
        topics = []
        positions = []
        for category in QuestionCategory.objects.order_by('id'):
            for topic in category.topics.order_by('id'):
                topics.append(topic)
                for position in topic.positions.all().order_by('id'):
                    positions.append(position)
        return (topics, positions)

class MeRepresentaMeiaLaranjaQuestionsWizardForm(MediaNaranjaWizardForm):
    template_name = 'merepresenta/questions.html'
    done_template_name = 'merepresenta/resultado.html'
    calculator_extra_kwargs = {'questions_adapter_class':MeRepresentaAdapter}

    form_list = [MeRepresentaQuestionsForm]

    def get_template_names(self):
        return self.template_name

    def get_element_selector_from_cleaned_data(self, cleaned_data):
        return cleaned_data.get('area', None)
