from django.db import models
from django.core.files import File
from django.db.models import Max
from .strava import *
from datetime import datetime
import random
from random import randint
import MySQLdb
import sys
import re
from django.core import files
import requests
import tempfile
import os

class Athlete(models.Model):
    atl_id = models.IntegerField(db_column='ATL_id', primary_key=True)
    atl_name_strava = models.CharField(db_column='ATL_name_strava', max_length=80, blank=True, null=True)
    atl_id_strava = models.IntegerField(db_column='ATL_id_strava', unique=True, blank=True, null=True)
    atl_code_strava = models.CharField(db_column='ATL_code_strava', max_length=80, blank=True, null=True)
    atl_email_strava = models.CharField(db_column='ATL_email_strava', max_length=80, blank=True, null=True)
    atl_city_strava = models.CharField(db_column='ATL_city_strava', max_length=80, blank=True, null=True)
    atl_country_strava = models.CharField(db_column='ATL_country_strava', max_length=80, blank=True, null=True)
    atl_sex_strava = models.CharField(db_column='ATL_sex_strava', max_length=1, blank=True, null=True)
    atl_created_at_strava = models.DateField(db_column='ATL_created_at_strava', blank=True, null=True)
    atl_status = models.CharField(db_column='ATL_status', max_length=1)
    # atl_creation_timestamp = models.DateTimeField(db_column='ATL_creation_timestamp')
    # atl_activation_timestamp = models.DateTimeField(db_column='ATL_activation_timestamp')
    # atl_inactivation_timestamp = models.DateTimeField(db_column='ATL_inactivation_timestamp')
    atl_pic = models.ImageField(db_column='ATL_pic', blank=True,upload_to="athletes")
    atl_pic_mini = models.ImageField(db_column='ATL_pic_mini', blank=True,upload_to="athletes_mini")

    class Meta:
        managed = False
        db_table = 'athlete'

    def __str__(self):
        return("Strive Id:" + str(self.atl_id)+";"+
               "Strava Name:" + str(self.atl_name_strava)+";"+
               "Strava Id:" + str(self.atl_id_strava)+";"+
               "Status:" + str(self.atl_status))

    def set_at_creation(self):
        last = Athlete.objects.all().aggregate(Max('atl_id'))['atl_id__max']
        if last:
            self.atl_id = last+1
        else:
            self.atl_id = 1
        # print(self.atl_id)
        self.atl_status = "A"
        # self.atl_creation_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def update_from_strava(self, strava_authObj):
        if strava_authObj:
            self.atl_id_strava = strava_authObj.logged_strava_atl_id
            self.atl_code_strava = strava_authObj.atl_strava_code
            self.atl_name_strava = re.sub('\W+',' ', strava_authObj.logged_strava_athlete.firstname ) + ' ' + re.sub('\W+',' ', strava_authObj.logged_strava_athlete.lastname )
            self.atl_email_strava = strava_authObj.logged_strava_athlete.email
            self.atl_city_strava = strava_authObj.logged_strava_athlete.city
            self.atl_country_strava = strava_authObj.logged_strava_athlete.country
            self.atl_sex_strava = strava_authObj.logged_strava_athlete.sex
            self.atl_created_at_strava = strava_authObj.logged_strava_athlete.created_at

    def get_visible_tours(self):
        list_visible_tours = []
        list_leagues = self.get_leagues()

        for league in list_leagues:

            atl_in_league_qs = AtlInLeague.objects.all().filter(ail_atl__atl_id = self.atl_id,
                                                                ail_lg__lg_id = league.lg_id)
            if atl_in_league_qs:
                atl_in_league = atl_in_league_qs[0]

            list_tours = league.get_tours()
            for tour in list_tours:
                # print(tour.tr_name)
                tr_status = tour.tour_status()
                if tr_status != "X":
                    atl_in_tour_qs = AtlInTour.objects.all().filter(ait_atl__atl_id = self.atl_id,
                                                                    ait_tr__tr_id = tour.tr_id)
                    if atl_in_tour_qs:
                        atl_in_tour = atl_in_tour_qs[0]

                        if league.lg_status == "A" and atl_in_league.ail_status == "A" and atl_in_tour.ait_status == "A":
                            # print(tour.tr_name)
                            list_visible_tours.append(tour)
                        elif atl_in_tour.ait_status == "A" and tr_status in ["F","Z"]:
                            # print(tour.tr_name)
                            list_visible_tours.append(tour)

        # print("I am leaving")
        # for tour in list_visible_tours:
        #     print("Inside Tours Visible {}".format(tour.tr_name))
        return list_visible_tours

    def can_see_tour(self, tour):
        this_atl_in_league_qs =  AtlInLeague.objects.all().filter(ail_lg__lg_id = tour.tr_lg.lg_id,
                                                                    ail_atl__atl_id = self.atl_id)
        if this_atl_in_league_qs:
            tr_status = tour.tour_status()
            this_atl_in_league = this_atl_in_league_qs[0]
            if this_atl_in_league.ail_status == "A":
                return True
            elif tr_status in ["F","Z"]:
                return True
        return False

    def get_tours_feed(self):
        list_tours_feed = []
        list_tours = self.get_visible_tours()
        # print("Len Tours Feed {}".format(len(list_tours)))
        for tour in list_tours:
            this_atl_in_tour_qs = AtlInTour.objects.all().filter(ait_atl__atl_id = self.atl_id,
                                                            ait_tr__tr_id = tour.tr_id)
            # print("Inside Tours feed {}".format(tour.tr_name))
            if this_atl_in_tour_qs:
                this_atl_in_tour = this_atl_in_tour_qs[0]
                tour_feed = tours_feedClass()
                tour_feed.list_atl_in_tour = list(AtlInTour.objects.all().filter(ait_tr__tr_id = tour.tr_id))
                tour_feed.list_atl_in_tour.sort(key=lambda x: x.ait_rank, reverse=False)
                tour_feed.atl_in_league = AtlInLeague.objects.all().filter(ail_lg__lg_id = tour.tr_lg.lg_id,
                                                                            ail_atl__atl_id = self.atl_id)[0]
                # atl_in_tour = [atl_in_tour for atl_in_tour in tour_feed.list_atl_in_tour if atl_in_tour.ait_atl.atl_id == self.atl_id]
                # if atl_in_tour:
                #     tour_feed.atl_in_tour_rank = atl_in_tour[0].ait_rank
                #     tour_feed.atl_in_tour_points = atl_in_tour[0].ait_points

                tour_feed.atl_in_tour_rank = this_atl_in_tour.ait_rank
                tour_feed.atl_in_tour_points = this_atl_in_tour.ait_points

                tour_feed.tour = tour
                tour_feed.league = tour.tr_lg
                tour_feed.summary = tour.get_summary()
                list_tours_feed.append(tour_feed)
                # print("Tour: {}".format(tour.tr_name))
        return list_tours_feed

    def download_pic_from_strava(self, strava_authObj, size):
        if size == "L":
            url_pic = strava_authObj.logged_strava_athlete.profile
        else:
            url_pic = strava_authObj.logged_strava_athlete.profile_medium
        request = requests.get(url_pic, stream=True)
        # Was the request OK?
        if request.status_code != requests.codes.ok:
            self.atl_pic = ""
            # print("it was not possible to get the photo")
            # print(url_pic)

        file_name = str(self.atl_id) + ".jpg"
        lf = tempfile.NamedTemporaryFile()

        # Read the streamed image in sections
        for block in request.iter_content(1024 * 8):
            # If no more file then stop
            if not block:
                break
            # Write image block to temporary file
            lf.write(block)

        # Save the temporary image to the model#
        # This saves the model so be sure that is it valid
        if size == "L":
            self.atl_pic.save(file_name, files.File(lf))
        else:
            self.atl_pic_mini.save(file_name, files.File(lf))

    def get_code_strava(atl_id):
        atl = Athlete.objects.get(pk=atl_id)
        return atl.atl_code_strava

    def get_leagues(self):
        list_leagues_athlete = []
        links_leagues_athlete = AtlInLeague.objects.all().filter(ail_atl__atl_id = self.atl_id)
        for link in links_leagues_athlete:
            list_leagues_athlete.append(link.ail_lg)
        return list_leagues_athlete

    def are_pending_invites(self):
        atl_in_league_qs = AtlInLeague.objects.all().filter(ail_atl__atl_id = self.atl_id,
                                                     ail_status = "C")
        if atl_in_league_qs:
            for atl_in_league in atl_in_league_qs:
                if atl_in_league.ail_lg.lg_status == "A":
                    return True
        return False

    def join_league(self,league,not_join_started_tour):
        atl_in_league = AtlInLeague()
        atl_in_league.set_at_creation(self ,league, "A")
        atl_in_league = atl_in_league.get_saving_instance()
        atl_in_league.save()
        list_tours_league = league.get_tours()
        for tour in list_tours_league:
            tr_status = tour.tour_status()
            if (tr_status == "A" and not not_join_started_tour) or tr_status == "T":
                atl_in_tour=AtlInTour()
                atl_in_tour.set_at_creation(self, tour)
                atl_in_tour.save()

    def dismiss_league_invitation(self, league):
        atl_in_league_qs = AtlInLeague.objects.all().filter(ail_atl__atl_id = self.atl_id,
                                                            ail_lg__lg_id = league.lg_id,
                                                            ail_status = "C")
        if atl_in_league_qs:
            atl_in_league = atl_in_league_qs[0]
            atl_in_league.delete()

def league_file_name(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.lg_id, ext)
    return os.path.join('leagues/repo', filename)

class league_feedClass():
    league : ''
    summary : ''
    logged_strive_atl_league_status = ''

class League(models.Model):
    lg_id = models.IntegerField(db_column='LG_id', primary_key=True)  # Field name made lowercase.
    lg_name = models.CharField(db_column='LG_name', unique=True, max_length=80)  # Field name made lowercase.
    lg_activation_code = models.IntegerField(db_column='LG_activation_code')  # Field name made lowercase.
    lg_atl_creator = models.ForeignKey(Athlete, models.DO_NOTHING, db_column='LG_atl_id_creator')  # Field name made lowercase.
    lg_status = models.CharField(db_column='LG_status', max_length=1)  # Field name made lowercase.
    # lg_creation_timestamp = models.DateTimeField(db_column='LG_creation_timestamp')  # Field name made lowercase.
    # lg_inactivation_timestamp = models.DateTimeField(db_column='LG_inactivation_timestamp')  # Field name made lowercase. =
    lg_pic = models.ImageField(db_column='LG_pic', upload_to=league_file_name, blank=True, default='leagues/default_league.jpg')

    class Meta:
        managed = False
        db_table = 'league'

    def set_at_creation(self, logged_strive_athlete):
        last = League.objects.all().aggregate(Max('lg_id'))['lg_id__max']
        if last:
            self.lg_id = last+1
        else:
            self.lg_id = 1
        self.lg_activation_code = random.randint(100000,999999)
        self.lg_atl_creator = logged_strive_athlete
        self.lg_status = "A"
        # self.lg_creation_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def reactivate(self):
        self.lg_status = "A"
        # self.lg_inactivation_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.save()

    def inactivate(self):
        self.lg_status = "I"
        # self.lg_inactivation_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.save()
        list_tours = self.get_tours()
        # For all Tours of this League Running and To Be Started, cancell the Tour definitly
        for tour in list_tours:
            tr_status = tour.tour_status()
            if tr_status == "A" or tr_status == "T":
                tour.tr_status = "X"
                tour.save()

    def get_athletes_in_league(self):
        list_athletes_in_league = []
        links_atl_league = AtlInLeague.objects.all().filter(ail_lg__lg_id = self.lg_id)
        for link in links_atl_league:
            # print("loop do get_athletes_in_league")
            atl_in_league = athlete_in_league_extClass()
            atl_in_league.atl = link.ail_atl
            # print(link.ail_atl.atl_name_strava)
            atl_in_league.atl_in_league_status = link.ail_status
            # print(link.ail_status)
            # print(atl_in_league.atl.atl_name_strava)
            # print(atl_in_league.atl_in_league_status)
            list_athletes_in_league.append(atl_in_league)
        return list_athletes_in_league

    def get_tours(self):
        list_tours_league=self.tour_set.all()
        return [tour for tour in list_tours_league if tour.tr_status != "X"]

    def get_segments(self):
        list_tours = self.get_tours();
        list_segments = []
        for tour in list_tours:
            list_segments = list_segments + tour.get_segments()
        list_segments = list(set(list_segments))
        return list_segments

    def get_summary(self):
        list_athletes_in_league = self.get_athletes_in_league()
        num_athletes = len([atl_in_league_ext for atl_in_league_ext in list_athletes_in_league if atl_in_league_ext.atl_in_league_status == "A"])

        unstarted_tours = 0
        active_tours = 0
        finished_tours = 0
        inactive_tours = 0
        list_tours = self.get_tours();
        num_tours = len(list_tours)

        for tour in list_tours:
            tr_status = tour.tour_status()
            if tr_status == "T":
                unstarted_tours = unstarted_tours + 1
            elif tr_status == "A":
                active_tours = active_tours + 1
            elif tr_status == "I":
                inactive_tours = inactive_tours + 1
            elif tr_status in ["F","Z"]:
                finished_tours = finished_tours + 1
        return {    'num_athletes' : num_athletes,
                    'unstarted_tours' : unstarted_tours,
                    'active_tours' : active_tours,
                    'finished_tours' : finished_tours,
                    'inactive_tours' : inactive_tours,
                    'num_tours' : num_tours,
                }

    def inactivate_athlete(self, athlete):
        atl_in_league_qs = AtlInLeague.objects.all().filter(ail_atl__atl_id = athlete.atl_id,
                                                            ail_lg__lg_id = self.lg_id)
        if atl_in_league_qs:
            atl_in_league = atl_in_league_qs[0]
            atl_in_league.ail_status = "I"
            atl_in_league.save()

            list_tours_league = self.get_tours()

            for tour in list_tours_league:
                tour.inactivate_athlete(athlete)

    def reactivate_athlete(self, athlete):
        atl_in_league_qs = AtlInLeague.objects.all().filter(ail_atl__atl_id = athlete.atl_id,
                                                            ail_lg__lg_id = self.lg_id)
        if atl_in_league_qs:
            atl_in_league = atl_in_league_qs[0]
            atl_in_league.ail_status = "A"
            atl_in_league.save()

            list_tours_league = self.get_tours()

            for tour in list_tours_league:
                tour.reactivate_athlete(athlete)

class athlete_in_league_extClass():
    atl = ''
    atl_in_league_status = ''

class AtlInLeague(models.Model):
    ail_atl = models.ForeignKey(Athlete, models.DO_NOTHING, db_column='AIL_atl_id')
    ail_lg = models.ForeignKey(League, models.DO_NOTHING, db_column='AIL_lg_id')

    ail_atl_nick_name = models.CharField(db_column='AIL_atl_nick_name', max_length=80, blank=True, null=True)  # Field name made lowercase.
    ail_status = models.CharField(db_column='AIL_status', max_length=1, blank=True, null=True)  # Field name made lowercase.
    # ail_creation_timestamp = models.DateTimeField(db_column='AIL_creation_timestamp')  # Field name made lowercase.
    # ail_activation_timestamp = models.DateTimeField(db_column='AIL_activation_timestamp')  # Field name made lowercase.
    # ail_inactivation_timestamp = models.DateTimeField(db_column='AIL_inactivation_timestamp')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'atl_in_league'
        unique_together = (('ail_atl', 'ail_lg'), ('ail_lg', 'ail_atl_nick_name'),)

    def set_at_creation(self,athlete,league, status):
        self.ail_atl = athlete;
        self.ail_lg = league;
        self.ail_atl_nick_name = athlete.atl_name_strava
        self.ail_status = status
        # self.ail_creation_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def get_saving_instance(self):
        atl_in_league_qs = AtlInLeague.objects.all().filter(ail_lg__lg_id=self.ail_lg.lg_id,
                                        ail_atl__atl_id=self.ail_atl.atl_id)
        if atl_in_league_qs:
            atl_in_league_qs[0].update_from(self)
            return atl_in_league_qs[0]
        else:
            return self

    def update_from(self,atl_in_league):
        self.ail_status = atl_in_league.ail_status

class ScoringSystem(models.Model):
    ss_id = models.IntegerField(db_column='SS_id', primary_key=True)  # Field name made lowercase.
    ss_name = models.CharField(db_column='SS_name', max_length=80)  # Field name made lowercase.
    ss_pos1 = models.IntegerField(db_column='SS_pos1', blank=True, null=True)  # Field name made lowercase.
    ss_pos2 = models.IntegerField(db_column='SS_pos2', blank=True, null=True)  # Field name made lowercase.
    ss_pos3 = models.IntegerField(db_column='SS_pos3', blank=True, null=True)  # Field name made lowercase.
    ss_pos4 = models.IntegerField(db_column='SS_pos4', blank=True, null=True)  # Field name made lowercase.
    ss_pos5 = models.IntegerField(db_column='SS_pos5', blank=True, null=True)  # Field name made lowercase.
    ss_pos6 = models.IntegerField(db_column='SS_pos6', blank=True, null=True)  # Field name made lowercase.
    ss_pos7 = models.IntegerField(db_column='SS_pos7', blank=True, null=True)  # Field name made lowercase.
    ss_pos8 = models.IntegerField(db_column='SS_pos8', blank=True, null=True)  # Field name made lowercase.
    ss_pos9 = models.IntegerField(db_column='SS_pos9', blank=True, null=True)  # Field name made lowercase.
    ss_pos10 = models.IntegerField(db_column='SS_pos10', blank=True, null=True)  # Field name made lowercase.
    ss_pos11 = models.IntegerField(db_column='SS_pos11', blank=True, null=True)  # Field name made lowercase.
    ss_pos12 = models.IntegerField(db_column='SS_pos12', blank=True, null=True)  # Field name made lowercase.
    ss_pos13 = models.IntegerField(db_column='SS_pos13', blank=True, null=True)  # Field name made lowercase.
    ss_pos14 = models.IntegerField(db_column='SS_pos14', blank=True, null=True)  # Field name made lowercase.
    ss_pos15 = models.IntegerField(db_column='SS_pos15', blank=True, null=True)  # Field name made lowercase.
    ss_pos16 = models.IntegerField(db_column='SS_pos16', blank=True, null=True)  # Field name made lowercase.
    ss_pos17 = models.IntegerField(db_column='SS_pos17', blank=True, null=True)  # Field name made lowercase.
    ss_pos18 = models.IntegerField(db_column='SS_pos18', blank=True, null=True)  # Field name made lowercase.
    ss_pos19 = models.IntegerField(db_column='SS_pos19', blank=True, null=True)  # Field name made lowercase.
    ss_pos20 = models.IntegerField(db_column='SS_pos20', blank=True, null=True)  # Field name made lowercase.
    ss_pos21 = models.IntegerField(db_column='SS_pos21', blank=True, null=True)  # Field name made lowercase.
    ss_pos22 = models.IntegerField(db_column='SS_pos22', blank=True, null=True)  # Field name made lowercase.
    ss_pos23 = models.IntegerField(db_column='SS_pos23', blank=True, null=True)  # Field name made lowercase.
    ss_pos24 = models.IntegerField(db_column='SS_pos24', blank=True, null=True)  # Field name made lowercase.
    ss_pos25 = models.IntegerField(db_column='SS_pos25', blank=True, null=True)  # Field name made lowercase.
    ss_pos26 = models.IntegerField(db_column='SS_pos26', blank=True, null=True)  # Field name made lowercase.
    ss_pos27 = models.IntegerField(db_column='SS_pos27', blank=True, null=True)  # Field name made lowercase.
    ss_pos28 = models.IntegerField(db_column='SS_pos28', blank=True, null=True)  # Field name made lowercase.
    ss_pos29 = models.IntegerField(db_column='SS_pos29', blank=True, null=True)  # Field name made lowercase.
    ss_pos30 = models.IntegerField(db_column='SS_pos30', blank=True, null=True)  # Field name made lowercase.
    ss_status = models.CharField(db_column='SS_status', max_length=1)  # Field name made lowercase.
    # ss_creation_timestamp = models.DateTimeField(db_column='SS_creation_timestamp')  # Field name made lowercase.
    # ss_inactivation_timestamp = models.DateTimeField(db_column='SS_inactivation_timestamp')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'scoring_system'

    def get_as_list(self):
        score_list = []
        score_list.append(self.ss_pos1)
        score_list.append(self.ss_pos2)
        score_list.append(self.ss_pos3)
        score_list.append(self.ss_pos4)
        score_list.append(self.ss_pos5)
        score_list.append(self.ss_pos6)
        score_list.append(self.ss_pos7)
        score_list.append(self.ss_pos8)
        score_list.append(self.ss_pos9)
        score_list.append(self.ss_pos10)
        score_list.append(self.ss_pos11)
        score_list.append(self.ss_pos12)
        score_list.append(self.ss_pos13)
        score_list.append(self.ss_pos14)
        score_list.append(self.ss_pos15)
        score_list.append(self.ss_pos16)
        score_list.append(self.ss_pos17)
        score_list.append(self.ss_pos18)
        score_list.append(self.ss_pos19)
        score_list.append(self.ss_pos20)
        score_list.append(self.ss_pos21)
        score_list.append(self.ss_pos22)
        score_list.append(self.ss_pos23)
        score_list.append(self.ss_pos24)
        score_list.append(self.ss_pos25)
        score_list.append(self.ss_pos26)
        score_list.append(self.ss_pos27)
        score_list.append(self.ss_pos28)
        score_list.append(self.ss_pos29)
        score_list.append(self.ss_pos30)
        return score_list

class best_trial_feedClass():
    atl_best_trial = ''
    sg_name_strava = ''
    atl_name_strava = ''

class Segment(models.Model):
    sg_id = models.IntegerField(db_column='SG_id', primary_key=True)  # Field name made lowercase.
    sg_name_strava = models.CharField(db_column='SG_name_strava', max_length=80, blank=True, null=True)  # Field name made lowercase.
    sg_id_strava = models.IntegerField(db_column='SG_id_strava', unique=True, blank=True, null=True)  # Field name made lowercase.
    sg_distance = models.FloatField(db_column='SG_distance', blank=True, null=True)  # Field name made lowercase.
    sg_avg_grade = models.FloatField(db_column='SG_avg_grade', blank=True, null=True)  # Field name made lowercase.
    sg_low_elev = models.IntegerField(db_column='SG_low_elev', blank=True, null=True)  # Field name made lowercase.
    sg_high_elev = models.IntegerField(db_column='SG_high_elev', blank=True, null=True)  # Field name made lowercase.
    sg_elev_dif = models.IntegerField(db_column='SG_elev_dif', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'segment'

    def set_at_creation(self):
        last = Segment.objects.all().aggregate(Max('sg_id'))['sg_id__max']
        if last:
            self.sg_id = last+1
        else:
            self.sg_id = 1

    def update_from_strava(self, strava_segment):
        if strava_segment:
            self.sg_name_strava = strava_segment.name
            self.sg_id_strava = strava_segment.id
            self.sg_distance = round(float(strava_segment.distance/1000),1)
            self.sg_avg_grade = float(strava_segment.average_grade)
            self.sg_low_elev = int(strava_segment.elevation_low)
            self.sg_high_elev = int(strava_segment.elevation_high)
            self.sg_elev_dif = self.sg_high_elev-self.sg_low_elev

    def get_best_trial_tour_feed(self, tour):
        list_best_trial_feed = []
        list_atl_best_trial = AtlBestTrial.objects.all().filter(abt_sg__sg_id = self.sg_id, abt_tr__tr_id = tour.tr_id)
        for atl_best_trial in list_atl_best_trial:
            best_trial_feed = best_trial_feedClass()
            best_trial_feed.atl_best_trial = atl_best_trial
            best_trial_feed.atl_name_strava = atl_best_trial.abt_atl.atl_name_strava
            best_trial_feed.sg_name_strava = atl_best_trial.abt_sg.sg_name_strava
            list_best_trial_feed.append(best_trial_feed)
        return list_best_trial_feed

    def convert_list_segments(list_strava_segments):
        ''' This function convert list of segments from Strava model to Strive model '''
        list_strive_segments = []
        for strava_seg in list_strava_segments:
            strive_seg = Segment()
            strive_seg.update_from_strava(strava_seg)
            list_strive_segments.append(strive_seg)
        return list_strive_segments

class tours_feedClass():
    tour_summary = ''
    tour = ''
    list_atl_in_tour = []
    atl_in_league = []
    atl_in_tour_rank = ''
    atl_in_tour_points = ''
    league = ''

class Tour(models.Model):
    tr_id = models.IntegerField(db_column='TR_id', primary_key=True)  # Field name made lowercase.
    tr_name = models.CharField(db_column='TR_name', max_length=80)  # Field name made lowercase.
    tr_lg = models.ForeignKey(League, models.DO_NOTHING, db_column='TR_lg_id')
    tr_start_date = models.DateField(db_column='TR_start_date', blank=True, null=True)  # Field name made lowercase.
    tr_finish_date = models.DateField(db_column='TR_finish_date')  # Field name made lowercase.
    tr_ss = models.ForeignKey(ScoringSystem, models.DO_NOTHING, db_column='TR_ss_id')  # Field name made lowercase.
    tr_atl_creator = models.ForeignKey(Athlete, models.DO_NOTHING, db_column='TR_atl_id_creator')  # Field name made lowercase.
    tr_activation_code = models.IntegerField(db_column='TR_activation_code')  # Field name made lowercase.
    tr_status = models.CharField(db_column='TR_status', max_length=1)  # Field name made lowercase.
    # tr_creation_timestamp = models.DateTimeField(db_column='TR_creation_timestamp')  # Field name made lowercase.
    # tr_inactivation_timestamp = models.DateTimeField(db_column='TR_inactivation_timestamp')  # Field name made lowercase.
    tr_pic = models.ImageField(db_column='TR_pic', blank=True,upload_to="tours/repo",default='tours/default_tour.jpg')

    class Meta:
        managed = False
        db_table = 'tour'
        unique_together = (('tr_lg', 'tr_name'),)

    def set_at_creation(self, league, logged_strive_athlete):
        last = Tour.objects.all().aggregate(Max('tr_id'))['tr_id__max']
        if last:
            self.tr_id = last+1
        else:
            self.tr_id = 1
        self.tr_lg = league
        self.tr_activation_code = random.randint(100000,999999)
        self.tr_atl_creator = logged_strive_athlete
        self.tr_status = "A"
        # self.tr_creation_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def delete(self):
        self.tr_status = "X"
        self.save()

    def delete_segment(self, sg_id):
        seg_in_tour_qs = SegInTour.objects.all().filter(sit_tr__tr_id = self.tr_id, sit_sg__sg_id = sg_id)
        if seg_in_tour_qs:
            seg_in_tour = seg_in_tour_qs[0]
            print("I am inside delete")
            seg_in_tour.delete()

    def is_running_bydate(self):
        today = datetime.now().date()
        if self.tr_start_date <= today and self.tr_finish_date >= today:
            return True
        return False

    def is_tobestarted_bydate(self):
        today = datetime.now().date()
        if self.tr_start_date > today:
            return True
        return False

    def is_finished_bydate(self):
        today = datetime.now().date()
        if self.tr_finish_date < today:
            return True
        return False

    def tour_status(self):
        today = datetime.now().date()
        if self.tr_status not in ["I","Z"]:
            if self.is_finished_bydate() and self.tr_status != "F":
                self.tr_status = "F"
                self.save()
            elif self.is_tobestarted_bydate() and self.tr_status != "T":
                self.tr_status = "T"
                self.save()
            elif self.is_running_bydate() and self.tr_status != "A":
                self.tr_status = "A"
                self.save()
        return self.tr_status

    def get_segments(self):
        list_seg_tour = []
        links_seg_tour = SegInTour.objects.all().filter(sit_tr__tr_id = self.tr_id)
        for link in links_seg_tour:
            # print("loop do segment in tour")
            list_seg_tour.append(link.sit_sg)
        # print(list_seg_tour)
        return list_seg_tour

    def get_athletes(self):
        # return self.get.athlete_set()
        list_atl_tour = []
        links_atl_tour = AtlInTour.objects.all().filter(ait_tr__tr_id = self.tr_id)
        for link in links_atl_tour:
            # print("loop do segment in tour")
            list_atl_tour.append(link.ait_atl)
        # print(list_seg_tour)
        return list_atl_tour

    def get_best_trial_feed(self):
        list_tour_best_trials = []
        list_segments = self.get_segments()
        for seg in list_segments:
            list_seg_best_trial_tour = seg.get_best_trial_tour_feed(self)
            for atl_best_trial in list_seg_best_trial_tour:
                list_tour_best_trials.append(atl_best_trial)
        return list_tour_best_trials

    def get_summary(self):
        num_athletes = len(self.get_athletes())
        num_segments = len(self.get_segments())
        days_to_go = (self.tr_finish_date - datetime.now().date()).days
        if days_to_go < 0:
            days_to_go = "-"
        leader_qs = AtlInTour.objects.all().filter(ait_tr__tr_id =  self.tr_id, ait_rank = 1)

        if leader_qs:
            if leader_qs[0].ait_points == 0:
                leader_name = "None"
                leader_pic = ''
                leader_id = ''
            else:
                leader_name = leader_qs[0].ait_atl.atl_name_strava
                leader_pic = leader_qs[0].ait_atl.atl_pic_mini
                leader_id = leader_qs[0].ait_atl.atl_id
        else:
            leader_name = "None"
            leader_pic = ''
            leader_id = ''

        return { 'num_athletes' : num_athletes,
                    'num_segments' : num_segments,
                    'days_to_go' : days_to_go,
                    'leader_name' : leader_name,
                    'leader_pic' : leader_pic,
                    'leader_id' : leader_id }

    def inactivate_athlete(self, athlete):
        tr_status = self.tour_status()
        if tr_status == "A" or tr_status == "T":
            atl_in_tour_qs = AtlInTour.objects.all().filter(ait_atl__atl_id = athlete.atl_id,
                                                            ait_tr__tr_id = self.tr_id)
            if atl_in_tour_qs:
                atl_in_tour = atl_in_tour_qs[0]
                atl_in_tour.ait_status = "I"
                atl_in_tour.ait_rank = NOT_RANKED
                atl_in_tour.ait_points = 0
                atl_in_tour.ait_ridden = 0
                atl_in_tour.save()

                atl_best_trial_qs = AtlBestTrial.objects.all().filter(abt_atl__atl_id = athlete.atl_id,
                                                                abt_tr__tr_id = self.tr_id)
                for atl_best_trial in atl_best_trial_qs:
                    atl_best_trial.abt_status = "I"
                    atl_best_trial.abt_date = datetime.strptime('Jan 1 1900','%b %d %Y')
                    atl_best_trial.abt_time = t = datetime.strptime("00:00:00","%H:%M:%S")
                    atl_best_trial.abt_rank = -1
                    atl_best_trial.abt_points = -1
                    atl_best_trial.save()

    def reactivate_athlete(self, athlete):
        if self.tr_status != "I":
            if not self.is_finished_bydate():
                atl_in_tour_qs = AtlInTour.objects.all().filter(ait_atl__atl_id = athlete.atl_id,
                                                                ait_tr__tr_id = self.tr_id)
                if atl_in_tour_qs:
                    atl_in_tour = atl_in_tour_qs[0]
                    atl_in_tour.ait_status = "A"
                    atl_in_tour.save()

                    atl_best_trial_qs = AtlBestTrial.objects.all().filter(abt_atl__atl_id = athlete.atl_id,
                                                                    abt_tr__tr_id = self.tr_id)
                    for atl_best_trial in atl_best_trial_qs:
                        atl_best_trial.abt_status = "A"
                        atl_best_trial.save()

    def update_ranking(self):
        tr_status = self.tour_status()
        if tr_status in ["Z","I","X"] or self.tr_lg.lg_status == 'I':
            return False

        list_segments = self.get_segments()

        # Get a list with all athletes in this tour
        list_atl = self.get_athletes()

        # Get the Best Trial for all athletes for each tour segment in the Tour
        list_best_trial = []
        list_best_trial_updated = []
        list_atl_actives = []
        strava_authObj = strava_authClass()
        for atl in list_atl:
            atl_in_tour_qs = AtlInTour.objects.all().filter(ait_atl__atl_id =atl.atl_id,
                                                            ait_tr__tr_id = self.tr_id)
            if atl_in_tour_qs:
                if atl_in_tour_qs[0].ait_status == "A":
                    strava_authObj.change_access_for_query(Athlete.get_code_strava(atl.atl_id))
                    for seg in list_segments:
                        effort_list = strava_authObj.get_efforts_segment(seg.sg_id_strava,self.tr_start_date,self.tr_finish_date,1)
                        # print(effort_list)
                        if effort_list:
                            atl_best_trial = AtlBestTrial()
                            atl_best_trial.set_at_creation(self,seg,atl,
                                                            effort_list[0].start_date,
                                                            effort_list[0].elapsed_time)
                            list_best_trial.append(atl_best_trial)
                    # strava_authObj.resume_access_after_query()
                    list_atl_actives.append(atl)

        # Obtain the scoring system used in this Tour
        scoring = ScoringSystem.objects.get(pk=self.tr_ss.ss_id)
        list_scoring = scoring.get_as_list()

        # Handle each segment in this tour and order the best time trials of each one
        # Then match each athlete effort in the segment if the scoring systems
        for seg in list_segments:
            list_best_trial_seg = [bt for bt in list_best_trial if bt.abt_sg.sg_id == seg.sg_id]
            list_best_trial_seg.sort(key=lambda x: x.abt_time, reverse=False)
            # print("Ordered rank of {} :".format(seg.sg_name_strava))
            i = 1
            for atl_best_trial in list_best_trial_seg:
                atl_best_trial.abt_rank = i
                atl_best_trial.abt_points = list_scoring[i-1]
                i=i+1
                # # print("{} / {} / {} / {} / {} / {}".format(atl_best_trial.abt_atl.atl_name_strava,
                #                     atl_best_trial.abt_sg.sg_name_strava, atl_best_trial.abt_date,
                #                     atl_best_trial.abt_time, atl_best_trial.abt_rank, atl_best_trial.abt_points))

                # print(atl_best_trial.abt_tr.tr_id, atl_best_trial.abt_atl.atl_id, atl_best_trial.abt_sg.sg_id)

                atl_best_trial = atl_best_trial.get_saving_instance()
                atl_best_trial.save()
                list_best_trial_updated.append(atl_best_trial)

        # Calculte the athlete summary in this tours
        list_atl_in_tour = []

        # Sum the points and the segments ridden for each athlete in the tour
        for atl in list_atl_actives:
            atl_in_tour = AtlInTour()
            atl_in_tour.set_at_creation(atl,self)
            list_atl_best_trial = [abt for abt in list_best_trial_updated
                                    if abt.abt_atl.atl_id == atl.atl_id]
            for atl_best_trial in list_atl_best_trial:
                atl_in_tour.ait_ridden = atl_in_tour.ait_ridden + 1
                atl_in_tour.ait_points = atl_in_tour.ait_points + atl_best_trial.abt_points
            list_atl_in_tour.append(atl_in_tour)

        # Now, sort atls in this tour using the points obtained as a key
        list_atl_in_tour.sort(key=lambda x: x.ait_points, reverse=True)

        # Set the position of each athlete in the Tour
        i = 1
        for atl_in_tour in list_atl_in_tour:
            atl_in_tour.ait_rank = i
            i=i+1
            atl_in_tour = atl_in_tour.get_saving_instance()
            atl_in_tour.save()

        # print("Ordered rank in the Tour {} :".format(self.tr_name))
        # for atl_in_tour in list_atl_in_tour:
        #         print("{} / {} / {} / {}".format(atl_in_tour.ait_atl.atl_name_strava,atl_in_tour.ait_rank,
        #                                     atl_in_tour.ait_points, atl_in_tour.ait_ridden))

        # If it was reached the last date of the Tour, set as finished-finished, status = "Z
        today = datetime.now().date()
        if today > self.tr_finish_date:
            self.tr_status = "Z"
            self.save()
        return True

NOT_RANKED = 1000

class AtlInTour(models.Model):
    ait_atl = models.ForeignKey(Athlete, models.DO_NOTHING, db_column='AIT_atl_id')
    ait_tr = models.ForeignKey(Tour, models.DO_NOTHING, db_column='AIT_tr_id')

    ait_ridden = models.IntegerField(db_column='AIT_ridden', blank=True, null=True)  # Field name made lowercase.
    ait_rank = models.IntegerField(db_column='AIT_rank', blank=True, null=True)  # Field name made lowercase.
    ait_points = models.IntegerField(db_column='AIT_points', blank=True, null=True)  # Field name made lowercase.
    ait_status = models.CharField(db_column='AIT_status', max_length=1, blank=True, null=True)  # Field name made lowercase.
    # ait_inactivation_timestamp = models.DateTimeField(db_column='AIT_inactivation_timestamp')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'atl_in_tour'
        unique_together = (('ait_atl', 'ait_tr'),)

    def set_at_creation(self, athlete, tour):
        self.ait_atl = athlete
        self.ait_tr = tour
        self.ait_rank = NOT_RANKED
        self.ait_ridden = 0
        self.ait_points = 0
        self.ait_status = 'A'

    def get_saving_instance(self):
        atl_in_tour_qs = AtlInTour.objects.all().filter(ait_tr__tr_id=self.ait_tr.tr_id,
                                        ait_atl__atl_id=self.ait_atl.atl_id)
        if atl_in_tour_qs:
            atl_in_tour_qs[0].update_from(self)
            return atl_in_tour_qs[0]
        else:
            return self

    def update_from(self,atl_in_tour):
        self.ait_ridden = atl_in_tour.ait_ridden
        self.ait_rank = atl_in_tour.ait_rank
        self.ait_points = atl_in_tour.ait_points

class SegInTour(models.Model):
    sit_sg = models.ForeignKey(Segment, models.DO_NOTHING, db_column='SIT_sg_id')
    sit_tr = models.ForeignKey(Tour, models.DO_NOTHING, db_column='SIT_tr_id')

    sit_status = models.CharField(db_column='SIT_status', max_length=1)
    # sit_creation_timestamp = models.DateTimeField(db_column='SIT_creation_timestamp')
    # sit_inactivation_timestamp = models.DateTimeField(db_column='SIT_inactivation_timestamp')

    def set_at_creation(self, segment, tour):
        self.sit_sg = segment;
        self.sit_tr = tour;
        self.sit_status = 'A'
        # self.sit_creation_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    class Meta:
        managed = False
        db_table = 'seg_in_tour'
        unique_together = (('sit_tr', 'sit_sg'),)


class AtlBestTrial(models.Model):
    abt_atl = models.ForeignKey(Athlete, models.DO_NOTHING, db_column='ABT_atl_id')
    abt_tr = models.ForeignKey(Tour, models.DO_NOTHING, db_column='ABT_tr_id')
    abt_sg = models.ForeignKey(Segment, models.DO_NOTHING, db_column='ABT_sg_id')

    abt_date = models.DateField(db_column='ABT_date')
    abt_time = models.TimeField(db_column='ABT_time')
    abt_rank = models.IntegerField(db_column='ABT_rank')
    abt_points = models.IntegerField(db_column='ABT_points')

    abt_status = models.CharField(db_column='ABT_status', max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'atl_best_trial'
        unique_together = (('abt_atl', 'abt_tr', 'abt_sg'),)

    def set_at_creation(self, tour, seg, atl, date, time_elapsed):
        self.abt_tr = tour
        self.abt_sg = seg
        self.abt_atl = atl
        # print("{} / {} / {} / {}".format(self.abt_atl.atl_name_strava, self.abt_sg.sg_name_strava,
        #                                  date, time_elapsed))
        self.abt_date = date.date()

        self.abt_time = (datetime.min + time_elapsed).time()

        # print("{} / {}".format(self.abt_date,self.abt_time))
        self.abt_rank = -1
        self.abt_points = -1
        self.abt_status = "A"

    def get_saving_instance(self):
        atl_best_trial_qs = AtlBestTrial.objects.all().filter(abt_tr__tr_id=self.abt_tr.tr_id,
                                        abt_atl__atl_id=self.abt_atl.atl_id,abt_sg__sg_id=self.abt_sg.sg_id)
        if atl_best_trial_qs:
            atl_best_trial_qs[0].update_from(self)
            return atl_best_trial_qs[0]
        else:
            return self

    def update_from(self,atl_best_trial):
        self.abt_date = atl_best_trial.abt_date
        self.abt_time = atl_best_trial.abt_time
        self.abt_rank = atl_best_trial.abt_rank
        self.abt_points = atl_best_trial.abt_points
