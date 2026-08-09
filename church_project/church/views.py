from django.db import models
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

import csv

from .forms import (
    DonationForm,
    EventForm,
    EventLocationCheckinForm,
    EventRegistrationForm,
    MemberForm,
    VolunteerSignupForm,
)
from .models import Attendance, Donation, Event, Group, Member, VolunteerSignup


def is_church_staff(user):
    return user.is_authenticated and (user.is_staff or user.groups.filter(name='Staff').exists())


def is_church_volunteer(user):
    return user.is_authenticated and (user.is_staff or user.groups.filter(name__in=['Volunteer', 'Staff']).exists())


def home(request):
    members_count = Member.objects.count()
    events_count = Event.objects.count()
    donations_total = Donation.objects.aggregate(total_amount=models.Sum('amount'))['total_amount'] or 0
    volunteer_signups_count = VolunteerSignup.objects.count()
    return render(request, 'church/home.html', {
        'members_count': members_count,
        'events_count': events_count,
        'donations_total': donations_total,
        'volunteer_signups_count': volunteer_signups_count,
    })


@login_required
def members(request):
    query = request.GET.get('q', '').strip()
    active = request.GET.get('active', '')
    members = Member.objects.order_by('last_name', 'first_name')
    if query:
        members = members.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
            | Q(phone__icontains=query)
        )
    if active.lower() == 'true':
        members = members.filter(is_active=True)
    elif active.lower() == 'false':
        members = members.filter(is_active=False)
    return render(request, 'church/members.html', {
        'members': members,
        'query': query,
        'active': active,
    })


@login_required
def events(request):
    query = request.GET.get('q', '').strip()
    events = Event.objects.order_by('start_time')
    if query:
        events = events.filter(
            Q(title__icontains=query)
            | Q(location__icontains=query)
            | Q(description__icontains=query)
        )
    upcoming_events = events.annotate(attendance_count=models.Count('attendance'))[:20]
    return render(request, 'church/events.html', {
        'events': upcoming_events,
        'query': query,
    })


@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    form = EventRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        member = form.cleaned_data['member']
        status = form.cleaned_data['status']
        event.attendance_set.update_or_create(
            member=member,
            defaults={'status': status},
        )
        return redirect(reverse('event_detail', args=[event.id]))
    volunteer_signups = event.volunteersignup_set.select_related('member').all()
    return render(request, 'church/event_detail.html', {
        'event': event,
        'form': form,
        'volunteer_signups': volunteer_signups,
    })


@login_required
@user_passes_test(is_church_volunteer)
def event_checkin(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    form = EventLocationCheckinForm(request.POST or None)
    member = None
    error = None
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data.get('email')
        phone = form.cleaned_data.get('phone')
        member_qs = Member.objects.filter(is_active=True)
        if email:
            member_qs = member_qs.filter(email__iexact=email)
        if phone:
            member_qs = member_qs.filter(phone__iexact=phone)
        member = member_qs.first()
        if not member:
            error = 'No active member found with that email or phone.'
        else:
            Attendance.objects.update_or_create(
                event=event,
                member=member,
                defaults={'status': f'Checked in at {event.location}'},
            )
            return redirect('event_detail', event_id=event.id)
    return render(request, 'church/event_checkin.html', {
        'event': event,
        'form': form,
        'error': error,
        'member': member,
    })


@login_required
@user_passes_test(is_church_volunteer)
def volunteer_signup(request, event_id=None, group_id=None):
    event = get_object_or_404(Event, pk=event_id) if event_id else None
    group = get_object_or_404(Group, pk=group_id) if group_id else None
    if request.method == 'POST':
        form = VolunteerSignupForm(request.POST)
        if form.is_valid():
            signup = form.save()
            if event:
                return redirect('event_detail', event_id=event.id)
            if group:
                return redirect('group_detail', group_id=group.id)
            return redirect('home')
    else:
        initial = {}
        if event:
            initial['event'] = event
        if group:
            initial['group'] = group
        form = VolunteerSignupForm(initial=initial)

    return render(request, 'church/volunteer_signup.html', {
        'form': form,
        'event': event,
        'group': group,
    })


@login_required
@user_passes_test(is_church_staff)
def event_attendance(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    members = Member.objects.filter(is_active=True).order_by('last_name', 'first_name')
    attended_ids = set(event.attendance_set.values_list('member_id', flat=True))
    if request.method == 'POST':
        selected_ids = {int(pk) for pk in request.POST.getlist('members')}
        for member in members:
            if member.id in selected_ids:
                Attendance.objects.update_or_create(
                    event=event,
                    member=member,
                    defaults={'status': 'Checked in'},
                )
            elif member.id in attended_ids:
                Attendance.objects.filter(event=event, member=member).delete()
        return redirect('event_detail', event_id=event.id)
    return render(request, 'church/event_attendance.html', {
        'event': event,
        'members': members,
        'attended_ids': attended_ids,
    })


@login_required
@user_passes_test(is_church_staff)
def event_form(request, event_id=None):
    event = get_object_or_404(Event, pk=event_id) if event_id else None
    form = EventForm(request.POST or None, instance=event)
    if request.method == 'POST' and form.is_valid():
        saved_event = form.save()
        return redirect('event_detail', event_id=saved_event.id)
    return render(request, 'church/event_form.html', {'form': form, 'event': event})


@login_required
def member_detail(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    donations = Donation.objects.filter(member=member).order_by('-donated_at')
    events = member.events.order_by('start_time')
    return render(request, 'church/member_detail.html', {
        'member': member,
        'donations': donations,
        'events': events,
        'groups': member.groups.all(),
    })


@login_required
@user_passes_test(is_church_staff)
def member_form(request, member_id=None):
    member = get_object_or_404(Member, pk=member_id) if member_id else None
    form = MemberForm(request.POST or None, instance=member)
    if request.method == 'POST' and form.is_valid():
        saved_member = form.save()
        return redirect('member_detail', member_id=saved_member.id)
    return render(request, 'church/member_form.html', {'form': form, 'member': member})


@login_required
def groups(request):
    groups = Group.objects.prefetch_related('leaders', 'members').order_by('name')
    return render(request, 'church/groups.html', {'groups': groups})


@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    volunteer_signups = group.volunteersignup_set.select_related('member').all()
    return render(request, 'church/group_detail.html', {
        'group': group,
        'volunteer_signups': volunteer_signups,
    })


@login_required
@user_passes_test(is_church_staff)
def reports(request):
    donation_stats = Donation.objects.values('donation_type').annotate(
        total=models.Sum('amount'),
        count=models.Count('id'),
    ).order_by('-total')
    event_attendance = Event.objects.annotate(
        attendance_count=models.Count('attendance'),
    ).order_by('-attendance_count')[:10]
    volunteer_by_role = VolunteerSignup.objects.values('role').annotate(
        count=models.Count('id'),
    ).order_by('-count')[:10]
    volunteer_by_event = VolunteerSignup.objects.filter(event__isnull=False).values('event__title').annotate(
        count=models.Count('id'),
    ).order_by('-count')[:10]
    volunteer_by_group = VolunteerSignup.objects.filter(group__isnull=False).values('group__name').annotate(
        count=models.Count('id'),
    ).order_by('-count')[:10]
    max_role = max((item['count'] for item in volunteer_by_role), default=0)
    max_event = max((item['count'] for item in volunteer_by_event), default=0)
    max_group = max((item['count'] for item in volunteer_by_group), default=0)
    return render(request, 'church/reports.html', {
        'donation_stats': donation_stats,
        'event_attendance': event_attendance,
        'volunteer_by_role': volunteer_by_role,
        'volunteer_by_event': volunteer_by_event,
        'volunteer_by_group': volunteer_by_group,
        'max_role': max_role,
        'max_event': max_event,
        'max_group': max_group,
    })


@login_required
@user_passes_test(is_church_staff)
def export_attendance_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Event', 'Member', 'Status', 'Checked in at', 'Event start'])

    attendances = Attendance.objects.select_related('event', 'member').order_by('event__start_time', 'member__last_name')
    for attendance in attendances:
        writer.writerow([
            attendance.event.title,
            str(attendance.member),
            attendance.status,
            attendance.checked_in_at,
            attendance.event.start_time,
        ])
    return response


@login_required
def donations(request):
    donations = Donation.objects.order_by('-donated_at')[:20]
    return render(request, 'church/donations.html', {'donations': donations})


@login_required
@user_passes_test(is_church_staff)
def add_donation(request):
    form = DonationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('donations')
    return render(request, 'church/add_donation.html', {'form': form})
