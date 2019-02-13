import MySQLdb
import sys
from .models import *
from .strava import *

class strive_authClass():
    logged_strive_status = False
    logged_strive_athlete = ''
    stat_qty_leagues = 0
    stat_qty_tours = 0
    stat_qty_palmares = 0

    def strive_login(self, logged_strava_atl_id):
        self.logged_strive_status = False
        atl_loggedObj_ret=Athlete.objects.all().filter(atl_id_strava=logged_strava_atl_id)
        if not atl_loggedObj_ret:
            return
        self.logged_strive_athlete = atl_loggedObj_ret[0]
        self.logged_strive_status = True

    def logout(self):
        self.logged_strive_status = False
        self.logged_strive_athlete = ''
        self.stat_qty_leagues = 0
        self.stat_qty_tours = 0
        self.stat_qty_palmares = 0

    def get_updated_atl_stat(self):
        count_league = 0
        count_tour = 0
        list_leagues_athlete = self.logged_strive_athlete.get_leagues()
        for league in list_leagues_athlete:
            if league.lg_status == "A":
                list_atl_in_leagues = AtlInLeague.objects.all().filter(ail_atl__atl_id = self.logged_strive_athlete.atl_id,
                                                                    ail_lg__lg_id = league.lg_id)
                for atl_in_league in list_atl_in_leagues:
                    if atl_in_league.ail_status == "A":
                        count_league = count_league + 1
        self.stat_qty_leagues = count_league
        self.stat_qty_tours = len(self.logged_strive_athlete.get_visible_tours())
        self.stat_qty_palmares = 0

    def auth_context(self):
        context = {
            'logged_strive_status' : self.logged_strive_status,
            'logged_strive_athlete' : self.logged_strive_athlete,
            'stat_qty_leagues' : self.stat_qty_leagues,
            'stat_qty_tours' : self.stat_qty_tours,
            'stat_qty_palmares' : self.stat_qty_palmares,
        }
        return context

# GLOBAL VARIABLES
strive_authObj = strive_authClass()

def is_you(atl_id):
    if strive_authObj.logged_strive_athlete.atl_id == atl_id:
        return "you!"
    else:
        return ''
