import stravalib
from stravalib.client import Client
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from stravalib import unithelper
from datetime import datetime, timedelta

class strava_authClass():
    MY_STRAVA_CLIENT_ID = 30858
    MY_STRAVA_CLIENT_SECRET = 'dea53ced70533ed1173b7c110b12ef29f48e0c9c'
    strava_url = ''
    atl_strava_code = ''
    logged_strava_atl_id = 0
    logged_strava_athlete = ''
    query_strava_atl_id = 0
    query_strava_athlete = ''
    client = ''

    def get_strava_url(self, request):
        self.MY_STRAVA_CLIENT_ID = 30858
        host_port = request.get_host()
        # print("This is host_port {}".format(host_port))
        url = self.client.authorization_url(client_id=self.MY_STRAVA_CLIENT_ID,
                                            redirect_uri='http://' + host_port + '/CLeaguesApp/authorization')
        # print("enviar essa URL")
        # print("This is url {}".format(url))
        return url

    def __init__(self):
        self.client = Client()

    def login(self, atl_strava_code):
        self.atl_strava_code = atl_strava_code
        user_access_token = ''
        user_access_token = self.client.exchange_code_for_token(client_id=self.MY_STRAVA_CLIENT_ID,
                    client_secret=self.MY_STRAVA_CLIENT_SECRET,
                    code=self.atl_strava_code)
        if user_access_token :
            self.logged_strava_status = True
            self.logged_strava_athlete = self.client.get_athlete()
            temp_str = str(self.logged_strava_athlete)[12:-1]
            final_id = temp_str.find(' ')
            self.logged_strava_atl_id = int(temp_str[0:final_id])
        else:
            self.logged_strava_status = False
            self.logged_strava_athlete = ''
            self.logged_strava_atl_id = 0

    def logout(self):
        self.atl_strava_code = ''
        self.logged_strava_atl_id  = 0
        self.logged_strava_athlete = ''

    def auth_context(self):
        context = { 'logged_strava_atl_id' : self.logged_strava_atl_id,
                    'logged_strava_athlete' : self.logged_strava_athlete }
        return context

    def change_access_for_query(self, atl_strava_code):
        # print("atl_strava_code {}".format(atl_strava_code))
        user_access_token = ''
        user_access_token = self.client.exchange_code_for_token(client_id=self.MY_STRAVA_CLIENT_ID,
                    client_secret=self.MY_STRAVA_CLIENT_SECRET,
                    code=atl_strava_code)
        # print("user_access_token {}".format(user_access_token))
        # if user_access_token:
        #     self.query_strava_athlete = self.client.get_athlete()
        #     self.query_strava_atl_id = self.query_strava_athlete.id
        #     print(self.query_strava_athlete)
        #     print(self.query_strava_atl_id)
        # return

    # def resume_access_after_query(self):
    #     # print("bellow the strava code :")
    #     # print(self.atl_strava_code)
    #     user_access_token = ''
    #     user_access_token = self.client.exchange_code_for_token(client_id=self.MY_STRAVA_CLIENT_ID,
    #                 client_secret=self.MY_STRAVA_CLIENT_SECRET,
    #                 code=self.atl_strava_code)
    #     # print(user_access_token)
    #     if user_access_token:
    #         self.query_strava_athlete = ''
    #         self.query_strava_atl_id = 0
    #         # print(self.query_strava_athlete)
    #         # print(self.query_strava_atl_id)
    #     return

    def get_atl_last_efforts(self, limit, start_date, finish_date):
        '''
        This function get all efforts from the last activities of an athlete
        '''
        if self.client:
            list_atl_last_act = []
            list_atl_last_efforts = []
            limit_count = 0
            after_date = start_date - timedelta(days=1)
            before_date = finish_date + timedelta(days=1)
            after_datetime = datetime.combine(after_date, datetime.min.time())
            before_datetime = datetime.combine(before_date, datetime.min.time())
            # print(before_datetime)
            int_atl_act = self.client.get_activities(after=after_datetime, before=before_datetime)
            list_atl_last_act = list_atl_last_act + list(int_atl_act)
            for atl_act in list_atl_last_act:
                if atl_act.type == "Ride":
                    int_act_segment_efforts = self.client.get_activity(atl_act.id).segment_efforts
                    list_atl_last_efforts = list_atl_last_efforts + list(int_act_segment_efforts)
                    limit_count = limit_count + 1
                    if limit_count == limit:
                        break
            return list_atl_last_efforts

    def get_unique_segments_from_efforts(list_efforts):
        '''
        This function get the segments from a list of efforts
        Repeated segments are not included in the list
        '''
        list_unique_segments = []
        control = []
        for eff in list_efforts:
            if not eff.segment.id in control and not eff.hidden:
                control = control + [eff.segment.id]
                list_unique_segments = list_unique_segments + [ eff.segment ]
                # print(str(eff.segment.id) + " " + eff.segment.name + " " + str(eff.segment.distance) + " " + str(eff.segment.average_grade))
                # print(str(eff.segment.name) + " " + str(eff.hidden))
        return list_unique_segments

# Test routines bellow

    def get_atl_activities(self, limit):
        '''
        This function get the last activities of an athlete
        '''
        if self.client:
            int_atl_act = self.client.get_activities(limit=limit)
            list_atl_act = list(int_atl_act)
            return list_atl_act

    def get_efforts_segment(self,segment_id, start_date_local, end_date_local, limit):
        '''
        This function get efforts from a athlete in a segment, ordererd by the best results
        '''

        # print("{} {} {} {}".format(segment_id, start_date_local, end_date_local, limit))
        int_seg_eff = self.client.get_segment_efforts(segment_id=segment_id,
                            start_date_local= start_date_local, end_date_local = end_date_local,
                            limit=limit)
        try:
            list_seg_eff = list(int_seg_eff)
            # for seg_eff in list_seg_eff:
            #     print(seg_eff.elapsed_time)
            #     print(seg_eff.start_date)
            return list_seg_eff
        except :
            print("não autenticado")
