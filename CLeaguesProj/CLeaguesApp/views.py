from django.shortcuts import render
from django.views.generic import View
from django import forms
from .forms import *
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from stravalib.client import Client
from .strava import *
from .st_classes import *
from .st_functions import *
from .models import *
from django.urls import reverse
from django.shortcuts import redirect
from urllib.parse import urlencode
from .email_notifications import *

LAST_ACTIVITIES = 20
DAYS_ACTIVITIES = 90

def general_context(request):
    cleagues_authObj = get_cleagues_authObj(request)
    context = {
        **cleagues_authObj.auth_context(),
    }
    # print(list_logged_cleagues)
    return context

# Decorator for Views accesses

def logged_user_required(func):
    def _wrapped_func(request, *args, **kwargs):
        httprequest = args[0]
        cleagues_authObj = get_cleagues_authObj(httprequest)
        if cleagues_authObj:
            if cleagues_authObj.logged_cleagues_athlete and cleagues_authObj.strava_authObj:
                if cleagues_authObj.logged_cleagues_athlete.atl_id and cleagues_authObj.strava_authObj.logged_strava_athlete:
                    return func(request, *args, **kwargs)
        return HttpResponseRedirect("/CLeaguesApp/main")
    return _wrapped_func

def exist_league(func):
    def _wrapped_func(request, *args, **kwargs):
        lg_id = args[0].GET.get('league')
        league_qs = League.objects.all().filter(lg_id=lg_id)
        if league_qs:
            kwargs['league'] = league_qs[0]
            return func(request, *args, **kwargs)
        else:
            base_url = "/CLeaguesApp/oops"
            query_string =  urlencode({'error': "NoLeague",
                                       'code' : lg_id })
            url = '{}?{}'.format(base_url, query_string)
            return HttpResponseRedirect(url)
    return _wrapped_func

def exist_tour(func):
    def _wrapped_func(request, *args, **kwargs):
        tr_id = args[0].GET.get('tour')
        tour_qs = Tour.objects.all().filter(tr_id=tr_id)

        if tour_qs:
            tour = tour_qs[0]
            if tour.tr_status != "X":
                kwargs['tour'] = tour_qs[0]
                return func(request, *args, **kwargs)

        base_url = "/CLeaguesApp/oops"
        query_string =  urlencode({'error': "NoTour",
                                   'code' : tr_id })
        url = '{}?{}'.format(base_url, query_string)
        return HttpResponseRedirect(url)
    return _wrapped_func

def exist_athlete(func):
    def _wrapped_func(request, *args, **kwargs):
        atl_id = args[0].GET.get('athlete')
        atl_qs = Athlete.objects.all().filter(atl_id=atl_id)
        if atl_qs:
            kwargs['athlete'] = atl_qs[0]
            return func(request, *args, **kwargs)
        else:
            base_url = "/CLeaguesApp/oops"
            query_string =  urlencode({'error': "NoAthlete",
                                       'code' : atl_id })
            url = '{}?{}'.format(base_url, query_string)
            return HttpResponseRedirect(url)
    return _wrapped_func

def permit_to_update_league(func):
    def _wrapped_func(request, *args, **kwargs):
        league = kwargs['league']
        httprequest = args[0]
        cleagues_authObj = get_cleagues_authObj(httprequest)
        logged_cleagues_athlete = cleagues_authObj.logged_cleagues_athlete
        if logged_cleagues_athlete.atl_id == league.lg_atl_creator.atl_id:
            return func(request, *args, **kwargs)
        else:
            base_url = "/CLeaguesApp/oops"
            query_string =  urlencode({'error': "NoLeagueUpdatePermit",
                                       'code' : lg_id })
            url = '{}?{}'.format(base_url, query_string)
            return HttpResponseRedirect(url)
    return _wrapped_func

def permit_to_update_athlete(func):
    def _wrapped_func(request, *args, **kwargs):
        athlete = kwargs['athlete']
        httprequest = args[0]
        cleagues_authObj = get_cleagues_authObj(httprequest)
        logged_cleagues_athlete = cleagues_authObj.logged_cleagues_athlete
        if logged_cleagues_athlete.atl_id == athlete.atl_id:
            return func(request, *args, **kwargs)
        else:
            base_url = "/CLeaguesApp/oops"
            query_string =  urlencode({'error': "NoAthleteUpdatePermit",
                                       'code' : athlete.atl_id })
            url = '{}?{}'.format(base_url, query_string)
            return HttpResponseRedirect(url)
    return _wrapped_func

def permit_to_update_tour(func):
    def _wrapped_func(request, *args, **kwargs):
        tour = kwargs['tour']
        httprequest = args[0]
        cleagues_authObj = get_cleagues_authObj(httprequest)
        logged_cleagues_athlete = cleagues_authObj.logged_cleagues_athlete
        if logged_cleagues_athlete.atl_id == tour.tr_lg.lg_atl_creator.atl_id:
            return func(request, *args, **kwargs)
        else:
            base_url = "/CLeaguesApp/oops"
            query_string =  urlencode({'error': "NoTourUpdatePermit",
                                       'code' : tour.tr_id })
            url = '{}?{}'.format(base_url, query_string)
            return HttpResponseRedirect(url)
    return _wrapped_func

def permit_to_see_league(func):
    def _wrapped_func(request, *args, **kwargs):
        league = kwargs['league']
        httprequest = args[0]
        cleagues_authObj = get_cleagues_authObj(httprequest)
        logged_cleagues_athlete = cleagues_authObj.logged_cleagues_athlete

        # if the League is Inactive only the League Creator can see its details
        if league.lg_status == "I":
            if league.lg_atl_creator.atl_id == logged_cleagues_athlete.atl_id:
                return func(request, *args, **kwargs)
        else:
            # If the League is Active, the Athlete can see the League details only if he is active in the League
            atl_in_league_qs = AtlInLeague.objects.all().filter(ail_atl__atl_id = logged_cleagues_athlete.atl_id,
                                                                ail_lg__lg_id = league.lg_id)
            if atl_in_league_qs:
                if atl_in_league_qs[0].ail_status == "A":
                    return func(request, *args, **kwargs)

        base_url = "/CLeaguesApp/oops"
        query_string =  urlencode({'error': "NoLeagueSeePermit",
                                   'code' : league.lg_id })
        url = '{}?{}'.format(base_url, query_string)
        return HttpResponseRedirect(url)
    return _wrapped_func

def permit_to_see_tour(func):
    def _wrapped_func(request, *args, **kwargs):
        tour = kwargs['tour']
        httprequest = args[0]
        cleagues_authObj = get_cleagues_authObj(httprequest)
        logged_cleagues_athlete = cleagues_authObj.logged_cleagues_athlete

        if logged_cleagues_athlete.can_see_tour(tour):
            return func(request, *args, **kwargs)
        else:
            base_url = "/CLeaguesApp/oops"
            query_string =  urlencode({'error': "NoTourSeePermit",
                                       'code' : tour.tr_id })
            url = '{}?{}'.format(base_url, query_string)
            return HttpResponseRedirect(url)
    return _wrapped_func

# View Classes

class oopsViewClass(View):
    def get(self, request, *args, **kwargs):
        message = ''
        error = request.GET.get('error')
        if error == "NoLeague":
            message = "The League you have informed in the URL does no exist"
        elif error == "NoTour":
            message = "The Tour you have informed in the URL does no exist"
        elif error == "NoAthlete":
            message = "The Athlete you have informed in the URL does no exist"
        elif error == "NoLeagueUpdatePermit":
            message = "You cannot update this League, since you are not the creator of it"
        elif error == "NoTourUpdatePermit":
            message = "You cannot update this Tour, since you are not the creator of it"
        elif error == "NoAthleteUpdatePermit":
            message = "You cannot update this Athlete, since you are not him/her"
        elif error == "NoLeagueSeePermit":
            message = "You cannot see the League you have informed in the URL, since you do not belong to it"
        elif error == "NoTourSeePermit":
            message = "You cannot see the Tour you have informed in the URL, since you do not belong to its League"
        context = { **general_context(request),
                    'message' : message }
        return render(request, "CLeaguesApp/oops.html", context=context)

class indexViewClass(View):
    def get(self, request, *args, **kwargs):
        cleagues_authObj = get_cleagues_authObj(request)

        # print("I am in index GET")

        if request.path.find('logout') != -1 :
            cleagues_authObj.logout(request)
        elif request.path.find('authorization') != -1 :
            atl_strava_code = request.GET.get('code')
            cleagues_authObj.logout(request)

            # Cleagues will log in Strava
            # The strava athlete objected will be created inside cleagues_authObj
            cleagues_authObj.login(atl_strava_code,request)

            # If it was possible to get the Athlete Id from Strava
            # (It means the code returned by Strava is valid)
            # Try to the log Athlete from CLeagues database
            if cleagues_authObj.strava_authObj.logged_strava_atl_id:
                # print(cleagues_authObj.strava_authObj.logged_strava_atl_id)

                # If the athlete is not registered in CLeagues database
                # Start the registering process
                if not cleagues_authObj.logged_cleagues_athlete :
                    # print("I will go to register_page")
                    return HttpResponseRedirect("/CLeaguesApp/register_page/")
                else:
                    # print("I am a user already registered. Let's begin using it")
                    # print(cleagues_authObj.logged_cleagues_athlete)
                    cleagues_authObj.get_updated_atl_stat()
                    # return render(request, "CLeaguesApp/index.html", context=general_context(request))
                    return HttpResponseRedirect("/CLeaguesApp/tours_feed/")
        else:
            cleagues_authObj.logout(request)
            # print("I logged out completely")
        # print("I am getting out of Index GET")
        context = { **general_context(request), }
        return render(request, "CLeaguesApp/index.html", context=context)

    def post(self, request, *args, **kwargs):
        cleagues_authObj = get_cleagues_authObj(request)

        # print("I am in index POST")
        strava_authForm=strava_authFormClass(request.POST)
        if strava_authForm.is_valid():
            return HttpResponseRedirect(cleagues_authObj.strava_authObj.get_strava_url(request))
        context = { **general_context(request), }
        return render(request, "CLeaguesApp/index.html", context=context)

class leagues_feedViewClass(View):

    @logged_user_required
    def get(self, request, *args, **kwargs):
        list_atl_leagues = []
        list_atl_leagues_updated = []
        cleagues_authObj = get_cleagues_authObj(request)
        if cleagues_authObj.logged_cleagues_athlete:
            list_atl_leagues = cleagues_authObj.logged_cleagues_athlete.get_leagues()
        for league in list_atl_leagues:
            league_feed = league_feedClass()
            league_feed.league = league
            league_feed.summary = league.get_summary()
            atl_in_league_qs = AtlInLeague.objects.all().filter(ail_atl__atl_id = cleagues_authObj.logged_cleagues_athlete.atl_id,
                                                             ail_lg__lg_id = league.lg_id)
            if atl_in_league_qs:
                league_feed.logged_cleagues_atl_league_status = atl_in_league_qs[0].ail_status
            else:
                league_feed.logged_cleagues_atl_league_status = "I"
            list_atl_leagues_updated.append(league_feed)
        if cleagues_authObj.logged_cleagues_athlete.are_pending_invites():
            notification = "There are pending League inviations waiting for your decision"
        else:
            notification = ''
        if request.path.find('invite') != -1 :
            invite_view =  True
        else:
            invite_view = False
        context = { 'list_leagues_feed' : list_atl_leagues_updated,
                    'notification' : notification,
                    'invite_view' : invite_view,
                    **general_context(request) }
        return render(request, "CLeaguesApp/leagues_feed.html", context=context)

class register_pageViewClass(View):
    def get(self, request, *args, **kwargs):
        context = { **general_context(request), }
        return render(request, "CLeaguesApp/register_page.html", context=context)

    def post(self, request, *args, **kwargs):
        # print("I am in register_page POST")
        cleagues_authObj = get_cleagues_authObj(request)
        cleagues_authObj.logged_cleagues_athlete = Athlete()
        cleagues_authObj.logged_cleagues_athlete.set_at_creation()
        cleagues_authObj.logged_cleagues_athlete.update_from_strava(cleagues_authObj.strava_authObj)
        cleagues_authObj.logged_cleagues_athlete.download_pic_from_strava(cleagues_authObj.strava_authObj, "L")
        cleagues_authObj.logged_cleagues_athlete.download_pic_from_strava(cleagues_authObj.strava_authObj, "M")
        cleagues_authObj.logged_cleagues_athlete.save()

        # Login again, but now update the cleagues athelete date
        cleagues_authObj.login(cleagues_authObj.strava_authObj.atl_strava_code,request)

        context = { **general_context(request), }
        return render(request, "CLeaguesApp/register_page.html", context=context)

class invite_athletesViewClass(View):
    list_select_athletes = []

    @logged_user_required
    @exist_league
    @permit_to_update_league
    def get(self, request, *args, **kwargs):
        league = kwargs['league']
        list_athletes_league = league.get_athletes_in_league()
        # list_main_atl_source = Athlete.objects.all()
        # list_select_athletes = filter_athletes(list_main_atl_source,
        #                                         [atl_in_league.atl for atl_in_league in list_athletes_league])
        invite_athletesViewClass.list_select_athletes = []
        search_atl_form = search_athletesFormClass()
        context = { **general_context(request),
                    'list_athletes_league' : list_athletes_league,
                    'list_select_athletes' : invite_athletesViewClass.list_select_athletes,
                    'league' : league,
                    'search_atl_form': search_atl_form}
        return render(request, "CLeaguesApp/invite_athletes.html", context=context)

    @logged_user_required
    @exist_league
    @permit_to_update_league
    def post(self, request, *args, **kwargs):
        league = kwargs['league']
        list_athletes_league = league.get_athletes_in_league()
        # list_select_athletes = []
        # search_atl_form = search_athletesFormClass()
        if request.POST.get("btn_search_atl"):
            search_atl_form = search_athletesFormClass(request.POST, request.FILES)
            if search_atl_form.is_valid():
                atl_name_strava = search_atl_form.cleaned_data.get('atl_name_strava')
                atl_city_strava = search_atl_form.cleaned_data.get('atl_city_strava')
                if atl_name_strava and not atl_city_strava:
                    list_main_atl_source = Athlete.objects.all().filter(atl_name_strava__icontains=atl_name_strava)
                elif not atl_name_strava and atl_city_strava:
                    list_main_atl_source = Athlete.objects.all().filter(atl_city_strava__icontains=atl_city_strava)
                elif atl_name_strava and atl_city_strava:
                    list_main_atl_source = Athlete.objects.all().filter(atl_name_strava__icontains=atl_name_strava,
                                                                        atl_city_strava__icontains=atl_city_strava)
                else:
                    list_main_atl_source = []
                invite_athletesViewClass.list_select_athletes = filter_athletes(list_main_atl_source,
                                                    [atl_in_league_ext.atl for atl_in_league_ext in list_athletes_league])
            else:
                invite_athletesViewClass.list_select_athletes = []
        elif request.POST.get("btn_add_selected_atl"):

            # Get the list of Athlete Ids selected by the user
            list_add_atl_id = request.POST.getlist('dual-list-options[]')

            # Check if any athlete were selected by thw user
            if list_add_atl_id :

                # print('some athletes were selected')
                # for i in list_add_atl_id:
                #     print(i)

                # Get a list of athletes based on the athlete Ids selected by the user
                list_add_atls = [atl for atl in invite_athletesViewClass.list_select_athletes if str(atl.atl_id) in list_add_atl_id]
                for atl in list_add_atls:
                    # print(atl.atl_name_strava)
                    atl_in_league = AtlInLeague()
                    atl_in_league.set_at_creation(atl, league, "C")
                    atl_in_league.save()
                    event_record = EventRecord()
                    event_record.create_record_league_invitation_notification(atl, league)
                    atl_in_league_ext = athlete_in_league_extClass()
                    atl_in_league_ext.atl = atl_in_league.ail_atl
                    atl_in_league_ext.atl_in_league_status = atl_in_league.ail_status
                    list_athletes_league.append(atl_in_league_ext)
                # list_select_athletes = filter_athletes(list_main_atl_source,
                #                                 [atl_in_league_ext.atl for atl_in_league_ext in list_athletes_league])
                base_url = "/CLeaguesApp/invite_athletes"
                query_string =  urlencode({'league': league.lg_id})
                url = '{}?{}'.format(base_url, query_string)
                return HttpResponseRedirect(url)
            search_atl_form = search_athletesFormClass()
        else:
            search_atl_form = search_athletesFormClass()
        context = { **general_context(request),
                        'list_athletes_league' : list_athletes_league,
                        'list_select_athletes' : invite_athletesViewClass.list_select_athletes,
                        'league' : league,
                        'search_atl_form' : search_atl_form}
        return render(request, "CLeaguesApp/invite_athletes.html", context=context)

class create_leagueViewClass(View):

    @logged_user_required
    def get(self, request, *args, **kwargs):
        league_form = leagueFormClass()
        context = { **general_context(request) ,
                    'league_form': league_form }
        return render(request, "CLeaguesApp/create_league.html", context=context)

    @logged_user_required
    def post(self, request, *args, **kwargs):
        league_form = leagueFormClass(request.POST, request.FILES)
        cleagues_authObj = get_cleagues_authObj(request)

        # Check to see form is valid
        if league_form.is_valid() :
            league = league_form.save(commit=False)

            # Check if they provided a profile picture
            if request.FILES:
                league.lg_pic = request.FILES['lg_pic']

            if league.lg_pic:
                # print("I got a picture")
                league.lg_pic = resize_image(league.lg_pic,162)
            # else:
            #     print("I did not got a picture")

            league.set_at_creation(cleagues_authObj.logged_cleagues_athlete)
            league.save()

            atl_in_league = AtlInLeague()
            atl_in_league.set_at_creation(cleagues_authObj.logged_cleagues_athlete,league, "A")
            atl_in_league.save()

            cleagues_authObj.get_updated_atl_stat()

            base_url = "/CLeaguesApp/league_details"
            query_string =  urlencode({'league': league.lg_id})
            url = '{}?{}'.format(base_url, query_string)
            # print(url)
            return HttpResponseRedirect(url)
        # else:
        #     # print(league_form.errors)

        context = { **general_context(request) ,
                    'league_form': league_form }
        return render(request, "CLeaguesApp/create_league.html", context=context)

class create_tourViewClass(View):

    @logged_user_required
    @exist_league
    @permit_to_update_league
    def get(self, request, *args, **kwargs):
        league = kwargs['league']
        tour_form = tourFormClass()
        original_tr_id = request.GET.get('original_tour')
        original_tour = ''
        if original_tr_id:
            original_tour_qs = Tour.objects.all().filter(tr_id=original_tr_id)
            if original_tour_qs:
                original_tour = original_tour_qs[0]
                tour_form = tourFormClass(None, instance=original_tour, initial = {'tr_ss': original_tour.tr_ss,
                                                                         'tr_name' : original_tour.tr_name + " - copy",
                                                                         'tr_start_date' : datetime.now().date()+timedelta(days=5),
                                                                         'tr_finish_date' : datetime.now().date()+timedelta(days=19), })
        context = { **general_context(request),
                    'tour_form' : tour_form,
                    'league' : league,
                    'original_tour' : original_tour  }
        return render(request, "CLeaguesApp/create_tour.html", context=context)
        context = { **general_context(request), }

    @logged_user_required
    @exist_league
    @permit_to_update_league
    def post(self, request, *args, **kwargs):
        league = kwargs['league']
        original_tr_id = request.GET.get('original_tour')
        original_tour = ''
        if original_tr_id:
            original_tour_qs = Tour.objects.all().filter(tr_id=original_tr_id)
            if original_tour_qs:
                original_tour = original_tour_qs[0]
        tour_form = tourFormClass(request.POST, request.FILES)
        cleagues_authObj = get_cleagues_authObj(request)
        if tour_form.is_valid(league):
            tour = tour_form.save(commit=False)

            # Check if they provided a profile picture
            if request.FILES:
                tour.tr_pic = request.FILES['tr_pic']

            if tour.tr_pic:
                # print("I got a picture")
                tour.tr_pic = resize_image(tour.tr_pic,162)
            # else:
            #     print("I did not got a picture")

            tour.set_at_creation(league, cleagues_authObj.logged_cleagues_athlete)
            tour.save()

            # Include all the athletes from the League in this Tour
            list_athletes_in_league = tour.tr_lg.get_athletes_in_league()
            for atl_in_league in list_athletes_in_league:
                # Check if the athlete is active and the Athlete is active in the league
                if atl_in_league.atl.atl_status == "A" and atl_in_league.atl_in_league_status == "A":
                    atlintour = AtlInTour()
                    atlintour.set_at_creation(atl_in_league.atl, tour)
                    atlintour.save()
                    event_record = EventRecord()
                    event_record.create_record_tour_creation_notification(atl_in_league.atl, tour)

            if original_tr_id:
                tour.clone_segments(original_tour)

            cleagues_authObj.get_updated_atl_stat()

            base_url = "/CLeaguesApp/tour_details_segments"
            query_string =  urlencode({'tour': tour.tr_id,
                                       'select' : "NoSelection"})
            url = '{}?{}'.format(base_url, query_string)
            # print(url)
            return HttpResponseRedirect(url)
        context = { **general_context(request),
                    'tour_form' : tour_form,
                    'league' : league,
                    'original_tour' : original_tour,
                    }
        return render(request, "CLeaguesApp/create_tour.html", context=context)

class tour_details_segmentsViewClass(View):
    list_act_full_segments = []
    list_act_full_segments_last_date = datetime.now().date()

    @logged_user_required
    @exist_tour
    @permit_to_see_tour
    def get(self, request, *args, **kwargs):

        select = request.GET.get('select')
        tour = kwargs['tour']
        cleagues_authObj = get_cleagues_authObj(request)

        # Get the status of the logged Athlete in the League of this Tour
        atl_in_league_status = AtlInLeague.objects.all().filter(ail_atl__atl_id = cleagues_authObj.logged_cleagues_athlete.atl_id,
                                                                ail_lg__lg_id = tour.tr_lg.lg_id)[0].ail_status

        # Get the list of all Athletes in this Tour
        list_atl_in_tour = list(AtlInTour.objects.all().filter(ait_tr__tr_id = tour.tr_id))

        # Get the Atl in Tour object for the logged Athlete
        logged_atl_in_tour = [atl_in_tour for atl_in_tour in list_atl_in_tour if atl_in_tour.ait_atl.atl_id == cleagues_authObj.logged_cleagues_athlete.atl_id]

        # Get all segments that can be selected according to the view chosen (NoSelection, FromLeague, FromActivies)
        list_select_segments = tour_details_segmentsViewClass.get_full_segments(tour,select,cleagues_authObj)

        # Get all segments in this Tour
        list_tour_segments = tour.get_segments()

        # Don't offer to select segments already in the Tour
        list_id_strava_tour_segments = [seg.sg_id_strava for seg in list_tour_segments]
        list_select_segments = [seg for seg in list_select_segments if seg.sg_id_strava not in list_id_strava_tour_segments]

        # Get the best trials of each segment in this Tour
        list_best_trial_tour_feed = tour.get_best_trial_feed()

        context = { **general_context(request),
                    'view' : "Segments",
                    'tour' : tour ,
                    **tour.get_summary(),
                    'list_tour_segments' : list_tour_segments,
                    'select' : select,
                    'list_select_segments' : list_select_segments,
                    'list_best_trial_tour_feed' : list_best_trial_tour_feed,
                    'atl_in_league_status' : atl_in_league_status,
                    'logged_atl_in_tour' : logged_atl_in_tour[0],
                   }
        return render(request, "CLeaguesApp/tour_details_segments.html", context=context)

    @logged_user_required
    @exist_tour
    @permit_to_update_tour
    def post(self, request, *args, **kwargs):
        # print("I am in POST tour details")

        tour = kwargs['tour']
        cleagues_authObj = get_cleagues_authObj(request)

        # # Get the status of the logged Athlete in the League of this Tour
        # atl_in_league_status = AtlInLeague.objects.all().filter(ail_atl__atl_id = cleagues_authObj.logged_cleagues_athlete.atl_id,
        #                                                         ail_lg__lg_id = tour.tr_lg.lg_id)[0].ail_status
        #
        # # Get the list of all Athletes in this Tour
        # list_atl_in_tour = list(AtlInTour.objects.all().filter(ait_tr__tr_id = tour.tr_id))
        #
        # # Get the Atl in Tour object for the logged Athlete
        # logged_atl_in_tour = [atl_in_tour for atl_in_tour in list_atl_in_tour if atl_in_tour.ait_atl.atl_id == cleagues_authObj.logged_cleagues_athlete.atl_id]

        sg_id = request.GET.get('delete')
        select = request.GET.get('select')

        # print(sg_id)
        # print(select)

        # Get the full list from CycleLeagues Segments that can be selected in this view, as defined by 'select'
        list_select_segments = tour_details_segmentsViewClass.get_full_segments(tour,select,cleagues_authObj)

        if sg_id:
            tour.delete_segment(sg_id)
            # base_url = "/CLeaguesApp/tour_details_segments"
            # query_string =  urlencode({'tour': tour.tr_id,
            #                            'select' : select})
            # url = '{}?{}'.format(base_url, query_string)
            # return HttpResponseRedirect(url)
        elif request.POST.get("button-add-select"):
            # Get the list of Strava Ids selected by the user
            list_add_segments_id_strava = request.POST.getlist('dual-list-options[]')

            # Check if any segment were selected by the user
            if list_add_segments_id_strava:

                # Obtain the Segment objects based on the Ids selected in the HTML

                list_add_segments = [seg for seg in list_select_segments if str(seg.sg_id_strava) in list_add_segments_id_strava]
                for seg_in_list in list_add_segments:

                    seg_in_bd_queryset = Segment.objects.filter(sg_id_strava=seg_in_list.sg_id_strava)

                    # Check if the strava segment is already registered in CycleLeagues
                    if not seg_in_bd_queryset:
                        # Save in CLeagues DB a new segment
                        seg_in_list.set_at_creation()
                        seg_in_list.save()
                        seg_in_bd = seg_in_list
                    else:
                        seg_in_bd = seg_in_bd_queryset[0]

                    # Add the selected segment in the Tour
                    segintour = SegInTour()
                    segintour.set_at_creation(seg_in_bd, tour)
                    segintour.save()

        base_url = "/CLeaguesApp/tour_details_segments"
        query_string =  urlencode({'tour': tour.tr_id,
                                   'select' : select})
        url = '{}?{}'.format(base_url, query_string)
        return HttpResponseRedirect(url)

        # list_tour_segments = tour.get_segments()
        #
        # # Don't offer to select segments already in the Tour
        # list_id_strava_tour_segments = [seg.sg_id_strava for seg in list_tour_segments]
        # list_select_segments = [seg for seg in list_select_segments if seg.sg_id_strava not in list_id_strava_tour_segments]
        #
        # list_best_trial_tour_feed = tour.get_best_trial_feed()
        #
        # context = { **general_context(request),
        #             'view' : "Segments",
        #             'tour' : tour ,
        #             **tour.get_summary(),
        #             'list_tour_segments' : list_tour_segments,
        #             'select' : select,
        #             'list_select_segments': list_select_segments,
        #             'list_best_trial_tour_feed' : list_best_trial_tour_feed,
        #             'atl_in_league_status' : atl_in_league_status,
        #             'logged_atl_in_tour' : logged_atl_in_tour[0],
        #             }
        # return render(request, "CLeaguesApp/tour_details_segments.html", context=context)

    def get_full_segments(tour,select,cleagues_authObj):
        if select == "FromLeague":
            # print("FromLeague")
            league = tour.tr_lg
            tour_details_segmentsViewClass.list_league_full_segments = list(set(league.get_segments()))
            return tour_details_segmentsViewClass.list_league_full_segments
        elif select == "FromActivities":
            today = datetime.now().date()
            # If the segments from Activities were selected before is not necessary to get back to and obtain it again from strava
            if (not tour_details_segmentsViewClass.list_act_full_segments or
                            tour_details_segmentsViewClass.list_act_full_segments_last_date < today) :
                # print("I am getting a new full activity list")
                today = datetime.now().date()
                if cleagues_authObj.logged_cleagues_athlete.atl_id == 1:
                    # days = 500
                    # last = None
                    days = DAYS_ACTIVITIES
                    last = LAST_ACTIVITIES
                else:
                    days = DAYS_ACTIVITIES
                    last = LAST_ACTIVITIES
                first_date = today - timedelta(days=days)
                # print(today)
                # print(first_date)
                list_last_efforts = cleagues_authObj.strava_authObj.get_atl_last_efforts(last,first_date,today)
                list_strava_segments = strava_authClass.get_unique_segments_from_efforts(list_last_efforts)
                tour_details_segmentsViewClass.list_act_full_segments = Segment.convert_list_segments(list_strava_segments)
            return tour_details_segmentsViewClass.list_act_full_segments
        elif select == "FromAll":
            # print("I got here to get all!")
            return Segment.objects.all()
        return []

class delete_tourViewClass(View):
    @logged_user_required
    @exist_tour
    @permit_to_update_tour
    def get(self, request, *args, **kwargs):
        tour = kwargs['tour']
        list_tour_segments = tour.get_segments()
        cleagues_authObj = get_cleagues_authObj(request)
        atl_in_league_status = AtlInLeague.objects.all().filter(ail_atl__atl_id = cleagues_authObj.logged_cleagues_athlete.atl_id,
                                                                ail_lg__lg_id = tour.tr_lg.lg_id)[0].ail_status
        list_atl_in_tour = list(AtlInTour.objects.all().filter(ait_tr__tr_id = tour.tr_id))
        logged_atl_in_tour = [atl_in_tour for atl_in_tour in list_atl_in_tour if atl_in_tour.ait_atl.atl_id == cleagues_authObj.logged_cleagues_athlete.atl_id]
        context = { **general_context(request),
                    'view' : "Segments",
                    'tour' : tour ,
                    **tour.get_summary(),
                    'list_tour_segments' : list_tour_segments,
                    'list_best_trial_tour_feed' : [],
                    'atl_in_league_status' : atl_in_league_status,
                    'logged_atl_in_tour' : logged_atl_in_tour[0],
                    'dont_edit' : True,
                   }
        return render(request, "CLeaguesApp/delete_tour.html", context=context)

    @logged_user_required
    @exist_tour
    @permit_to_update_tour
    def post(self, request, *args, **kwargs):
        tour = kwargs['tour']
        cleagues_authObj = get_cleagues_authObj(request)
        if request.POST.get("btn_delete_tour"):
            # print("dentro")
            tour.delete()
            cleagues_authObj.get_updated_atl_stat()
        # print("fora")
        base_url = "/CLeaguesApp/league_details"
        query_string =  urlencode({'league': tour.tr_lg.lg_id})
        url = '{}?{}'.format(base_url, query_string)
        return HttpResponseRedirect(url)

class join_leagueViewClass(View):
    @logged_user_required
    def get(self, request, *args, **kwargs):
        join_league_form = join_leagueFormClass()
        context = { **general_context(request),
                    'join_league_form' : join_league_form,
                }
        return render(request, "CLeaguesApp/join_league.html", context=context)

    @logged_user_required
    def post(self, request, *args, **kwargs):
        join_league_form = join_leagueFormClass(data=request.POST, request=request)
        if join_league_form.is_valid():
            league = join_league_form.league
            base_url = "/CLeaguesApp/confirm_join_league"
            query_string = urlencode({'league': league.lg_id})
            url = '{}?{}'.format(base_url, query_string)
            return HttpResponseRedirect(url)

        # print(message)
        context = { **general_context(request),
                    'join_league_form' : join_league_form,
                    }
        return render(request, "CLeaguesApp/join_league.html", context=context)

def get_league_context(ext_league_form,league, request):
        list_athletes_league = league.get_athletes_in_league()
        list_tours_league = league.get_tours()
        cleagues_authObj = get_cleagues_authObj(request)
        if league.lg_atl_creator.atl_id == cleagues_authObj.logged_cleagues_athlete.atl_id:
            league_admin = True
        else:
            league_admin = False
        return { **general_context(request) ,
                    'list_athletes_league' : list_athletes_league,
                    'list_tours_league' : list_tours_league,
                    'league' : league,
                    'league_admin' : league_admin,
                    'ext_league_form' : ext_league_form, }

class league_detailsViewClass(View):

    @logged_user_required
    @exist_league
    @permit_to_see_league
    def get(self, request, *args, **kwargs):
        league = kwargs['league']
        context = {
            **get_league_context('',league,request),
            'editable' : True,
        }
        return render(request, "CLeaguesApp/league_details.html", context=context)

class confirm_join_leagueViewClass(View):
    @logged_user_required
    @exist_league
    def get(self, request, *args, **kwargs):
        league = kwargs['league']
        confirm_join_league_form = confirm_join_leagueFormClass(request.POST)
        context = {
            **get_league_context(confirm_join_league_form,league, request),
            'editable' : False,
        }
        return render(request, "CLeaguesApp/confirm_join_league.html", context=context)

    @logged_user_required
    @exist_league
    def post(self, request, *args, **kwargs):
        league = kwargs['league']
        confirm_join_league_form = confirm_join_leagueFormClass(request.POST)
        cleagues_authObj = get_cleagues_authObj(request)
        context = {
            **get_league_context(confirm_join_league_form,league, request),
            'editable' : False,
        }
        if request.POST.get("btn_join_league"):
            # print("The Join button was chosen")
            if confirm_join_league_form.is_valid():

                cleagues_authObj.logged_cleagues_athlete.join_league(league,confirm_join_league_form.cleaned_data.get('not_join_started_tour'))
                cleagues_authObj.get_updated_atl_stat()

                base_url = "/CLeaguesApp/league_details"
                query_string =  urlencode({'league': league.lg_id})
                url = '{}?{}'.format(base_url, query_string)
                # print(url)
                return HttpResponseRedirect(url)
        elif request.POST.get("btn_dismiss_league"):
            cleagues_authObj.logged_cleagues_athlete.dismiss_league_invitation(league)
            return HttpResponseRedirect("/CLeaguesApp/leagues_feed")
        return render(request, "CLeaguesApp/confirm_join_league.html", context=context)

class inact_leagueViewClass(View):
    @logged_user_required
    @exist_league
    @permit_to_update_league
    def get(self, request, *args, **kwargs):
        league = kwargs['league']
        context = {
            **get_league_context('',league, request),
            'editable' : False,
        }
        return render(request, "CLeaguesApp/inact_league.html", context=context)

    @logged_user_required
    @exist_league
    @permit_to_update_league
    def post(self, request, *args, **kwargs):
        league = kwargs['league']
        cleagues_authObj = get_cleagues_authObj(request)
        context = {
            **get_league_context('',league, request),
            'editable' : False,
        }
        if request.POST.get("btn_inact_league"):
            # print("The Inact button was chosen")
            league = context['league']
            if league:
                league.inactivate()
                cleagues_authObj.get_updated_atl_stat()
                return HttpResponseRedirect("/CLeaguesApp/leagues_feed")
        return render(request, "CLeaguesApp/inact_league.html", context=context)

class react_leagueViewClass(View):

    @logged_user_required
    @exist_league
    @permit_to_update_league
    def get(self, request, *args, **kwargs):
        league = kwargs['league']
        context = {
            **get_league_context('',league, request),
            'editable' : False,
        }
        return render(request, "CLeaguesApp/react_league.html", context=context)

    @logged_user_required
    @exist_league
    @permit_to_update_league
    def post(self, request, *args, **kwargs):
        league = kwargs['league']
        cleagues_authObj = get_cleagues_authObj(request)
        context = {
            **get_league_context('',league, request),
            'editable' : False,
        }
        if request.POST.get("btn_react_league"):
            # print("The React button was chosen")
            league = context['league']
            if league:
                # print("Here I will reactivate the League")
                league.reactivate()
                cleagues_authObj.get_updated_atl_stat()
                return HttpResponseRedirect("/CLeaguesApp/leagues_feed")
        return render(request, "CLeaguesApp/react_league.html", context=context)

class tours_feedViewClass(View):

    @logged_user_required
    def get(self, request, *args, **kwargs):
        # print("Entrei in Get")
        cleagues_authObj = get_cleagues_authObj(request)
        list_tours_feed = cleagues_authObj.logged_cleagues_athlete.get_tours_feed()
        # print("Sai do get tours feed")
        if cleagues_authObj.logged_cleagues_athlete.are_pending_invites():
            notification = "There are pending League inviations waiting for your decision"
        else:
            notification = ''
        context = { **general_context(request),
                    'list_tours_feed' : list_tours_feed,
                    'notification' : notification, }
        # print("Vou entrar no render")
        return render(request, "CLeaguesApp/tours_feed.html", context=context)

class tour_details_rankViewClass(View):
    @logged_user_required
    @exist_tour
    @permit_to_see_tour
    def get(self, request, *args, **kwargs):
        tour = kwargs['tour']
        cleagues_authObj = get_cleagues_authObj(request)

        list_atl_in_tour = list(AtlInTour.objects.all().filter(ait_tr__tr_id = tour.tr_id))
        list_atl_in_tour.sort(key=lambda x: x.ait_rank, reverse=False)
        total_seg_in_tour = len(SegInTour.objects.all().filter(sit_tr__tr_id = tour.tr_id))
        list_best_trial_tour_feed = tour.get_best_trial_feed()
        atl_in_league_status = AtlInLeague.objects.all().filter(ail_atl__atl_id = cleagues_authObj.logged_cleagues_athlete.atl_id,
                                                                ail_lg__lg_id = tour.tr_lg.lg_id)[0].ail_status
        logged_atl_in_tour_qs = [atl_in_tour for atl_in_tour in list_atl_in_tour if atl_in_tour.ait_atl.atl_id == cleagues_authObj.logged_cleagues_athlete.atl_id]
        if logged_atl_in_tour_qs:
            logged_atl_in_tour = logged_atl_in_tour_qs[0]
        else:
            logged_atl_in_tour = ''
        context = { **general_context(request),
                    'view' : "Rank",
                    'tour' : tour,
                    **tour.get_summary(),
                    'list_atl_in_tour' : list_atl_in_tour,
                    'list_best_trial_tour_feed' : list_best_trial_tour_feed,
                    'atl_in_league_status' : atl_in_league_status,
                    'logged_atl_in_tour' : logged_atl_in_tour,
                    }
        return render(request, "CLeaguesApp/tour_details_rank.html", context=context)

class tour_details_athletesViewClass(View):

    @logged_user_required
    @exist_tour
    @permit_to_see_tour
    def get(self, request, *args, **kwargs):
        tour = kwargs['tour']
        list_atl_in_tour = list(AtlInTour.objects.all().filter(ait_tr__tr_id = tour.tr_id))
        list_atl_in_tour.sort(key=lambda x: x.ait_rank, reverse=False)
        context = { **general_context(request),
                    'view' : "Athletes",
                    'tour' : tour,
                    **tour.get_summary(),
                    'list_atl_in_tour' : list_atl_in_tour,
                    }
        return render(request, "CLeaguesApp/tour_details_athletes.html", context=context)

    # @logged_user_required
    # def post(self, request, *args, **kwargs):
    #     context = { **general_context(request), }
    #     return render(request, "CLeaguesApp/tour_details_athletes.html", context=context)

class edit_tourViewClass(View):

    @logged_user_required
    @exist_tour
    @permit_to_update_tour
    def get(self, request, *args, **kwargs):
        tour = kwargs['tour']
        tour_form = tourFormClass(None, instance=tour, initial = {'tr_ss': tour.tr_ss,
                                                                    })
        # tour_form.fields['tr_pic'].widget = forms.HiddenInput()
        tour_form.fields['tr_pic'].label = "Change Tour Image"
        context = { **general_context(request),
                    'tour': tour,
                    'tour_form': tour_form,
                    'tr_name' : tour.tr_name,
                    }
        return render(request, "CLeaguesApp/edit_tour.html", context=context)

    @logged_user_required
    @exist_tour
    @permit_to_update_tour
    def post(self, request, *args, **kwargs):
        tour = kwargs['tour']

        tr_name_original = tour.tr_name
        tour_form = tourFormClass(request.POST, instance=tour)
        tour_form.fields['tr_pic'].label = "Change Tour Image"

        if tour:
            if tour_form.is_valid(tour.tr_lg):
                tour = tour_form.save(commit=False)

                # Check if they provided a profile picture
                if request.FILES:
                    tour.tr_pic = request.FILES['tr_pic']

                if tour.tr_pic:
                    # print("I got a picture")
                    tour.tr_pic = resize_image(tour.tr_pic,162)
                # else:
                #     print("I did not got a picture")

                tour.save()

                base_url = "/CLeaguesApp/tour_details_rank"
                query_string =  urlencode({'tour': tour.tr_id})
                url = '{}?{}'.format(base_url, query_string)
                # print(url)
                return HttpResponseRedirect(url)
        # tour_form.fields['tr_pic'].widget = forms.HiddenInput()
        context = { **general_context(request),
                    'tour_form' : tour_form,
                    'tour' : tour,
                    'tr_name' : tr_name_original,
                    }
        return render(request, "CLeaguesApp/edit_tour.html", context=context)

class edit_leagueViewClass(View):

    @logged_user_required
    @exist_league
    @permit_to_update_league
    def get(self, request, *args, **kwargs):
        league = kwargs['league']
        league_form = leagueFormClass(None, instance=league)
        league_form.fields['lg_pic'].label = "Change League Image"
        context = { **general_context(request),
                    'league': league,
                    'league_form': league_form,
                    'lg_name' : league.lg_name,
                    }
        return render(request, "CLeaguesApp/edit_league.html", context=context)

    @logged_user_required
    @exist_league
    @permit_to_update_league
    def post(self, request, *args, **kwargs):
        league = kwargs['league']

        lg_name_original = league.lg_name
        league_form = leagueFormClass(request.POST, instance=league)
        league_form.fields['lg_pic'].label = "Change League Image"

        if league_form.is_valid():
            league = league_form.save(commit=False)

            # Check if they provided a profile picture
            if request.FILES:
                league.lg_pic = request.FILES['lg_pic']

            if league.lg_pic:
                # print("I got a picture")
                league.lg_pic = resize_image(league.lg_pic,162)
            # else:
            #     print("I did not got a picture")

            league.save()

            base_url = "/CLeaguesApp/league_details"
            query_string =  urlencode({'league': league.lg_id})
            url = '{}?{}'.format(base_url, query_string)
            # print(url)
            return HttpResponseRedirect(url)
        context = { **general_context(request),
                    'league_form' : league_form,
                    'league' : league,
                    'lg_name' : lg_name_original,
                    }
        return render(request, "CLeaguesApp/edit_league.html", context=context)

class inact_athlete_leagueViewClass(View):

    @logged_user_required
    @exist_league
    @permit_to_update_league
    @exist_athlete
    def get(self, request, *args, **kwargs):
        league = kwargs['league']
        athlete = kwargs['athlete']
        context = { **general_context(request),
                        'athlete' : athlete,
                        'league' : league, }
        return render(request, "CLeaguesApp/inact_athlete_league.html", context=context)

    @logged_user_required
    @exist_league
    @permit_to_update_league
    @exist_athlete
    def post(self, request, *args, **kwargs):
        league = kwargs['league']
        athlete = kwargs['athlete']
        if request.POST.get("btn_inact_athlete_league"):

            league.inactivate_athlete(athlete)

            base_url = "/CLeaguesApp/league_details"
            query_string =  urlencode({'league': league.lg_id})
            url = '{}?{}'.format(base_url, query_string)
            return HttpResponseRedirect(url)

        context = { **general_context(request),
                        'athlete' : athlete,
                        'league' : league, }
        return render(request, "CLeaguesApp/inact_athlete_league.html", context=context)

class inact_self_leagueViewClass(View):

    @logged_user_required
    @exist_league
    @exist_athlete
    @permit_to_update_athlete
    def get(self, request, *args, **kwargs):
        league = kwargs['league']
        athlete = kwargs['athlete']
        context = { **general_context(request),
                        'athlete' : athlete,
                        'league' : league, }
        return render(request, "CLeaguesApp/inact_self_league.html", context=context)

    @logged_user_required
    @exist_league
    @exist_athlete
    @permit_to_update_athlete
    def post(self, request, *args, **kwargs):
        league = kwargs['league']
        athlete = kwargs['athlete']
        cleagues_authObj = get_cleagues_authObj(request)
        if request.POST.get("btn_inact_self_league"):

            league.inactivate_athlete(athlete)
            cleagues_authObj.get_updated_atl_stat()

            return HttpResponseRedirect("/CLeaguesApp/leagues_feed")

        context = { **general_context(request),
                        'athlete' : athlete,
                        'league' : league, }
        return render(request, "CLeaguesApp/inact_self_league.html", context=context)

class react_athlete_leagueViewClass(View):

    @logged_user_required
    @exist_league
    @permit_to_update_league
    @exist_athlete
    def get(self, request, *args, **kwargs):
        league = kwargs['league']
        athlete = kwargs['athlete']
        context = { **general_context(request),
                        'athlete' : athlete,
                        'league' : league, }
        return render(request, "CLeaguesApp/react_athlete_league.html", context=context)

    @logged_user_required
    @exist_league
    @permit_to_update_league
    @exist_athlete
    def post(self, request, *args, **kwargs):
        league = kwargs['league']
        athlete = kwargs['athlete']
        if request.POST.get("btn_react_athlete_league"):

            league.reactivate_athlete(athlete)

            base_url = "/CLeaguesApp/league_details"
            query_string =  urlencode({'league': league.lg_id})
            url = '{}?{}'.format(base_url, query_string)
            return HttpResponseRedirect(url)

        context = { **general_context(request),
                        'athlete' : athlete,
                        'league' : league, }
        return render(request, "CLeaguesApp/react_athlete_league.html", context=context)

class triumphs_feedViewClass(View):

    @logged_user_required
    def get(self, request, *args, **kwargs):

        cleagues_authObj = get_cleagues_authObj(request)

        list_triumphs_feed, list_triumphs_feed_rank = cleagues_authObj.logged_cleagues_athlete.get_triumphs_feed()

        if cleagues_authObj.logged_cleagues_athlete.are_pending_invites():
            notification = "There are pending League inviations waiting for your decision"
        else:
            notification = ''

        context = { **general_context(request),
                    'list_triumphs_feed' : list_triumphs_feed,
                    'list_triumphs_feed_rank' : list_triumphs_feed_rank,
                    'notification' : notification, }

        return render(request, "CLeaguesApp/triumphs_feed.html", context=context)

class edit_athleteViewClass(View):

    @logged_user_required
    @exist_athlete
    @permit_to_update_athlete
    def get(self, request, *args, **kwargs):
        athlete = kwargs['athlete']
        athlete_form = athleteFormClass(None, instance=athlete)
        athlete_form.fields['atl_pic'].label = "Change your Picture"
        context = { **general_context(request),
                    'athlete': athlete,
                    'athlete_form': athlete_form,
                    }
        return render(request, "CLeaguesApp/edit_athlete.html", context=context)

    @logged_user_required
    @exist_athlete
    @permit_to_update_athlete
    def post(self, request, *args, **kwargs):
        athlete = kwargs['athlete']

        athlete_form = athleteFormClass(request.POST, instance=athlete)
        athlete_form.fields['atl_pic'].label = "Change Your Picture"

        if athlete_form.is_valid():
            athlete = athlete_form.save(commit=False)

            # Check if they provided a profile picture
            if request.FILES:
                atl_pic = request.FILES['atl_pic']
                if atl_pic:
                    # print("I got a picture")
                    athlete.atl_pic = resize_image(atl_pic,124)
                    athlete.atl_pic_mini = resize_image(atl_pic,60)

            athlete.save()

            set_cleagues_authObj_athlete(request, athlete)

            return HttpResponseRedirect("/CLeaguesApp/tours_feed")
        context = { **general_context(request),
                    'athlete_form' : athlete_form,
                    'athlete' : athlete,
                    }
        return render(request, "CLeaguesApp/edit_athlete.html", context=context)

class error403ViewClass(View):
    def get(self, request, *args, **kwargs):
        context = { **general_context(request), }
        return render(request, "CLeaguesApp/Error403.html", context=context)

### For Strava testing

class test_ViewClass(View):
    def get(self, request, *args, **kwargs):

        # Send Notifications
        run_batch_notifications()

        # Update Rankings
        # list_tours = Tour.objects.all()
        # for tour in list_tours:
        #     tour.update_ranking()

        context = { **general_context(request), }
        return render(request, "CLeaguesApp/test_strava.html", context=context)

# Empty views for a while

class blankViewClass(View):
    def get(self, request, *args, **kwargs):
        context = { **general_context(request), }
        return render(request, "CLeaguesApp/blank.html", context=context)
