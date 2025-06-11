import csv
from pathlib import path
from gps_app.models import GPSData

# Mapping for player renaming
PLAYER_NAME_MAPPING = {
    'Demo 1': 'ABDULKARIM KASSIM KISWANYA',
    'Demo 2': 'ZOGOYA RICHARD ZOGOYA',
    'Demo 3': 'MACHELA JULIUS MACHELA',
    'Demo 4': 'PHALES EMMANUEL MKUDE',
    'Demo 5': 'RAJABU SHOMVI  SAID',
    'Demo 6': 'JACKSON FLUGENCE MLOKOZI',
    'Demo 7': 'DAUD SAID ATHUMANI',
    'Demo 8':  'NULL1',
    'Demo 9': 'CARLOS WILLIUM CHASAMBI',
    'Demo 10': 'NULL2',
    'Demo 11': 'ADINANI RASHID ATHUMANI',
    'Demo 12': 'NOSHAD JOHN TIMAMU',
    'Demo 13': 'MOHAMMED ISMAIL SHILLA',
    'Demo 14': 'MUHARRAMI YAHYA STINYE',
    'Demo 15': 'SETEBE JUMA SETEBE',
    'Demo 16': 'ISMAIL OMAR ALLY',
    'Demo 17': 'ALOBOGAST CHARLES KYOBYA',
    'Demo 18': 'FEISAL OTHUMAN JUMA',
    'Demo 19': 'PIUS SEVERINE JOHN',
    'Demo 20': 'NUHU NICCO LUGALAMILA',
    'Demo 21': 'OMARY JUMA MDACHI',
    'Demo 22': 'ALLY HASSANI ALLY',
    'Demo 23': 'ASHRAFU SHABANI KIBEKU',
    'Demo 24': 'ABDALLA SALUM SIO',
    'Demo 25': 'NULL3',
    }


def upload_performance_data(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            if row['Period Name'] != 'Session':
                continue

            player_name = PLAYER_NAME_MAP.get(row['Player Name'], row['Player Name'])

            PerformanceData.objects.create(
                player_name=player_name,
                period_name=row['Period Name'],
                period_number=int(row['Period Number']),
                max_acceleration=float(row['Max Acceleration']),
                max_deceleration=float(row['Max Deceleration']),
                acceleration_efforts=int(row['Acceleration Efforts']),
                deceleration_efforts=int(row['Deceleration Efforts']),
                accel_decel_efforts=int(row['Accel + Decel Efforts']),
                accel_decel_efforts_per_minute=float(row['Accel + Decel Efforts Per Minute']),
                duration=row['Duration'],
                distance=float(row['Distance']),
                player_load=float(row['Player Load']),
                max_velocity=float(row['Max Velocity']),
                max_vel_percent_max=float(row['Max Vel (% Max)']),
                meterage_per_minute=float(row['Meterage Per Minute']),
                player_load_per_minute=float(row['Player Load Per Minute']),
                work_rest_ratio=float(row['Work/Rest Ratio']),
                max_heart_rate=int(row['Max Heart Rate']),
                avg_heart_rate=int(row['Avg Heart Rate']),
                max_hr_percent_max=float(row['Max HR (% Max)']),
                avg_hr_percent_max=float(row['Avg HR (% Max)']),
                hr_exertion=float(row['HR Exertion']),
                red_zone=float(row['Red Zone']),
                hr_band_1_duration=row['Heart Rate Band 1 Duration'],
                hr_band_2_duration=row['Heart Rate Band 2 Duration'],
                hr_band_3_duration=row['Heart Rate Band 3 Duration'],
                hr_band_4_duration=row['Heart Rate Band 4 Duration'],
                hr_band_5_duration=row['Heart Rate Band 5 Duration'],
                hr_band_6_duration=row['Heart Rate Band 6 Duration'],
                energy=float(row['Energy']),
                high_metabolic_load_distance=float(row['High Metabolic Load Distance']),
                standing_distance=float(row['Standing Distance']),
                walking_distance=float(row['Walking Distance']),
                jogging_distance=float(row['Jogging Distance']),
                running_distance=float(row['Running Distance']),
                hi_distance=float(row['HI Distance']),
                sprint_distance=float(row['Sprint Distance']),
                sprint_efforts=int(row['Sprint Efforts']),
                sprint_dist_per_min=float(row['Sprint Dist Per Min']),
                high_speed_distance=float(row['High Speed Distance']),
                high_speed_efforts=int(row['High Speed Efforts']),
                high_speed_distance_per_minute=float(row['High Speed Distance Per Minute']),
                impacts=int(row['Impacts']),
                athlete_tags=row.get('Athlete Tags', ''),
                activity_tags=row.get('Activity Tags', ''),
                game_tags=row.get('Game Tags', ''),
                athlete_participation_tags=row.get('Athlete Participation Tags', ''),
                period_tags=row.get('Period Tags', ''),
            )
