import xml.etree.ElementTree as ET

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect

from events.forms import SignupForm
from events.models import Event, EventSignup
from uwcs_auth.models import WarwickGGUser


class EventIndexView(LoginRequiredMixin, View):
    template_name = 'events/event_index.html'
    login_url = '/accounts/login/'

    def get(self, request):
        ctx = {}
        return render(request, self.template_name, context=ctx)


class EventView(View):
    template_name = 'events/event_home.html'

    def get(self, request, slug):
        event = get_object_or_404(Event, slug=slug)

        has_signed_up = False
        if request.user.is_authenticated:
            has_signed_up = EventSignup.objects.for_event(event, request.user).exists()

        ctx = {
            'event': event,
            'has_signed_up': has_signed_up,
            'event_slug': slug,
        }

        return render(request, self.template_name, context=ctx)


def check_membership(api_token, uni_id, request, society):
    membership_url = 'https://www.warwicksu.com/membershipapi/listMembers/{token}/'.format(token=api_token)
    api_call = requests.get(membership_url)

    if api_call.status_code == 200:
        xml_root = ET.fromstring(api_call.text)
        members = list(map(lambda x: x.find('UniqueID').text, xml_root))

        return uni_id in members
    else:
        messages.error(request,
                       'There was an error checking your {soc} membership, please contact an exec member.'.format(
                           soc=society), extra_tags='is-danger')

        return False


class SignupChargeView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'

    @method_decorator(csrf_protect, name='dispatch')
    def post(self, request):
        # TODO: Charge stripe
        pass


class SignupFormView(LoginRequiredMixin, View):
    template_name = 'events/signup_view.html'
    login_url = '/accounts/login/'

    def get(self, request, slug):
        event = get_object_or_404(Event, slug=slug)

        has_signed_up = EventSignup.objects.for_event(event, request.user).exists()
        if has_signed_up:
            messages.error(request, 'You\'re already signed up to that event.', extra_tags='is-danger')
            return redirect('event_home', slug=slug)

        profile = WarwickGGUser.objects.get(user=request.user)

        # If the event is hosted by UWCS
        if 'UWCS' in event.hosted_by:
            uwcs_member = check_membership(settings.UWCS_API_KEY, profile.uni_id, request, 'UWCS')
        else:
            uwcs_member = False

        # If the event is hosted by Esports
        if 'WE' in event.hosted_by:
            esports_member = check_membership(settings.ESPORTS_API_KEY, profile.uni_id, request, 'Esports')
        else:
            esports_member = False

        is_host_member = esports_member or uwcs_member
        signup_cost = event.cost_member if (esports_member or uwcs_member) else event.cost_non_member

        signup_form = SignupForm()

        ctx = {
            'event': event,
            'event_cost': signup_cost,
            'stripe_cost': 100 * signup_cost,
            'is_host_member': is_host_member,
            'stripe_pubkey': settings.STRIPE_PUBLIC_KEY,
            'signup_form': signup_form
        }
        return render(request, self.template_name, context=ctx)


class UnsignupFormView(LoginRequiredMixin, View):
    template_name = 'events/unsignup_view.html'
    login_url = '/accounts/login/'

    def get(self, request, slug):
        event = get_object_or_404(Event, slug=slug)

        has_signed_up = EventSignup.objects.for_event(event, request.user).exists()

        if not has_signed_up:
            messages.error(request, 'You cannot un-signup from an event you\'re not signed up to.',
                           extra_tags='is-danger')
            return redirect('event_home', slug=slug)

        ctx = {
            'event': event
        }
        return render(request, self.template_name, context=ctx)
