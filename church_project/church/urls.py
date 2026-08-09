from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('members/', views.members, name='members'),
    path('members/add/', views.member_form, name='member_add'),
    path('members/<int:member_id>/', views.member_detail, name='member_detail'),
    path('members/<int:member_id>/edit/', views.member_form, name='member_edit'),
    path('events/', views.events, name='events'),
    path('events/add/', views.event_form, name='event_add'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/checkin/', views.event_checkin, name='event_checkin'),
    path('events/<int:event_id>/attendance/', views.event_attendance, name='event_attendance'),
    path('events/<int:event_id>/signup/', views.volunteer_signup, name='event_volunteer_signup'),
    path('events/<int:event_id>/edit/', views.event_form, name='event_edit'),
    path('groups/', views.groups, name='groups'),
    path('groups/<int:group_id>/', views.group_detail, name='group_detail'),
    path('groups/<int:group_id>/signup/', views.volunteer_signup, name='group_volunteer_signup'),
    path('reports/', views.reports, name='reports'),
    path('reports/attendance-export/', views.export_attendance_csv, name='export_attendance_csv'),
    path('donations/', views.donations, name='donations'),
    path('donations/add/', views.add_donation, name='add_donation'),
]
