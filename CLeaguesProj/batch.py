import os

if __name__ == '__main__' and __package__ is None:
    os.sys.path.append(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CLeaguesProj.settings")

import django
from django.conf import settings
django.setup()

from CLeaguesApp.models import Tour
from CLeaguesApp.email_notifications import run_batch_send_email_notifications

def main():
    print("Hello world")

    list_tours = Tour.objects.all()
    for tour in list_tours:
        print(tour.tr_name)

    # for tour in list_tours:
    #     tour.update_ranking()
    #     tour.create_notification_events()
    #
    # # Send Notifications
    # run_batch_send_email_notifications()

    print("OK")

if __name__ == "__main__":
    main()
