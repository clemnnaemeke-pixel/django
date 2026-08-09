from django import forms

from .models import Donation, Event, Member, VolunteerSignup


class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['member', 'amount', 'donation_type', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class EventRegistrationForm(forms.Form):
    member = forms.ModelChoiceField(
        queryset=Member.objects.filter(is_active=True),
        label='Member',
        empty_label='Select a member',
    )
    status = forms.CharField(max_length=50, required=False, label='Attendance note')


class EventLocationCheckinForm(forms.Form):
    email = forms.EmailField(required=False, label='Member email')
    phone = forms.CharField(max_length=20, required=False, label='Member phone')

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        phone = cleaned_data.get('phone')
        if not email and not phone:
            raise forms.ValidationError('Provide either an email or phone number to check in.')
        return cleaned_data


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'location', 'start_time', 'end_time']


class VolunteerSignupForm(forms.ModelForm):
    class Meta:
        model = VolunteerSignup
        fields = ['member', 'group', 'event', 'role', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].required = False
        self.fields['event'].required = False
        self.fields['role'].required = False
        self.fields['status'].required = False


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'email', 'phone', 'birthday', 'gender', 'address', 'is_active', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
