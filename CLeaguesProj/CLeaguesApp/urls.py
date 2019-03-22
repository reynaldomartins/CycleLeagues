from django.conf.urls import url
from django.urls import path

from CLeaguesApp import views

app_name = 'CLeaguesApp'

urlpatterns = [
    url(r'^main/$',views.indexViewClass.as_view(), name='indexURLName'),
    url(r'^$',views.indexViewClass.as_view(), name='indexURLName'),
    url(r'^blank/$',views.blankViewClass.as_view(), name='blankURLName'),
    url(r'^Error403/$',views.error403ViewClass.as_view(), name='error403URLName'),
    url(r'^logout/$',views.indexViewClass.as_view(), name='logoutURLName'),
    url(r'^authorization/$',views.indexViewClass.as_view(), name='indexURLName'),
    url(r'^register_page/$',views.register_pageViewClass.as_view(), name='register_pageURLName'),
    url(r'^leagues_feed/$',views.leagues_feedViewClass.as_view(), name='leagues_feedURLName'),
    url(r'^leagues_feed_invite/$',views.leagues_feedViewClass.as_view(), name='leagues_feed_inviteURLName'),
    url(r'^league_details/$',views.league_detailsViewClass.as_view(), name='league_detailsURLName'),
    url(r'^tours_feed/$',views.tours_feedViewClass.as_view(), name='tours_feedURLName'),
    url(r'^create_tour/$',views.create_tourViewClass.as_view(), name='create_tourURLName'),
    url(r'^tour_details_segments/$',views.tour_details_segmentsViewClass.as_view(), name='tour_details_segmentsURLName'),
    url(r'^tour_details_rank/$',views.tour_details_rankViewClass.as_view(), name='tour_details_rankURLName'),
    url(r'^tour_details_athletes/$',views.tour_details_athletesViewClass.as_view(), name='tour_details_athletesURLName'),
    url(r'^edit_tour/$',views.edit_tourViewClass.as_view(), name='edit_tourURLName'),
    url(r'^delete_tour/$',views.delete_tourViewClass.as_view(), name='delete_tourURLName'),
    url(r'^edit_league/$',views.edit_leagueViewClass.as_view(), name='edit_leagueURLName'),
    url(r'^create_league/$',views.create_leagueViewClass.as_view(), name='create_leagueURLName'),
    url(r'^invite_athletes/$',views.invite_athletesViewClass.as_view(), name='invite_athletesURLName'),
    url(r'^edit_athlete/$',views.edit_athleteViewClass.as_view(), name='edit_athleteURLName'),
    url(r'^test_strava/$',views.test_ViewClass.as_view(), name='test_stravaURLName'),
    url(r'^join_league/$',views.join_leagueViewClass.as_view(), name='join_leagueURLName'),
    url(r'^confirm_join_league/$',views.confirm_join_leagueViewClass.as_view(), name='confirm_join_leagueURLName'),
    url(r'^inact_league/$',views.inact_leagueViewClass.as_view(), name='inact_leagueURLName'),
    url(r'^react_league/$',views.react_leagueViewClass.as_view(), name='react_leagueURLName'),
    url(r'^inact_athlete_league/$',views.inact_athlete_leagueViewClass.as_view(), name='inact_athlete_leagueURLName'),
    url(r'^inact_self_league/$',views.inact_self_leagueViewClass.as_view(), name='inact_self_leagueURLName'),
    url(r'^react_athlete_league/$',views.react_athlete_leagueViewClass.as_view(), name='react_athlete_leagueURLName'),
    url(r'^triumphs_feed/$',views.triumphs_feedViewClass.as_view(), name='triumphs_feedURLName'),
    url(r'^oops/$',views.oopsViewClass.as_view(), name='oopsURLName'),
]
