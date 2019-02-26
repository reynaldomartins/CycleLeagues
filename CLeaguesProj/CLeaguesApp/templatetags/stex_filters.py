from django import template
from CLeaguesApp.st_functions import (tour_status_str, cleagues_status, athlete_status_str,
                                 filter_league_feed_by_status, filter_league_feed_by_status_athlete,
                                 create_list, filter_atl_best_trial_feed_by_seg,
                                 filter_atl_best_trial_feed_by_atl, filter_tour_feed_by_strstatus,
                                 count_list, define, add_one, rank_translation, rank_translation_small,
                                 append_list, is_you)

register = template.Library()

def subtract(value, arg):
    return value - arg

register.filter('subtract', subtract)

register.simple_tag(tour_status_str)
register.simple_tag(cleagues_status)
register.simple_tag(athlete_status_str)
register.simple_tag(filter_league_feed_by_status)
register.simple_tag(filter_league_feed_by_status_athlete)
register.simple_tag(create_list)
register.simple_tag(filter_atl_best_trial_feed_by_seg)
register.simple_tag(filter_atl_best_trial_feed_by_atl)
register.simple_tag(is_you)
register.simple_tag(filter_tour_feed_by_strstatus)
register.simple_tag(count_list)
register.simple_tag(define)
register.simple_tag(add_one)
register.simple_tag(rank_translation)
register.simple_tag(rank_translation_small)
register.simple_tag(append_list)
