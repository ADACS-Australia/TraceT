
import numpy
from trigger_app.signals import startup_signal
from django.views.generic.list import ListView
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from django.db import transaction
from django.db import models as dj_model
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage
import django_filters
from django_filters.views import FilterView
from django.utils.datastructures import MultiValueDict
from django.forms import DateTimeInput, Select
from django.core.files.base import ContentFile
from itertools import chain
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from . import models, serializers, forms, signals
from .telescope_observe import trigger_observation

import sys
import voeventparse as vp
from astropy.coordinates import SkyCoord
from astropy import units as u
import datetime

from tracet import parse_xml
import atca_rapid_response_api as arrApi

import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.level = logging.INFO

# Create a startup signal


if 'runserver' in sys.argv:
    # Send off start up signal because server is launching in development
    startup_signal.send(sender=startup_signal)


class EventFilter(django_filters.FilterSet):
    # DateTimeFromToRangeFilter raises exceptions in debugger for missing _before and _after keys
    recieved_data_after = django_filters.DateTimeFilter(
        field_name='recieved_data', lookup_expr='gte', widget=DateTimeInput(attrs={'type': 'datetime-local'}))
    recieved_data_before = django_filters.DateTimeFilter(
        field_name='recieved_data', lookup_expr='lte', widget=DateTimeInput(attrs={'type': 'datetime-local'}))

    event_observed_after = django_filters.DateTimeFilter(
        field_name='event_observed', lookup_expr='gte', widget=DateTimeInput(attrs={'type': 'datetime-local'}))
    event_observed_before = django_filters.DateTimeFilter(
        field_name='event_observed', lookup_expr='lte', widget=DateTimeInput(attrs={'type': 'datetime-local'}))

    duration__lte = django_filters.NumberFilter(
        field_name='duration', lookup_expr='lte')
    duration__gte = django_filters.NumberFilter(
        field_name='duration', lookup_expr='gte')

    ra__lte = django_filters.NumberFilter(field_name='ra', lookup_expr='lte')
    ra__gte = django_filters.NumberFilter(field_name='ra', lookup_expr='gte')

    dec__lte = django_filters.NumberFilter(field_name='dec', lookup_expr='lte')
    dec__gte = django_filters.NumberFilter(field_name='dec', lookup_expr='gte')

    pos_error__lte = django_filters.NumberFilter(
        field_name='pos_error', lookup_expr='lte')
    pos_error__gte = django_filters.NumberFilter(
        field_name='pos_error', lookup_expr='gte')

    fermi_detection_prob__lte = django_filters.NumberFilter(
        field_name='fermi_detection_prob', lookup_expr='lte')
    fermi_detection_prob__gte = django_filters.NumberFilter(
        field_name='fermi_detection_prob', lookup_expr='gte')

    swift_rate_signif__lte = django_filters.NumberFilter(
        field_name='swift_rate_signif', lookup_expr='lte')
    swift_rate_signif__gte = django_filters.NumberFilter(
        field_name='swift_rate_signif', lookup_expr='gte')

    telescopes = django_filters.AllValuesMultipleFilter(field_name='telescope')

    class Meta:
        model = models.Event

        # Django-filter cannot hanlde django FileField so exclude from filters
        fields = ('recieved_data_after', 'recieved_data_before', 'event_observed_after', 'event_observed_before', 'duration__lte', 'duration__gte', 'ra__lte', 'ra__gte', 'dec__lte', 'dec__gte', 'pos_error__lte', 'pos_error__gte',
                  'fermi_detection_prob__lte', 'fermi_detection_prob__gte', 'swift_rate_signif__lte', 'swift_rate_signif__gte', 'ignored', 'event_group_id__source_type', 'trig_id', 'telescope', 'event_group_id__source_name', 'sequence_num', 'event_type', 'telescopes')
        filter_overrides = {
            dj_model.CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
        }


def EventList(request):
    # Apply filters
    f = EventFilter(request.GET, queryset=models.Event.objects.all())
    events = f.qs

    # Get position error units
    poserr_unit = request.GET.get('poserr_unit', 'deg')

    # Paginate
    page = request.GET.get('page', 1)
    paginator = Paginator(events, 100)
    try:
        events = paginator.page(page)
    except InvalidPage:
        # if the page contains no results (EmptyPage exception) or
        # the page number is not an integer (PageNotAnInteger exception)
        # return the first page
        events = paginator.page(1)

    min_rec = models.Event.objects.filter().order_by(
        'recieved_data').first().recieved_data
    min_obs = models.Event.objects.filter().order_by(
        'event_observed').first().event_observed

    has_filter = any(field in request.GET for field in set(f.get_fields()))
    return render(request, 'trigger_app/voevent_list.html', {'filter': f, "page_obj": events, "poserr_unit": poserr_unit, 'has_filter': has_filter, 'min_rec': str(min_rec), 'min_obs': str(min_obs)})


class ProposalDecisionFilter(django_filters.FilterSet):
    # DateTimeFromToRangeFilter raises exceptions in debugger for missing _before and _after keys

    recieved_data_after = django_filters.DateTimeFilter(
        field_name='recieved_data', lookup_expr='gte', widget=DateTimeInput(attrs={'type': 'datetime-local'}))
    recieved_data_before = django_filters.DateTimeFilter(
        field_name='recieved_data', lookup_expr='lte', widget=DateTimeInput(attrs={'type': 'datetime-local'}))

    class Meta:
        model = models.ProposalDecision
        fields = '__all__'


def ProposalDecisionList(request):
    # Apply filters
    f = ProposalDecisionFilter(
        request.GET, queryset=models.ProposalDecision.objects.all())
    ProposalDecision = f.qs

    # Get position error units
    poserr_unit = request.GET.get('poserr_unit', 'deg')

    # Paginate
    page = request.GET.get('page', 1)
    paginator = Paginator(ProposalDecision, 100)
    try:
        ProposalDecision = paginator.page(page)
    except InvalidPage:
        # if the page contains no results (EmptyPage exception) or
        # the page number is not an integer (PageNotAnInteger exception)
        # return the first page
        ProposalDecision = paginator.page(1)

    strip_time_stamp(ProposalDecision)
    min_dec = models.ProposalDecision.objects.filter().order_by(
        'recieved_data').first().recieved_data

    return render(request, 'trigger_app/proposal_decision_list.html', {'filter': f, "page_obj": ProposalDecision, "poserr_unit": poserr_unit, "min_dec": min_dec})


def grab_decisions_for_event_groups(event_groups):
    # For the event groups, grab all useful information like each proposal decision was
    prop_settings = models.ProposalSettings.objects.all()

    telescope_list = []
    source_name_list = []
    proposal_decision_list = []
    proposal_decision_id_list = []
    for event_group in event_groups:
        event_group_events = models.Event.objects.filter(
            event_group_id=event_group)
        telescope_list.append(
            ' '.join(set(event_group_events.values_list('telescope', flat=True)))
        )
        event_with_source_name = list(
            filter(lambda x: x.source_name is not None, list(event_group_events)))
        if(len(event_with_source_name) > 0):
            source_name_list.append(event_with_source_name[0].source_name)
        else:
            source_name_list.append(event_group_events.first().source_name)
        # grab decision for each proposal
        decision_list = []
        decision_id_list = []
        for prop in prop_settings:
            this_decision = models.ProposalDecision.objects.filter(
                event_group_id=event_group, proposal=prop)
            if this_decision.exists():
                decision_list.append(
                    this_decision.first().get_decision_display())
                decision_id_list.append(this_decision.first().id)
            else:
                decision_list.append("")
                decision_id_list.append("")
        proposal_decision_list.append(decision_list)
        proposal_decision_id_list.append(decision_id_list)

    # zip into something that you can iterate over in the html
    return list(zip(event_groups, telescope_list, source_name_list, proposal_decision_list, proposal_decision_id_list)), event_groups


class EventGroupFilter(django_filters.FilterSet):
    telescope = django_filters.ChoiceFilter(
        field_name='telescope',
        choices=(
            ('SWIFT', 'SWIFT'),
            ('Fermi', 'Fermi'),
            ('LVC', 'LVC')
        ),
        method='filter_telescope')

    def filter_telescope(self, queryset, name, value):
        # construct the full lookup expression.
        return queryset.filter(voevent__telescope=value)

    class Meta:
        model = models.EventGroup
        fields = ['ignored', 'source_type', 'telescope']


def EventGroupList(request):
    # Apply filters
    req = request.GET
    if(not req.dict()):
        req = QueryDict("ignored=False&source_type=GRB&telescope=SWIFT")

    f = EventGroupFilter(req, queryset=models.EventGroup.objects.distinct())
    eventgroups = f.qs

    prop_settings = models.ProposalSettings.objects.all()
    # Paginate
    page = request.GET.get('page', 1)
    # zip the trigger event and the tevent_telescope_list together so I can loop over both in the html
    paginator = Paginator(eventgroups, 100)
    try:
        event_group_ids_paged = paginator.page(page)
    except InvalidPage:
        event_group_ids_paged = paginator.page(1)

    recent_triggers_info, page_obj = grab_decisions_for_event_groups(
        event_group_ids_paged)

    return render(request, 'trigger_app/event_group_list.html', {'filter': f, "trigger_info": recent_triggers_info, "settings": prop_settings, "page_obj": page_obj})


class CometLogFilter(django_filters.FilterSet):
    created_filter = django_filters.DateTimeFilter(
        field_name='created_at', lookup_expr='lte', widget=DateTimeInput(attrs={'type': 'datetime-local'}))

    class Meta:
        model = models.CometLog
        fields = {
            'created_at',
        }


def comet_log(request):
    f = CometLogFilter(request.GET, queryset=models.CometLog.objects.all())
    logs = f.qs

    # Paginate
    page = request.GET.get('page', 1)
    paginator = Paginator(logs, 100)
    try:
        logs = paginator.page(page)
    except InvalidPage:
        # if the page contains no results (EmptyPage exception) or
        # the page number is not an integer (PageNotAnInteger exception)
        # return the first page
        logs = paginator.page(1)

    return render(request, 'trigger_app/cometlog_filter.html', {'filter': f, "page_obj": logs})


class ProposalSettingsList(ListView):
    model = models.ProposalSettings
    ordering = ['priority']


def home_page(request):
    comet_status = models.Status.objects.get(name='twistd_comet')
    kafka_status = models.Status.objects.get(name='kafka')

    prop_settings = models.ProposalSettings.objects.all()

    # Filter out ignored event groups and telescope=swift and show only the 5 most recent
    recent_event_groups = models.EventGroup.objects.filter(
        ignored=False, source_type="GRB")
    recent_event_group_info, _ = grab_decisions_for_event_groups(
        recent_event_groups)

    recent_event_group_info = filter(
        lambda x: x[1] == "SWIFT", recent_event_group_info)

    context = {
        'twistd_comet_status': comet_status,
        'kafka_status': kafka_status,
        'settings': prop_settings,
        'remotes': ", ".join(settings.VOEVENT_REMOTES),
        'tcps': ", ".join(settings.VOEVENT_TCP),
        "recent_event_groups": list(recent_event_group_info)[:10]
    }
    return render(request, 'trigger_app/home_page.html', context)


def strip_time_stamp(prop_decs):
    for prop_dec in prop_decs:
        prop_dec_lines = prop_dec.decision_reason.split("\n")
        stripped_lines = []
        for line in prop_dec_lines:
            stripped_lines.append(line[28:])
        prop_dec.decision_reason = "\n".join(stripped_lines)


def EventGroup_details(request, tid):
    event_group = models.EventGroup.objects.get(id=tid)

    # grab telescope names
    events = models.Event.objects.filter(event_group_id=event_group)
    telescopes = ' '.join(set(events.values_list('telescope', flat=True)))

    # list all prop decisions
    prop_decs = models.ProposalDecision.objects.filter(
        event_group_id=event_group)

    # Grab obs if the exist
    obs = []
    for prop_dec in prop_decs:
        obs += models.Observations.objects.filter(
            proposal_decision_id=prop_dec)
    strip_time_stamp(prop_decs)

    # Get position error units
    poserr_unit = request.GET.get('poserr_unit', 'deg')

    context = {
        'event_group': event_group,
        'events': events,
        'obs': obs,
        'prop_decs': prop_decs,
        'telescopes': telescopes,
        'poserr_unit': poserr_unit,
    }

    return render(request, 'trigger_app/event_group_details.html', context)


def ProposalDecision_details(request, id):
    prop_dec = models.ProposalDecision.objects.get(id=id)

    # Work out all the telescopes that observed the event
    events = models.Event.objects.filter(
        event_group_id=prop_dec.event_group_id)
    telescopes = []
    event_types = []
    for event in events:
        telescopes.append(event.telescope)
        event_types.append(event.event_type)
    # Make sure they are unique and put each on a new line
    telescopes = ".\n".join(list(set(telescopes)))
    event_types = " \n".join(list(set(event_types)))

    observations = models.Observations.objects.filter(proposal_decision_id=id)
    poserr_unit = request.GET.get('poserr_unit', 'deg')

    content = {
        'prop_dec': prop_dec,
        'telescopes': telescopes,
        'events': events,
        'event_types': event_types,
        'obs': observations,
        'poserr_unit': poserr_unit,
    }
    return render(request, 'trigger_app/proposal_decision_details.html', content)


def ProposalDecision_result(request, id, decision):
    prop_dec = models.ProposalDecision.objects.get(id=id)

    if decision:
        # Decision is True (1) so trigger an observation
        obs_decision, decision_reason_log = trigger_observation(
            prop_dec,
            f"{prop_dec.decision_reason}User decided to trigger. ",
            reason="First Observation",
        )
        if obs_decision == 'E':
            # Error observing so send off debug
            trigger_bool = False
            debug_bool = True
        else:
            # Succesfully observed
            trigger_bool = True
            debug_bool = False

        prop_dec.decision_reason = decision_reason_log
        prop_dec.decision = obs_decision

        # send off alert messages to users and admins
        signals.send_all_alerts(trigger_bool, debug_bool, False, prop_dec)
    else:
        # False (0) so just update decision
        prop_dec.decision_reason += "User decided not to trigger. "
        prop_dec.decision = "I"
    prop_dec.save()

    return HttpResponseRedirect(f'/proposal_decision_details/{id}/')


def proposal_decision_path(request, id):
    prop_set = models.ProposalSettings.objects.get(id=id)
    telescope = prop_set.event_telescope

    # Create decision tree flow diagram
    # Set up mermaid javascript
    mermaid_script = f'''flowchart TD
  A(Event) --> B{{"Have we observed\nthis event before?"}}
  B --> |YES| D{{"Is the new event further away than\nthe repointing limit ({prop_set.repointing_limit} degrees)?"}}
  D --> |YES| R(Repoint)
  D --> |NO| END(Ignore)'''
    if telescope is None:
        mermaid_script += '''
  B --> |NO| E{Source type?}'''
    else:
        mermaid_script += f'''
  B --> |NO| C{{Is Event from {telescope}?}}
  C --> |NO| END
  C --> |YES| E{{Source type?}}'''
    mermaid_script += '''
  E --> F[GRB]'''
    if prop_set.source_type == "GRB":
        mermaid_script += f'''
  F --> J{{"Fermi GRB probability > {prop_set.fermi_prob}\\nor\\nSWIFT Rate_signif > {prop_set.swift_rate_signf} sigma"}}'''
        if prop_set.event_any_duration:
            mermaid_script += f'''
  J --> |YES| L[Trigger Observation]
subgraph GRB
  J
  L
end'''
        else:
            mermaid_script += f'''
  J --> |YES| K{{"Event duration between\n {prop_set.event_min_duration} and {prop_set.event_max_duration} s"}}
  J --> |NO| END
  K --> |YES| L[Trigger Observation]
  K --> |NO| M{{"Event duration between\n{prop_set.pending_min_duration_1} and {prop_set.pending_max_duration_1} s\nor\n{prop_set.pending_min_duration_2} and {prop_set.pending_max_duration_2} s"}}
  M --> |YES| N[Pending a human's decision]
  M --> |NO| END
subgraph GRB
  J
  K
  L
  M
  N
end
  style N fill:orange,color:white'''
    else:
        mermaid_script += '''
  F[GRB] --> END'''
    if prop_set.source_type == "FS":
        mermaid_script += f'''
  E --> G[Flare Star] --> L[Trigger Observation]'''
    else:
        mermaid_script += '''
  E --> G[Flare Star] --> END'''
    if prop_set.source_type == "NU":
        mermaid_script += f'''
  E --> I[Neutrino]
  I[Neutrino] --> |Antares Event| RANK{{Is the Antares ranking less than or equal to {prop_set.antares_min_ranking}?}}
  RANK --> |YES| L[Trigger Observation]
  RANK --> |NO| END
  I[Neutrino] --> |Non-Antares Event| L[Trigger Observation]
subgraph NU
  I
  RANK
end'''
    else:
        mermaid_script += '''
    E --> I[Neutrino] --> END'''
    if prop_set.source_type == "GW":
        mermaid_script += f'''
    E --> H[GW] --> L[Trigger Observation]'''
    else:
        mermaid_script += f'''
    E --> H[GW] --> END'''
    mermaid_script += '''
  style A fill:blue,color:white
  style END fill:red,color:white
  style L fill:green,color:white
  style R fill:#21B6A8,color:white'''

    return render(request, 'trigger_app/proposal_decision_path.html', {'proposal': prop_set,
                                                                       'mermaid_script': mermaid_script})


@login_required
def user_alert_status(request):
    proposals = models.ProposalSettings.objects.all()
    prop_alert_list = []
    for prop in proposals:
        # For each proposals find the user and admin alerts
        u = request.user
        user_alerts = models.UserAlerts.objects.filter(user=u, proposal=prop)
        alert_permissions = models.AlertPermission.objects.get(
            user=u, proposal=prop)
        # Put them into a dict that can be looped over in the html
        prop_alert_list.append({
            "proposal": prop,
            "user": user_alerts,
            "permission": alert_permissions,
        })
    return render(request, 'trigger_app/user_alert_status.html', {'prop_alert_list': prop_alert_list})


@login_required
def user_alert_delete(request, id):
    u = request.user
    user_alert = models.UserAlerts.objects.get(user=u, id=id)
    user_alert.delete()
    return HttpResponseRedirect('/user_alert_status/')


@login_required
def user_alert_create(request):
    if request.POST:
        # Create UserAlert that already includes user and proposal
        u = request.user
        ua = models.UserAlerts(user=u)
        # Let user update everything else
        form = forms.UserAlertForm(request.POST, instance=ua)
        if form.is_valid():
            try:
                form.save()
                # on success, the request is redirected as a GET
                return HttpResponseRedirect('/user_alert_status/')
            except:
                pass  # handling can go here
    else:
        form = forms.UserAlertForm()
    return render(request, 'trigger_app/form.html', {'form': form})


def voevent_view(request, id):
    event = models.Event.objects.get(id=id)
    v = vp.loads(event.xml_packet.encode())
    xml_pretty_str = vp.prettystr(v)
    return HttpResponse(xml_pretty_str, content_type='text/xml')


@transaction.atomic
def parse_and_save_xml(xml):
    logger.info(f'Attempting to parse xml {xml}')
    trig = parse_xml.parsed_VOEvent(None, packet=xml)
    logger.info(f'Successfully parsed xml {trig}')
    data = {
        'telescope': trig.telescope,
        'xml_packet': xml,
        'duration': trig.event_duration,
        'trig_id': trig.trig_id,
        'self_generated_trig_id': trig.self_generated_trig_id,
        'sequence_num': trig.sequence_num,
        'event_type': trig.event_type,
        'role': trig.role,
        'ra': trig.ra,
        'dec': trig.dec,
        'ra_hms': trig.ra_hms,
        'dec_dms': trig.dec_dms,
        'pos_error': trig.err,
        'ignored': trig.ignore,
        'source_name': trig.source_name,
        'source_type': trig.source_type,
        'event_observed': trig.event_observed,
        'fermi_most_likely_index': trig.fermi_most_likely_index,
        'fermi_detection_prob': trig.fermi_detection_prob,
        'swift_rate_signif': trig.swift_rate_signif,
        'hess_significance': trig.hess_significance,
        'antares_ranking': trig.antares_ranking,
        'lvc_false_alarm_rate': trig.lvc_false_alarm_rate,
        'lvc_binary_neutron_star_probability': trig.lvc_binary_neutron_star_probability,
        'lvc_neutron_star_black_hole_probability': trig.lvc_neutron_star_black_hole_probability,
        'lvc_binary_black_hole_probability': trig.lvc_binary_black_hole_probability,
        'lvc_terrestial_probability': trig.lvc_terrestial_probability,
        'lvc_includes_neutron_star_probability': trig.lvc_includes_neutron_star_probability,
        'lvc_skymap_fits': trig.lvc_skymap_fits
    }

    if trig.lvc_skymap_file:
        data['lvc_skymap_file'] = ContentFile(
            trig.lvc_skymap_file, f'{trig.trig_id}_skymap.fits')

    logger.info(f'New event data {data}')

    new_event = serializers.EventSerializer(data=data)
    if new_event.is_valid():
        logger.info(
            f'Successfully serialized event {new_event.validated_data}')
        new_event.save()
        logger.info(f'Successfully saved event {new_event.validated_data}')
        return new_event


@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def event_create(request):
    logger.info('Request to create an event received',
                extra={'event_create': True})
    logger.info(f'request.data:{request.data}')
    xml_string = request.data['xml_packet']
    new_event = parse_and_save_xml(xml_string)

    if new_event:
        logger.info('Event created response given to user')
        logger.info('Request to create an event received',
                    extra={'event_create_finished': True})
        return Response(new_event.data, status=status.HTTP_201_CREATED)
    else:
        logger.debug(request.data)
        logger.info('Request to create an event received',
                    extra={'event_create_finished': True})
        return Response(new_event.errors, status=status.HTTP_400_BAD_REQUEST)


@login_required
def proposal_form(request, id=None):
    # grab source type telescope dict
    src_tele = parse_xml.SOURCE_TELESCOPES
    if id:
        proposal = models.ProposalSettings.objects.get(id=id)
        title = f"Editing Proposal #{id}"
    else:
        proposal = None
        title = "New Proposal"
    if request.POST:
        form = forms.ProjectSettingsForm(request.POST, instance=proposal)
        if form.is_valid():
            saved = form.save()
            # on success, the request is redirected as a GET
            return redirect(proposal_decision_path, id=saved.id)
    else:
        form = forms.ProjectSettingsForm(instance=proposal)
    return render(request, 'trigger_app/proposal_form.html', {'form': form, "src_tele": src_tele, "title": title})


@login_required
def test_upload_xml(request):
    proposals = models.ProposalSettings.objects.filter(testing=False)
    if request.method == "POST":
        form = forms.TestEvent(request.POST)
        if form.is_valid():
            # Parse and submit the Event
            xml_string = str(request.POST['xml_packet'])
            logger.info(f'Test_upload_xml xml_string:{xml_string}')
            parse_and_save_xml(xml_string)
            logger.info(f'Test_upload_xml xml_string:{xml_string}')
            return HttpResponseRedirect('/')
    else:
        form = forms.TestEvent()
    return render(request, 'trigger_app/test_upload_xml_form.html', {'form': form, "proposals": proposals})


def cancel_atca_observation(request, id=None):
    # Grab obs and proposal data
    obs = models.Observations.objects.filter(obsid=id).first()
    proposal_settings = obs.proposal_decision_id.proposal
    decision_reason_log = obs.proposal_decision_id.decision_reason

    # Create the cancel request
    rapidObj = {'requestDict': {'cancel': obs.obsid,
                                'project': proposal_settings.project_id.id}}
    rapidObj["authenticationToken"] = proposal_settings.project_id.password
    rapidObj["email"] = proposal_settings.project_id.atca_email

    # Send the request.
    atca_request = arrApi.api(rapidObj)
    try:
        response = atca_request.send()
    except arrApi.responseError as r:
        logger.error(f"ATCA return message: {r}")
        decision_reason_log += f"ATCA cancel failed, return message: {r}\n "
        decision = 'E'
    else:
        decision_reason_log += f"ATCA observation canceled at {datetime.datetime.utcnow()}. \n"
        decision = 'C'
    # Update propocal decision
    proposal_decision = obs.proposal_decision_id
    proposal_decision.decision_reason = decision_reason_log
    proposal_decision.decision = decision
    proposal_decision.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
