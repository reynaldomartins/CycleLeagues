import boto3
from botocore.exceptions import ClientError
from .models import *
from CLeaguesProj.settings import MEDIA_URL, STATIC_DIR, MEDIA_DIR, BASE_DIR, STATIC_URL
from .st_functions import *

SENDER = "cycleleagues@cycleleagues.com"
CHARSET = "UTF-8"
CONFIGURATION_SET = "ConfigSet"
AWS_REGION = "us-west-2"
client = boto3.client('ses',region_name=AWS_REGION)

def send_email(subject, body_text, body_html, recipient):
    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    recipient,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])

def test_notification(logged_cleagues_athlete):
    list_tours_qs = Tour.objects.all()
    for tour in list_tours_qs:
        if tour.tour_status() in ["T"]:
            subject, body_text, body_html = set_notification_tour(logged_cleagues_athlete, tour)
            send_email(subject, body_text, body_html, "reynaldo.martins@globo.com")

def run_batch_send_email_notifications():
    event_record_qs = EventRecord.objects.all().filter(er_status="U")
    for event_record in event_record_qs:
        if event_record.er_type == "LEGINV":
            atl_qs = Athlete.objects.all().filter(atl_id= event_record.er_arg1)
            if atl_qs:
                athlete = atl_qs[0]
                if athlete.atl_email_strava:
                    league_qs = League.objects.all().filter(lg_id = event_record.er_arg2)
                    if league_qs:
                        subject, body_text, body_html = get_email_league_invitation_notification(athlete, league_qs[0])
                        if subject:
                            send_email(subject, body_text, body_html, athlete.atl_email_strava)
                            event_record.set_notified()
                else:
                    event_record.set_notified()
        elif event_record.er_type in ["TRCREA" , "TRSDAY"]:
            atl_qs = Athlete.objects.all().filter(atl_id= event_record.er_arg1)
            if atl_qs:
                athlete = atl_qs[0]
                if athlete.atl_email_strava:
                    tour_qs = Tour.objects.all().filter(tr_id = event_record.er_arg2)
                    if tour_qs:
                        if event_record.er_type == "TRSDAY":
                            subject, title_html = get_subject_and_title(event_record.er_type, event_record.er_arg3)
                        else:
                            subject, title_html = get_subject_and_title(event_record.er_type)
                        body_text, body_html = get_email_tour_athletes_segments_notification(athlete, tour_qs[0],title_html)
                        if body_html:
                            send_email(subject, body_text, body_html, athlete.atl_email_strava)
                            event_record.set_notified()
                else:
                    event_record.set_notified()
        elif event_record.er_type in ["TRSTAR","TRFINI","TRJRN","TRFDAY"]:
            atl_qs = Athlete.objects.all().filter(atl_id= event_record.er_arg1)
            if atl_qs:
                athlete = atl_qs[0]
                if athlete.atl_email_strava:
                    tour_qs = Tour.objects.all().filter(tr_id = event_record.er_arg2)
                    if tour_qs:
                        if event_record.er_type == "TRFDAY":
                            subject, title_html = get_subject_and_title(event_record.er_type, event_record.er_arg3)
                        else:
                            subject, title_html = get_subject_and_title(event_record.er_type)
                        body_text, body_html = get_email_tour_rank_segments_notification(athlete, tour_qs[0], title_html)
                        if body_html:
                            send_email(subject, body_text, body_html, athlete.atl_email_strava)
                            event_record.set_notified()
                else:
                    event_record.set_notified()

def get_subject_and_title(er_type, *args):
    if er_type == "TRCREA":
        subject = "CycleLeagues - A Tour has just been Created"
        title_html = ("""
        <h3>You are now taking part in a
        <span style="font-weight:bold;color:orangered;"> Tour </span>
        which has just been
        <span style="font-weight:bold;color:orangered;"> Created</span></h3>
        """)
    elif er_type == "TRSTAR":
        subject = "CycleLeagues - A Tour has just Started"
        title_html = ("""
        <h3>A
        <span style="font-weight:bold;color:orangered;"> Tour </span>
        in which You are running has just
        <span style="font-weight:bold;color:orangered;"> Started</span>
        </h3>
        """)
    elif er_type == "TRFINI":
        subject = "CycleLeagues - A Tour has just Finished"
        title_html = ("""
        <h3>A
        <span style="font-weight:bold;color:orangered;"> Tour </span>
        in which You are running has just
        <span style="font-weight:bold;color:orangered;"> Finished </span>
        - Look the FINAL RANKING
        </h3>
        """)
    elif er_type == "TRJRN":
        subject = "CycleLeagues - Tour Journal"
        title_html = ("""
        <h3>
        <span style="font-weight:bold;color:orangered;">Tour Ranking Update</span>
        </h3>
        """)
    elif er_type == "TRFDAY":
        subject = "CycleLeagues - A Tour is About to Finish"
        title_html = ("""
        <h3>A
        <span style="font-weight:bold;color:orangered;"> Tour </span>
        in which You are running is about to
        <span style="font-weight:bold;color:orangered;"> Finish within """ + str(args[0]) + """ days</span>
        </h3>
        """)
    elif er_type == "TRSDAY":
        subject = "CycleLeagues - A Tour is About to Start"
        title_html = ("""
        <h3>A
        <span style="font-weight:bold;color:orangered;"> Tour </span>
        in which You are taking part is about to
        <span style="font-weight:bold;color:orangered;"> Start within """ + str(args[0]) + """ days</span>
        </h3>
        """)
    else:
        return "", ""
    return subject, title_html

def get_email_league_invitation_notification(athlete, league):

    list_athletes_league_ext = league.get_athletes_in_league()
    list_tours_league = league.get_tours()

    subject = "CycleLeagues - You have been invited to Join a League"
    body_text = ""
    body_html = ( """
    <html>
    <head></head>
    <body>
        <div style="text-align: center;"> """)

    body_html = body_html + get_html_cycleleagues_head()

    body_html = body_html + ("""
            <h3>You have just been Invited to <span style="font-weight:bold;color:orangered;">Join a League</span></h3>
            <table align=center><tbody><tr>
                <td>
                    <h4><span style="font-weight:bold;color:orangered;">League</span>&nbsp;&nbsp;
                </td>
                <td>
                    <img class="img-circle" width="80" height="80" src=""" + MEDIA_URL + league.lg_pic.url + """ " />
                </td>
                <td>
                    &nbsp;<b>""" + league.lg_name + """</b>
                </td>
                <td>
                    <i><span style="font-size:.8em;">&nbsp; created by &nbsp;</span>
                </td>
                <td>
                    <img class="img-circle" width="40" height="40" src=" """ + MEDIA_URL + league.lg_atl_creator.atl_pic.url + """ " />
                </td>
                <td>
                    <i><span style="font-size:.8em;">&nbsp;""" + league.lg_atl_creator.atl_name_strava + """
                    <span style="color:red;font-weight: normal;">""" + is_you(athlete.atl_id,league.lg_atl_creator.atl_id) + """</span>
                    </span></i>
                </td>
           </tr></tbody></table>
        </div>
        <br>
        <div style="background-color: white;
                      padding: 10px;
                      border-radius: 10px;
                      border: lightblue 3px solid;">
            <table>
                <thead>
                  <th></th>
                  <th>Athletes in this League</th>
                </thead>
                <tbody>""" )

    for atl_in_lg_ext in list_athletes_league_ext:
        if atl_in_lg_ext.atl_in_league_status != "I":
            body_html = body_html + ("""
                        <tr>
                          <td>
                            <img class="img-circle" width="40" height="40" src=" """ +  MEDIA_URL + atl_in_lg_ext.atl.atl_pic.url + """ "/>
                          </td>
                          <td style="text-align:left;">
                              <strong>""" + atl_in_lg_ext.atl.atl_name_strava + """</strong>
                              <span style="color:red;font-weight: normal;">""" + is_you(athlete.atl_id,  atl_in_lg_ext.atl.atl_id) + """</span>
                              (""" + athlete_status_str(atl_in_lg_ext.atl_in_league_status) + """)
                           </td>
                        </tr>""" )

    body_html = body_html + ( """
                </tbody>
            </table>
        </div>
        <br>
        <div style="background-color: white;
                      padding: 10x;
                      border-radius: 10px;
                      border: lightblue 3px solid;">
                <table>
                    <thead>
                      <th style="width:10%;"></th>
                      <th style="width:30%;">Tours in this League</th>
                      <th style="width:18%;">Start Date</th>
                      <th style="width:18%;">Finish Date</th>
                      <th style="width:24%;">Status</th>
                    </thead>
                    <tbody>""")

    for tour in list_tours_league:
        body_html = body_html + ( """
                        <tr>
                            <td style="padding-right: 5px;
                                        padding-left: 5px;
                                        border: 1px solid white;
                                        border-color : white;
                                        text-align:center;">
                                <img class="img-circle" width="40" height="40" src=" """ + MEDIA_URL + tour.tr_pic.url + """ " />
                            &nbsp;</td>
                            <td style="padding-right: 5px;
                                        padding-left: 5px;
                                        border: 1px solid white;
                                        border-color : white lightblue white white;
                                        text-align:left;">
                                    <strong>""" + tour.tr_name + """</strong>
                            </td>
                            <td style="padding-right: 5px;
                                        padding-left: 5px;
                                        border: 1px solid white;
                                        border-color : white lightblue white white;
                                        text-align:center;">""" + str(tour.tr_start_date) + """
                            </td>
                            <td style="padding-right: 5px;
                                        padding-left: 5px;
                                        border: 1px solid white;
                                        border-color : white lightblue white white;
                                        text-align:center;">""" + str(tour.tr_finish_date) + """
                            </td>
                            <td style="padding-right: 5px;
                                        padding-left: 5px;
                                        border: 1px solid white;
                                        border-color : white;
                                        text-align:center;">""" + tour_status_str( tour.tour_status() ) + """
                            </td>
                        </tr>""" )

    body_html = body_html + ("""
                    </tbody>
                </table>
            </div>
        <br>""")

    body_html = body_html + get_html_footnote()

    body_html = body_html + ("""
    </body>
    </html>
            """ )

    return subject, body_text, body_html

###############################################################################

def get_tour_email_data(athlete, tour):
    # Get the status of the notified Athlete in the League of this Tour
    atl_in_league_status = AtlInLeague.objects.all().filter(ail_atl__atl_id = athlete.atl_id,
                                                            ail_lg__lg_id = tour.tr_lg.lg_id)[0].ail_status

    # Get the list of all Athletes in this Tour
    list_athletes_tour = list(AtlInTour.objects.all().filter(ait_tr__tr_id = tour.tr_id))

    # Get the Atl in Tour object for the notified Athlete
    notified_atl_in_tour_lst = [atl_in_tour for atl_in_tour in list_athletes_tour if atl_in_tour.ait_atl.atl_id == athlete.atl_id]

    if notified_atl_in_tour_lst == []:
        notified_atl_in_tour = ''
    else:
        notified_atl_in_tour = notified_atl_in_tour_lst[0]

    # Get all segments in this Tour
    list_tour_segments = tour.get_segments()

    tour_summary = tour.get_summary()

    return atl_in_league_status, list_athletes_tour, notified_atl_in_tour, list_tour_segments, tour_summary

def get_email_tour_athletes_segments_notification(athlete, tour, title_html):
    atl_in_league_status, list_athletes_tour, notified_atl_in_tour, list_tour_segments, tour_summary = get_tour_email_data(athlete, tour)

    if not notified_atl_in_tour:
        return "", "", ""


    body_text = ""
    body_html = ( """
    <html>
    <head></head>
    <body> """)
    body_html = body_html + ("""
        <div style="text-align: center;">""")
    body_html = body_html + get_html_cycleleagues_head()
    body_html = body_html + title_html
    body_html = body_html + ("""
        <br>
        <div align=center style="background-color: white;
                      padding: 10px;
                      border-radius: 10px;
                      border: lightblue 3px solid;
                      position: relative;
                      display: inline-block;">""")
    body_html = body_html + get_html_tour_head_summary(tour, athlete, tour_summary,notified_atl_in_tour)
    body_html = body_html + ("""
        </div>""")
    body_html = body_html + ("""
    </div>
    <br>
    """)
    body_html = body_html + ("""
            <div style="background-color: white;
                          padding: 10px;
                          border-radius: 10px;
                          border: lightblue 3px solid;">""")
    body_html = body_html + get_html_athletes_in_tour(list_athletes_tour, athlete)
    body_html = body_html +  ("""
            </div>
            <br>""" )
    body_html = body_html + ( """
        <div style="background-color: white;
                      padding: 10px;
                      border-radius: 10px;
                      border: lightblue 3px solid;">""")
    body_html = body_html + get_html_segments_in_tour(list_tour_segments)
    body_html = body_html + ("""
        </div>
        <br>""")
    body_html = body_html + get_html_footnote()
    body_html = body_html + ("""
    </body>
    </html>
            """ )
    return body_text, body_html

def get_email_tour_rank_segments_notification(athlete, tour, title_html):
    atl_in_league_status, list_athletes_tour, notified_atl_in_tour, list_tour_segments, tour_summary = get_tour_email_data(athlete, tour)

    if not notified_atl_in_tour:
        return "", "", ""

    body_text = ""
    body_html = ( """
    <html>
    <head></head>
    <body> """)
    body_html = body_html + ("""
        <div style="text-align: center;">""")
    body_html = body_html + get_html_cycleleagues_head()
    body_html = body_html + title_html
    body_html = body_html + ("""
        <br>
        <div align=center style="background-color: white;
                      padding: 10px;
                      border-radius: 10px;
                      border: lightblue 3px solid;
                      position: relative;
                      display: inline-block;">""")
    body_html = body_html + get_html_tour_head_summary(tour, athlete, tour_summary,notified_atl_in_tour)
    body_html = body_html + ("""
        </div>""")
    body_html = body_html + ("""
    </div>
    <br>
    """)
    body_html = body_html + ("""
            <div style="background-color: white;
                          padding: 10px;
                          border-radius: 10px;
                          border: lightblue 3px solid;">""")
    body_html = body_html + get_html_tour_rank(list_athletes_tour, athlete, tour_summary)
    body_html = body_html +  ("""
            </div>
            <br>""" )
    body_html = body_html + ( """
        <div style="background-color: white;
                      padding: 10px;
                      border-radius: 10px;
                      border: lightblue 3px solid;">""")
    body_html = body_html + get_html_segments_in_tour(list_tour_segments)
    body_html = body_html + ("""
        </div>
        <br>""")
    body_html = body_html + get_html_footnote()
    body_html = body_html + ("""
    </body>
    </html>
            """ )
    return body_text, body_html

def get_html_cycleleagues_head():
    return ("""
            <table align=center><tbody>
              <tr>
                  <td>
                    """ + str(STATIC_DIR + "images/CycleLeaguesIcon.png") + """
                  </td>
              </tr>
              <tr>
                  <td>
                    """ + str(STATIC_URL + "images/CycleLeaguesIcon.png") + """
                  </td>
              </tr>
              <tr>
                  <td>
                    <img class="img-circle" width="80" height="80" src=" """ + STATIC_URL + """images/CycleLeaguesIcon.png" />
                  </td>
                  <td>
                    <h3 style="display: inline-block;">&nbsp;&nbsp;CycleLeagues</h3>
                  </td>
              </tr>
            </tbody></table>""")

def get_html_tour_head_summary(tour, athlete, tour_summary,notified_atl_in_tour):
    body_html = ("""
            <table align=center><tbody><tr>
                <td>
                    <h4><span style="font-weight:bold;color:orangered;">Tour</span>&nbsp;&nbsp;
                </td>
                <td>
                    <img class="img-circle" width="80" height="80" src=""" + MEDIA_URL + tour.tr_pic.url + """ " />
                </td>
                <td>
                    &nbsp;<b>""" + tour.tr_name + """</b>
                </td>
                <td>
                    <i><span style="font-size:.8em;">&nbsp; from League&nbsp;</span>
                </td>
                <td>
                    <img class="img-circle" width="40" height="40" src=" """ + MEDIA_URL + tour.tr_lg.lg_pic.url + """ " />
                </td>
                <td>
                    <i><span style="font-size:.8em;">&nbsp;""" + tour.tr_lg.lg_name + """</i>
                </td>
           </tr></tbody></table>""")

    body_html = body_html + ("""
        <table align=center style="font-weight: normal;">
            <thead>
            <th>Athletes</th>
            <th>Segments</th>
            <th>Start</th>
            <th>Finish</th>""")

    if tour_summary['days_to_go' ] >= 0 :
        body_html = body_html + ("""
                                  <th>Days to Go</th>
                                  <th>Status</th>
                                  <th><span style="color:red;font-weight: normal;">Your</span>&nbsp;Rank</th>
                                  <th><strong>Leader</strong></th>""")
    else:
        body_html = body_html + ("""
                                  <th>Status</th>
                                  <th><span style="color:red;font-weight: normal;">Your</span>&nbsp;Rank</th>
                                  <th><strong>Winner</strong></th>""")

    body_html = body_html + ("""
        </thead>
        <tbody>
            <tr>
              <td style="padding-right: 5px;
                          padding-left: 5px;
                          border: 1px solid white;
                          border-color : white lightblue white white;
                          text-align:center;">""" + str(tour_summary['num_athletes']) + """</td>
              <td style="padding-right: 5px;
                          padding-left: 5px;
                          border: 1px solid white;
                          border-color : white lightblue white white;
                          text-align:center;">""" + str(tour_summary[ 'num_segments' ]) + """</td>
              <td style="padding-right: 5px;
                          padding-left: 5px;
                          border: 1px solid white;
                          border-color : white lightblue white white;
                          text-align:center;">""" + str(tour.tr_start_date) + """</td>
              <td style="padding-right: 5px;
                          padding-left: 5px;
                          border: 1px solid white;
                          border-color : white lightblue white white;
                          text-align:center;">""" + str(tour.tr_finish_date) + """</td>""")

    if tour_summary['days_to_go'] >= 0:
        body_html = body_html + ("""
            <td style="padding-right: 5px;
                        padding-left: 5px;
                        border: 1px solid white;
                        border-color : white lightblue white white;
                        text-align:center;">""" + str(tour_summary[ 'days_to_go' ]) + """</td>""")

    body_html = body_html + ("""
              <td style="padding-right: 5px;
                          padding-left: 5px;
                          border: 1px solid white;
                          border-color : white lightblue white white;
                          text-align:center;">""" + tour_status_str(tour.tr_status) + """</td>
              <td style="padding-right: 5px;
                          padding-left: 5px;
                          border: 1px solid white;
                          border-color : white lightblue white white;
                          text-align:center;">
                <span class="td-text-realce">""" + str(rank_translation_small(notified_atl_in_tour.ait_rank, notified_atl_in_tour.ait_points)) +
                """</span>/ """ + str(tour_summary[ 'num_athletes' ]) + """
              </td>
              <td style="padding-right: 5px;
                          padding-left: 5px;
                          border: 1px solid white;
                          border-color : white;
                          text-align:center;">""")

    # if tour_summary['leader_pic'] :
    #     body_html = body_html + ("""
    #             <img class="img-circle" width="40" height="40" src=" """+ MEDIA_URL + tour_summary[ 'leader_pic' ] + """ "/>""")

    body_html = body_html + ("""
                <strong>
                  """ + tour_summary[ 'leader_name' ] + """
                  <span style="color:red;font-weight: normal;">""" + is_you(athlete.atl_id, tour_summary[ 'leader_id' ]) + """</span>
                </strong>
              </td>
            </tr>
        </tbody>
        </table>""")
    return body_html

def get_html_athletes_in_tour(list_athletes_tour, athlete):
    body_html = ("""
                <table>
                    <thead>
                      <th></th>
                      <th>Athletes in this Tour</th>
                    </thead>
                    <tbody>""")

    # Pending - Do not show ATL if he is inactivated in a League

    for atl_in_tr in list_athletes_tour:
        body_html = body_html + ("""
                        <tr>
                          <td>
                            <img class="img-circle" width="40" height="40" src=" """ +  MEDIA_URL + atl_in_tr.ait_atl.atl_pic.url + """ "/>
                          </td>
                          <td style="text-align:left;">
                              <strong>""" + atl_in_tr.ait_atl.atl_name_strava + """</strong>
                              <span style="color:red;font-weight: normal;">""" + is_you(athlete.atl_id, atl_in_tr.ait_atl.atl_id) + """</span>
                           </td>
                        </tr>""")

    body_html = body_html + ("""</tbody>
                </table>""")
    return body_html

def get_html_segments_in_tour(list_tour_segments):
    if list_tour_segments:
        body_html = ( """
                <table>
                    <thead>
                      <th>Segments in this Tour</th>
                      <th>Distance</th>
                      <th>Average Grade</th>
                      <th>Elevation Diff.</th>
                    </thead>
                    <tbody>""")

        for seg in list_tour_segments:
            body_html = body_html + ( """
                            <tr>
                                <td style="padding-right: 5px;
                                            padding-left: 5px;
                                            border: 1px solid white;
                                            border-color : white lightblue white white;
                                            text-align:left;">
                                    <strong>""" + seg.sg_name_strava + """</strong>
                                </td>
                                <td style="padding-right: 5px;
                                            padding-left: 5px;
                                            border: 1px solid white;
                                            border-color : white lightblue white white;
                                            text-align:center;">
                                        """ + str(seg.sg_distance) + """ km
                                </td>
                                <td style="padding-right: 5px;
                                            padding-left: 5px;
                                            border: 1px solid white;
                                            border-color : white lightblue white white;
                                            text-align:center;">""" + str(seg.sg_avg_grade) + """ %
                                </td>
                                <td style="padding-right: 5px;
                                            padding-left: 5px;
                                            border: 1px solid white;
                                            border-color : white;
                                            text-align:center;">""" + str(seg.sg_high_elev-seg.sg_low_elev) + """ mts
                                </td>
                            </tr>""" )
        body_html = body_html + ("""
                        </tbody>
                    </table>""")
    else:
        body_html = ("""<p>No segments were selected for this Tour yet</p>""")
    return body_html

def get_html_footnote():
    return ("""
    <div style="text-align: center;">
        <h4>
            <a href='http://www.cycleleagues.com/'>www.CycleLeagues.com</a>
        </h4>
    </div>""")


def get_html_tour_rank(list_atl_in_tour, athlete, tour_summary):
    body_html = ("""
    <table>
        <thead>
            <th>Rank</th>
            <th></th>
            <th>Athlete</th>
            <th>Points</th>
            <th>Segments Riden</th>
            <th>Segments to Ride</th>
        </thead>
        <tbody>""")

    list_atl_in_tour.sort(key=lambda x: x.ait_rank, reverse=False)

    for ait in list_atl_in_tour:
        if ait.ait_status == "A":

            ridden_left = tour_summary[ 'num_segments' ] - ait.ait_ridden

            body_html = body_html + ("""
                <tr>
                    <td>""" +  str(MEDIA_DIR + ait.ait_atl.atl_pic_mini.url) + """ </td>
                </tr>
                <tr>
                    <td>""" +  str(MEDIA_URL + ait.ait_atl.atl_pic_mini.url) + """ </td>
                </tr>
                <tr>
                  <td style="padding-right: 5px;
                              padding-left: 5px;
                              border: 1px solid white;
                              border-color : white lightblue white white;
                              text-align:left;">""" + str(rank_translation(ait.ait_rank, ait.ait_points)) + """</td>
                  <td style="padding-right: 5px;
                              padding-left: 5px;
                              border: 1px solid white;
                              border-color : white;
                              text-align:left;">
                      <img class="img-circle" width="40" height="40"src=" """ + MEDIA_URL + ait.ait_atl.atl_pic_mini.url + """ " />
                  </td>
                  <td style="padding-right: 5px;
                              padding-left: 5px;
                              border: 1px solid white;
                              border-color : white lightblue white white;
                              text-align:left;">
                      &nbsp;&nbsp;""" + ait.ait_atl.atl_name_strava + """
                      <span style="color:red;font-weight: normal;">""" + is_you(athlete.atl_id, ait.ait_atl.atl_id) + """</span>
                  </td>
                  <td style="padding-right: 5px;
                              padding-left: 5px;
                              border: 1px solid white;
                              border-color : white lightblue white white;
                              text-align:center;"> """ + str(ait.ait_points) + """</td>
                  <td style="padding-right: 5px;
                              padding-left: 5px;
                              border: 1px solid white;
                              border-color : white lightblue white white;
                              text-align:center;"> """ + str(ait.ait_ridden) + """</td>
                  <td style="padding-right: 5px;
                              padding-left: 5px;
                              border: 1px solid white;
                              border-color : white;
                              text-align:center;"> """ + str(ridden_left) + """</td>
                </tr>""")

    body_html = body_html + ("""
        </tbody>
        </table>""")
    return body_html
