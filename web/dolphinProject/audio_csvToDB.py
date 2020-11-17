import csv
import os
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dolphinProject.settings")
django.setup()

from mainapp.models import MusicDB
from django.contrib.auth.models import User

CSV_PATH ="./train_plus_mood.csv"
# dolphinProject\audio_train_info.csv
#csv 파일 확정되면 경로 설정()

count = 0
with open(CSV_PATH, newline='', encoding='UTF8') as csvfile:
    data_reader = csv.DictReader(csvfile)
    for row in data_reader:
        
        MusicDB.objects.create(
            fname = row['fname'],
            label = row['label'],
            licenses = row['license'],
            # like = row[''],
            # date = row[''],
            downloads = 0,
            author = User.objects.get(username = 'admin'),
            real_author = row['freesound_id'],
            mood = row['mood'],
        )
        count += 1

        if count % 100 == 0:
            print(count)

print(count)
print('MusicDB update end')
