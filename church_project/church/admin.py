from django.contrib import admin

from .models import Address, Attendance, Donation, Event, Group, Member, VolunteerSignup


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('street', 'city', 'state', 'postal_code', 'country')
    search_fields = ('street', 'city', 'state', 'country')


class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'is_active')
    list_filter = ('is_active', 'gender')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    inlines = [AttendanceInline]


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('leaders', 'members')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'start_time', 'end_time')
    list_filter = ('start_time',)
    search_fields = ('title', 'location', 'description')
    inlines = [AttendanceInline]


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('member', 'amount', 'donated_at', 'donation_type')
    list_filter = ('donation_type', 'donated_at')
    search_fields = ('member__first_name', 'member__last_name', 'donation_type')


@admin.register(VolunteerSignup)
class VolunteerSignupAdmin(admin.ModelAdmin):
    list_display = ('member', 'group', 'event', 'role', 'status', 'signed_up_at')
    list_filter = ('status', 'group', 'event')
    search_fields = ('member__first_name', 'member__last_name', 'role')
