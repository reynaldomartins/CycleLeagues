import MySQLdb
import sys
from .models import *
from .strava import *

class cleagues_authClass():
    logged_cleagues_status = False
    logged_cleagues_athlete = ''
    strava_authObj = strava_authClass()
    stat_qty_leagues = 0
    stat_qty_tours = 0
    stat_qty_palmares = 0

    def login(self, atl_strava_code, request):
        global list_logged_cleagues

        # Avoid login into strava again if the object was already logged
        if not self.strava_authObj.logged_strava_athlete :
            self.strava_authObj = strava_authClass()
            self.strava_authObj.login(atl_strava_code)

        session_cleagues_id = request.session['session_cleagues_id']
        if session_cleagues_id:
            if session_cleagues_id.find("strava") != -1:
                del(list_logged_cleagues[session_cleagues_id])

        atl_loggedObj_ret=Athlete.objects.all().filter(atl_id_strava=self.strava_authObj.logged_strava_atl_id)
        if not atl_loggedObj_ret:
            self.logged_cleagues_status = False
            self.logged_cleagues_athlete = ''
            atl_id_temp = 'strava' + str(atl_strava_code)
            list_logged_cleagues[atl_id_temp] = self
            request.session['session_cleagues_id']= atl_id_temp
            return

        self.logged_cleagues_status = True
        self.logged_cleagues_athlete = atl_loggedObj_ret[0]
        atl_id = self.logged_cleagues_athlete.atl_id
        list_logged_cleagues[str(atl_id)] = self
        request.session['session_cleagues_id']=atl_id

    def logout(self,request):
        global list_logged_cleagues

        if self.logged_cleagues_athlete:
            del(list_logged_cleagues[str(self.logged_cleagues_athlete.atl_id)])
        request.session['session_cleagues_id']=None

        self.logged_cleagues_status = False
        self.logged_cleagues_athlete = ''
        if self.strava_authObj:
            self.strava_authObj.logout()
        self.stat_qty_leagues = 0
        self.stat_qty_tours = 0
        self.stat_qty_palmares = 0

    def get_updated_atl_stat(self):
        count_league = 0
        count_tour = 0
        list_leagues_athlete = self.logged_cleagues_athlete.get_leagues()
        for league in list_leagues_athlete:
            if league.lg_status == "A":
                list_atl_in_leagues = AtlInLeague.objects.all().filter(ail_atl__atl_id = self.logged_cleagues_athlete.atl_id,
                                                                    ail_lg__lg_id = league.lg_id)
                for atl_in_league in list_atl_in_leagues:
                    if atl_in_league.ail_status == "A":
                        count_league = count_league + 1
        self.stat_qty_leagues = count_league
        self.stat_qty_tours = len(self.logged_cleagues_athlete.get_visible_tours())
        self.stat_qty_palmares = 0

    def auth_context(self):
        context = {
            'logged_cleagues_status' : self.logged_cleagues_status,
            'logged_cleagues_athlete' : self.logged_cleagues_athlete,
            'strava_authObj' : self.strava_authObj,
            'stat_qty_leagues' : self.stat_qty_leagues,
            'stat_qty_tours' : self.stat_qty_tours,
            'stat_qty_palmares' : self.stat_qty_palmares,
        }
        return context

def get_cleagues_authObj(request):
    session_cleagues_id = request.session.get('session_cleagues_id', None)
    if session_cleagues_id:
        session_cleagues_id_str = str(session_cleagues_id)
        if session_cleagues_id_str in list_logged_cleagues:
            return list_logged_cleagues[session_cleagues_id_str]
    return cleagues_authClass()

# GLOBAL VARIABLE
# The list of all logged users
list_logged_cleagues = {}
