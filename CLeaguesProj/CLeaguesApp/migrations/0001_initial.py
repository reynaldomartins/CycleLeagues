# Generated by Django 2.1.1 on 2018-12-17 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Athlete',
            fields=[
                ('atl_id', models.IntegerField(db_column='ATL_id', primary_key=True, serialize=False)),
                ('atl_name_strava', models.CharField(blank=True, db_column='ATL_name_strava', max_length=80, null=True)),
                ('atl_id_strava', models.IntegerField(blank=True, db_column='ATL_id_strava', null=True, unique=True)),
                ('atl_email_strava', models.CharField(blank=True, db_column='ATL_email_strava', max_length=80, null=True)),
                ('atl_birth_date_strava', models.DateField(blank=True, db_column='ATL_birth_date_strava', null=True)),
                ('atl_status', models.CharField(db_column='ATL_status', max_length=1)),
                ('atl_creation_timestamp', models.DateTimeField(db_column='ATL_creation_timestamp')),
                ('atl_activation_timestamp', models.DateTimeField(db_column='ATL_activation_timestamp')),
                ('atl_inactivation_timestamp', models.DateTimeField(db_column='ATL_inactivation_timestamp')),
            ],
            options={
                'db_table': 'athlete',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AtlBestTrial',
            fields=[
                ('abt_atl', models.IntegerField(db_column='ABT_atl_id', primary_key=True, serialize=False)),
                ('abt_tr', models.IntegerField(db_column='ABT_tr_id')),
                ('abt_sg', models.IntegerField(db_column='ABT_sg_id')),
                ('abt_date', models.DateField(db_column='ABT_date')),
                ('abt_time', models.TimeField(db_column='ABT_time')),
                ('abt_rank', models.IntegerField(db_column='ABT_rank')),
                ('abt_points', models.IntegerField(db_column='ABT_points')),
            ],
            options={
                'db_table': 'atl_best_trial',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AtlInLeague',
            fields=[
                ('ail_atl', models.IntegerField(db_column='AIL_atl_id', primary_key=True, serialize=False)),
                ('ail_lg', models.IntegerField(db_column='AIL_lg_id')),
                ('ail_atl_nick_name', models.CharField(blank=True, db_column='AIL_atl_nick_name', max_length=80, null=True)),
                ('ail_status', models.CharField(blank=True, db_column='AIL_status', max_length=1, null=True)),
                ('ail_creation_timestamp', models.DateTimeField(db_column='AIL_creation_timestamp')),
                ('ail_activation_timestamp', models.DateTimeField(db_column='AIL_activation_timestamp')),
                ('ail_inactivation_timestamp', models.DateTimeField(db_column='AIL_inactivation_timestamp')),
            ],
            options={
                'db_table': 'atl_in_league',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AtlInTour',
            fields=[
                ('ait_atl', models.IntegerField(db_column='AIT_atl_id', primary_key=True, serialize=False)),
                ('ait_tr', models.IntegerField(db_column='AIT_tr_id')),
                ('ait_position', models.IntegerField(blank=True, db_column='AIT_position', null=True)),
                ('ait_riden', models.IntegerField(blank=True, db_column='AIT_riden', null=True)),
                ('ait_completed', models.IntegerField(blank=True, db_column='AIT_completed', null=True)),
                ('ait_status', models.CharField(blank=True, db_column='AIT_status', max_length=1, null=True)),
                ('ait_inactivation_timestamp', models.DateTimeField(db_column='AIT_inactivation_timestamp')),
            ],
            options={
                'db_table': 'atl_in_tour',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='League',
            fields=[
                ('lg_id', models.IntegerField(db_column='LG_id', primary_key=True, serialize=False)),
                ('lg_name', models.CharField(db_column='LG_name', max_length=80, unique=True)),
                ('lg_activation_code', models.IntegerField(db_column='LG_activation_code')),
                ('lg_status', models.CharField(db_column='LG_status', max_length=1)),
                ('lg_creation_timestamp', models.DateTimeField(db_column='LG_creation_timestamp')),
                ('lg_inactivation_timestamp', models.DateTimeField(db_column='LG_inactivation_timestamp')),
            ],
            options={
                'db_table': 'league',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ScoringSystem',
            fields=[
                ('ss_id', models.IntegerField(db_column='SS_id', primary_key=True, serialize=False)),
                ('ss_name', models.CharField(db_column='SS_name', max_length=80)),
                ('ss_pos1', models.IntegerField(blank=True, db_column='SS_pos1', null=True)),
                ('ss_pos2', models.IntegerField(blank=True, db_column='SS_pos2', null=True)),
                ('ss_pos3', models.IntegerField(blank=True, db_column='SS_pos3', null=True)),
                ('ss_pos4', models.IntegerField(blank=True, db_column='SS_pos4', null=True)),
                ('ss_pos5', models.IntegerField(blank=True, db_column='SS_pos5', null=True)),
                ('ss_pos6', models.IntegerField(blank=True, db_column='SS_pos6', null=True)),
                ('ss_pos7', models.IntegerField(blank=True, db_column='SS_pos7', null=True)),
                ('ss_pos8', models.IntegerField(blank=True, db_column='SS_pos8', null=True)),
                ('ss_pos9', models.IntegerField(blank=True, db_column='SS_pos9', null=True)),
                ('ss_pos10', models.IntegerField(blank=True, db_column='SS_pos10', null=True)),
                ('ss_pos11', models.IntegerField(blank=True, db_column='SS_pos11', null=True)),
                ('ss_pos12', models.IntegerField(blank=True, db_column='SS_pos12', null=True)),
                ('ss_pos13', models.IntegerField(blank=True, db_column='SS_pos13', null=True)),
                ('ss_pos14', models.IntegerField(blank=True, db_column='SS_pos14', null=True)),
                ('ss_pos15', models.IntegerField(blank=True, db_column='SS_pos15', null=True)),
                ('ss_pos16', models.IntegerField(blank=True, db_column='SS_pos16', null=True)),
                ('ss_pos17', models.IntegerField(blank=True, db_column='SS_pos17', null=True)),
                ('ss_pos18', models.IntegerField(blank=True, db_column='SS_pos18', null=True)),
                ('ss_pos19', models.IntegerField(blank=True, db_column='SS_pos19', null=True)),
                ('ss_pos20', models.IntegerField(blank=True, db_column='SS_pos20', null=True)),
                ('ss_pos21', models.IntegerField(blank=True, db_column='SS_pos21', null=True)),
                ('ss_pos22', models.IntegerField(blank=True, db_column='SS_pos22', null=True)),
                ('ss_pos23', models.IntegerField(blank=True, db_column='SS_pos23', null=True)),
                ('ss_pos24', models.IntegerField(blank=True, db_column='SS_pos24', null=True)),
                ('ss_pos25', models.IntegerField(blank=True, db_column='SS_pos25', null=True)),
                ('ss_pos26', models.IntegerField(blank=True, db_column='SS_pos26', null=True)),
                ('ss_pos27', models.IntegerField(blank=True, db_column='SS_pos27', null=True)),
                ('ss_pos28', models.IntegerField(blank=True, db_column='SS_pos28', null=True)),
                ('ss_pos29', models.IntegerField(blank=True, db_column='SS_pos29', null=True)),
                ('ss_pos30', models.IntegerField(blank=True, db_column='SS_pos30', null=True)),
                ('ss_status', models.CharField(db_column='SS_status', max_length=1)),
                ('ss_creation_timestamp', models.DateTimeField(db_column='SS_creation_timestamp')),
                ('ss_inactivation_timestamp', models.DateTimeField(db_column='SS_inactivation_timestamp')),
            ],
            options={
                'db_table': 'scoring_system',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SegInTour',
            fields=[
                ('sit_tr', models.IntegerField(db_column='SIT_tr_id', primary_key=True, serialize=False)),
                ('sit_sg', models.IntegerField(db_column='SIT_sg_id')),
                ('sit_status', models.CharField(db_column='SIT_status', max_length=1)),
                ('sit_creation_timestamp', models.DateTimeField(db_column='SIT_creation_timestamp')),
                ('sit_inactivation_timestamp', models.DateTimeField(db_column='SIT_inactivation_timestamp')),
            ],
            options={
                'db_table': 'seg_in_tour',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Segment',
            fields=[
                ('sg_id', models.IntegerField(db_column='SG_id', primary_key=True, serialize=False)),
                ('sg_name_strava', models.CharField(blank=True, db_column='SG_name_strava', max_length=80, null=True)),
                ('sg_id_strava', models.IntegerField(blank=True, db_column='SG_id_strava', null=True, unique=True)),
                ('sg_distance', models.FloatField(blank=True, db_column='SG_distance', null=True)),
                ('sg_avg_grade', models.FloatField(blank=True, db_column='SG_avg_grade', null=True)),
                ('sg_low_elev', models.IntegerField(blank=True, db_column='SG_low_elev', null=True)),
                ('sg_high_elev', models.IntegerField(blank=True, db_column='SG_high_elev', null=True)),
                ('sg_elev_dif', models.IntegerField(blank=True, db_column='SG_elev_dif', null=True)),
            ],
            options={
                'db_table': 'segment',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Tour',
            fields=[
                ('tr_id', models.IntegerField(db_column='TR_id', primary_key=True, serialize=False)),
                ('tr_name', models.CharField(db_column='TR_name', max_length=80)),
                ('tr_lg', models.IntegerField(blank=True, db_column='TR_lg_id', null=True)),
                ('tr_start_date', models.DateField(blank=True, db_column='TR_start_date', null=True)),
                ('tr_finish_date', models.DateField(db_column='TR_finish_date')),
                ('tr_activation_code', models.IntegerField(db_column='TR_activation_code')),
                ('tr_status', models.CharField(db_column='TR_status', max_length=1)),
                ('tr_creation_timestamp', models.DateTimeField(db_column='TR_creation_timestamp')),
                ('tr_inactivation_timestamp', models.DateTimeField(db_column='TR_inactivation_timestamp')),
            ],
            options={
                'db_table': 'tour',
                'managed': False,
            },
        ),
    ]
