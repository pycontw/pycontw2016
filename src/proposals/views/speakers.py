from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.http import Http404
from django.views.generic import CreateView, UpdateView

from proposals.forms import (
    AdditionalSpeakerCancelForm, AdditionalSpeakerCreateForm,
    AdditionalSpeakerSetStatusForm,
)
from proposals.models import AdditionalSpeaker, TalkProposal, TutorialProposal

from .mixins import FormValidMessageMixin, UserProfileRequiredMixin


class ProposalManageSpeakersView(
        LoginRequiredMixin, UserProfileRequiredMixin,
        FormValidMessageMixin, CreateView):

    model = AdditionalSpeaker
    form_class = AdditionalSpeakerCreateForm
    template_name = 'proposals/manage_speakers.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.proposal = (
                self.proposal_model.objects
                .select_related('submitter').get(pk=kwargs['pk'])
            )
        except self.proposal_model.DoesNotExist:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'request': self.request,
            'proposal': self.proposal,
        })
        return kwargs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['proposal'] = self.proposal
        return data

    def get_success_url(self):
        return self.proposal.get_manage_speakers_url()


class TalkProposalManageSpeakersView(ProposalManageSpeakersView):
    proposal_model = TalkProposal


class TutorialProposalManageSpeakersView(ProposalManageSpeakersView):
    proposal_model = TutorialProposal


class AdditionalSpeakerRemoveView(
        LoginRequiredMixin, UserProfileRequiredMixin,
        FormValidMessageMixin, UpdateView):

    model = AdditionalSpeaker
    form_class = AdditionalSpeakerCancelForm

    def get_object(self):
        instance = super().get_object()
        if instance.proposal.submitter != self.request.user:
            raise Http404
        return instance

    def get_success_url(self):
        return self.object.proposal.get_manage_speakers_url()


class AdditionalSpeakerSetStatusView(
        LoginRequiredMixin, UserProfileRequiredMixin,
        FormValidMessageMixin, UpdateView):

    http_method_names = ['post', 'options']
    model = AdditionalSpeaker
    form_class = AdditionalSpeakerSetStatusForm

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_success_url(self):
        return reverse('user_dashboard')
