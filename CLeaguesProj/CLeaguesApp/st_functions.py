from datetime import datetime
from PIL import Image
from io import BytesIO
import sys
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from .models import NOT_RANKED

def filter_athletes(list_atl_source, list_atl_control):
    control_atl_id = [atl.atl_id for atl in list_atl_control]
    return [atl for atl in list_atl_source if atl.atl_id not in control_atl_id]

def filter_league_feed_by_status(list_league_feed, status):
    return [league_feed for league_feed in list_league_feed if league_feed.league.lg_status == status]

def filter_league_feed_by_status_athlete(list_league_feed, status):
    return [league_feed for league_feed in list_league_feed if league_feed.logged_strive_atl_league_status == status]

def append_list(list1,list2):
    return list1 + list2

def filter_atl_best_trial_feed_by_seg(list_best_trial_feed, sg_id):
    list_atl_best_trial_feed_filtered = [best_trial_feed for best_trial_feed in list_best_trial_feed if best_trial_feed.atl_best_trial.abt_sg.sg_id == sg_id]
    list_atl_best_trial_feed_filtered.sort(key=lambda x: x.atl_best_trial.abt_rank, reverse=False)
    return list_atl_best_trial_feed_filtered

def filter_atl_best_trial_feed_by_atl(list_best_trial_feed, atl_id):
    list_atl_best_trial_feed_filtered = [best_trial_feed for best_trial_feed in list_best_trial_feed if best_trial_feed.atl_best_trial.abt_atl.atl_id == atl_id]
    list_atl_best_trial_feed_filtered.sort(key=lambda x: x.sg_name_strava, reverse=False)
    return list_atl_best_trial_feed_filtered

def filter_tour_feed_by_strstatus(list_tours_feed, status):
    list_tours_feed_filtered = []
    for tour_feed in list_tours_feed:
        if tour_feed.tour.tour_status() == status:
            list_tours_feed_filtered.append(tour_feed)
    return list_tours_feed_filtered

def count_list(list):
    return len(list)

def create_list(*args):
    list = []
    for item in args:
        list.append(item)
    return list

def define(val):
  return val;

def add_one(val):
  return val+1;

def tour_status_str(status):
    if status == "T":
            return "To be Started"
    elif status == "A":
            return "Running"
    elif status == "I":
        return "Inactive"
    # status is equal to "F" or "Z"
    else:
        return "Finished"

def athlete_status_str(status):
    if status == "A":
        return "Active"
    elif status == "I":
        return "Inactive"
    # status is equal to "C"
    else:
        return "Pending"

def strive_status(status):
    if status == "A":
        return "Active"
    else:
        return "Inactive"

def rank_translation(rank,points):
    if rank == NOT_RANKED:
        return "Not Ranked"
    elif points == 0:
        return "Did not Start (DNS)"
    else:
        return rank

def rank_translation_small(rank,points):
    if rank == NOT_RANKED:
        return "-"
    elif points == 0:
        return "DNS"
    else:
        return rank

def resize_image(uploaded_image, width_height):
        '''
        Get a class ImageField object and resize it, formating it as JPEG
        It returns the Image resized if everyhting is already
        Otherwise it returns a empty object
        '''
        try:
            imageTemporary = Image.open(uploaded_image)
            original_width, original_height = imageTemporary.size
            print("{} {}".format(original_width, original_height))
            if original_width > original_height:
                start_point = (original_width-original_height)/2
                imageTemporary = imageTemporary.crop((start_point,0,start_point+original_height,original_height))
                cropped_size = original_height
                print("{} {}".format(start_point, cropped_size))
            elif original_width < original_height:
                start_point = (original_height-original_width)/2
                imageTemporary = imageTemporary.crop((0,start_point,original_width,start_point+original_width))
                cropped_size = original_width
                print("{} {}".format(start_point, cropped_size))
            else:
                cropped_size = original_width
            if cropped_size > width_height:
                print("I will resized from {} to {}".format(cropped_size,width_height))
                imageTemporary = imageTemporary.resize( (width_height, width_height) )
            outputIoStream = BytesIO()
            imageTemporary.save(outputIoStream , format='JPEG', quality=100)
            outputIoStream.seek(0)
            uploaded_image_resized = InMemoryUploadedFile(outputIoStream,'ImageField', "%s.jpg" %uploaded_image.name.split('.')[0], 'image/jpeg', sys.getsizeof(outputIoStream), None)
            return uploaded_image_resized
        except:
            return ''
