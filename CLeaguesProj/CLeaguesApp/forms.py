from django import forms
from django.forms import ModelChoiceField
from django.forms import ValidationError
from django.core import validators
from django.contrib.admin.widgets import AdminDateWidget
from datetime import datetime, timedelta
from CLeaguesApp.models import *
from .st_classes import *

class strava_authFormClass(forms.Form):
    def void():
        return

class leagueFormClass(forms.ModelForm):
    lg_name = forms.CharField(widget=forms.TextInput, label="League Name", required=True,
                        error_messages={'unique': 'The League Name informed already exists in CycleLeagues.' })
    lg_pic = forms.ImageField(widget=forms.FileInput, label="Add a Picture to this League", required=False)

    # lg_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    # lg_activation_code = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    # lg_atl_creator = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    # lg_status = forms.CharField(widget=forms.HiddenInput(), required=False)
    # lg_creation_timestamp = forms.DateTimeField(widget=forms.HiddenInput(), required=False)
    # lg_inactivation_timestamp = forms.DateTimeField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = League
        fields = ('lg_name', 'lg_pic')

class SS_ModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return "{}".format(obj.ss_name)

class DateInput(forms.DateInput):
    input_type = 'date'

class tourFormClass(forms.ModelForm):
    tr_name = forms.CharField(widget=forms.TextInput, label="Tour Name", required=True)
    tr_start_date = forms.DateField(widget=DateInput(),
                    initial=datetime.now().date()+timedelta(days=5), label="Start Date", required=True)
    tr_finish_date = forms.DateField(widget=DateInput(),
                    initial=datetime.now().date()+timedelta(days=19),
                    label="Finish Date", required=True)
    tr_ss = SS_ModelChoiceField(queryset=ScoringSystem.objects.all(), label="Scoring System", required=True, to_field_name="ss_name")
    tr_pic = forms.ImageField(widget=forms.FileInput, label="Add a Picture to this Tour", required=False)

    class Meta:
        model = Tour
        fields = ('tr_name', 'tr_start_date', 'tr_finish_date', 'tr_ss', 'tr_pic')

    def is_valid(self, league):
        valid = super().is_valid()
        tr_name = self.cleaned_data['tr_name']
        # This is Creation
        if self.instance.pk == None:
            if Tour.objects.all().filter(tr_name = tr_name, tr_lg__lg_id = league.lg_id ):
                self.add_error('tr_name',"{} as Tour name was already used in the League {} !".format(tr_name, league.lg_name))
                return False
        # This is Update
        else:
            tour = Tour.objects.get(pk=self.instance.pk)
            if tour.tr_name != tr_name:
                if Tour.objects.all().filter(tr_name = tr_name, tr_lg__lg_id = league.lg_id ):
                    self.add_error('tr_name',"{} as Tour name was already used in the League {} !".format(tr_name, league.lg_name))
                    return False
        return valid

    def clean_tr_finish_date(self):
        tr_finish_date = self.cleaned_data['tr_finish_date']
        today = datetime.now().date()
        # Testing for Update
        if self.instance.pk != None:
            tour = Tour.objects.get(pk=self.instance.pk)
            if tour.is_running_bydate() and tr_finish_date < today:
                raise ValidationError('You cannot change the Finish Date from "{}" to a data in the past'.format(format(tour.tr_finish_date.strftime('%m/%d/%Y'))))
        return tr_finish_date

    def clean_tr_ss(self):
        # Its is update
        tr_ss = self.cleaned_data['tr_ss']
        # It is a update
        if self.instance.pk != None:
            tour = Tour.objects.get(pk=self.instance.pk)
            if tour.is_running_bydate() and tr_ss.ss_id != tour.tr_ss.ss_id :
                raise ValidationError('You cannot change the Scoring System from "{}" for a running Tour'.format(tour.tr_ss.ss_name))
        return tr_ss

    def clean_tr_start_date(self):
        tr_start_date = self.cleaned_data['tr_start_date']
        # Tests for Creation
        tomorrow = datetime.now().date()+timedelta(days=1)
        if self.instance.pk == None:
            if tr_start_date < tomorrow:
                raise ValidationError("Tour Start Date shall be in the future")
        # Tests for Update
        else:
            tour = Tour.objects.get(pk=self.instance.pk)
            if tour.is_running_bydate() :
                if tr_start_date != tour.tr_start_date:
                    raise ValidationError('You cannot change Start Date from "{}" for a Tour already running'.format(tour.tr_start_date.strftime('%m/%d/%Y')))
            else:
                if tr_start_date < tomorrow:
                    raise ValidationError('For changing Start Date from "{}", the new date shall be in the future'.format(tour.tr_start_date.strftime('%m/%d/%Y')))
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return tr_start_date

    def clean(self):
        cleaned_data = super(tourFormClass, self).clean()
        tr_start_date = cleaned_data.get("tr_start_date")
        tr_finish_date = cleaned_data.get("tr_finish_date")
        if tr_start_date and tr_finish_date:
            if self.instance.pk == None:
                if tr_finish_date <= tr_start_date:
                    raise ValidationError("Tour Finish Date shall be at least one day after Start Date")
                if tr_finish_date >= tr_start_date+timedelta(days=60):
                    raise ValidationError("Tour cannot exceed 60 days")
            else:
                if tr_finish_date >= tr_start_date+timedelta(days=60):
                    tour = Tour.objects.get(pk=self.instance.pk)
                    raise ValidationError('For changing Start Date from "{}" and Finish Date from "{}", the Tour cannot exceed 60 days'.format(tour.tr_start_date.strftime('%m/%d/%Y'),tour.tr_finish_date.strftime('%m/%d/%Y')))

class join_leagueFormClass(forms.Form):
    lg_activation_code = forms.IntegerField(widget=forms.NumberInput(), required=True,label="")
    league = ''
    request = ''

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(join_leagueFormClass, self).__init__(*args, **kwargs)

    def clean(self):
        print("Got in the Clean")
        cleaned_data = super(join_leagueFormClass, self).clean()
        lg_activation_code = cleaned_data.get('lg_activation_code')
        cleagues_authObj = get_cleagues_authObj(self.request)
        # print(lg_activation_code)
        if lg_activation_code:
            league_qs = League.objects.all().filter(lg_activation_code=lg_activation_code)
            if league_qs:
                league = league_qs[0]
                if league.lg_status == "I":
                    message = "The League {} was Inactivated by the creator. You cannot join it.".format(league.lg_name)
                    raise ValidationError(message)
                atl_in_league_qs = AtlInLeague.objects.all().filter(ail_atl__atl_id=cleagues_authObj.logged_cleagues_athlete.atl_id,
                                                   ail_lg__lg_id=league.lg_id )
                if atl_in_league_qs:
                    atl_in_league = atl_in_league_qs[0]
                    if atl_in_league.ail_status == "I":
                        message = "You have been Inactivated from the League {}. You cannot join it by yourself. Ask the League creator to do so.".format(league.lg_name)
                        raise ValidationError(message)
                    elif atl_in_league.ail_status == "A":
                        message = "Your are already taking part of the League {}.".format(league.lg_name)
                        raise ValidationError(message)
            else:
                message = "This is not an activation code from a existing League."
                raise ValidationError(message)
        self.league = league

class confirm_join_leagueFormClass(forms.Form):
    not_join_started_tour = forms.BooleanField(widget=forms.CheckboxInput(), required=False,label="I DON´T want to take part of already started Tours in this League")

class inact_leagueFormClass(forms.Form):
    i_am_aware = forms.BooleanField(widget=forms.CheckboxInput(), required=True,label="I am aware that this League can not be used or updated while it is Inactivated")

# class inact_tourFormClass(forms.Form):
#     i_am_aware = forms.BooleanField(widget=forms.CheckboxInput(), required=True,label="I am aware that this Tour can not be used or updated while it is Inactivated")

class search_athletesFormClass(forms.Form):
    atl_name_strava = forms.CharField(widget=forms.TextInput, label="Athlete Name", min_length=3, required=False)
    atl_city_strava = forms.CharField(widget=forms.TextInput, label="City Name", min_length=3, required=False)

    def clean(self):
        cleaned_data = super(search_athletesFormClass, self).clean()
        atl_name_strava = cleaned_data.get('atl_name_strava')
        atl_city_strava = cleaned_data.get('atl_city_strava')
        if not atl_name_strava and not atl_city_strava:
            message = "At least one search key shall be informed"
            raise ValidationError(message)
