from django.conf import settings
from django.db import models


class Address(models.Model):
    street = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name_plural = 'Addresses'

    def __str__(self):
        parts = [self.street, self.city, self.state, self.postal_code, self.country]
        return ', '.join([part for part in parts if part])


class Member(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    birthday = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    address = models.ForeignKey(Address, null=True, blank=True, on_delete=models.SET_NULL)
    joined_at = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Group(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    leaders = models.ManyToManyField(Member, blank=True, related_name='leading_groups')
    members = models.ManyToManyField(Member, blank=True, related_name='groups')

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    attendees = models.ManyToManyField(Member, through='Attendance', blank=True, related_name='events')

    def __str__(self):
        return self.title


class Attendance(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    checked_in_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, blank=True)

    class Meta:
        unique_together = ('member', 'event')

    def __str__(self):
        return f'{self.member} - {self.event}'


class Donation(models.Model):
    member = models.ForeignKey(Member, null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    donated_at = models.DateTimeField(auto_now_add=True)
    donation_type = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        donor = self.member or 'Anonymous'
        return f'{donor} - {self.amount}'


class VolunteerSignup(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, null=True, blank=True, on_delete=models.SET_NULL)
    event = models.ForeignKey(Event, null=True, blank=True, on_delete=models.SET_NULL)
    role = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=50, default='Pending')
    signed_up_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-signed_up_at']

    def __str__(self):
        target = self.group or self.event or 'General'
        return f'{self.member} volunteering for {target}'
