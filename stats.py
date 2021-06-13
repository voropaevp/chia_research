import json
import pandas as pd
import pathlib
import datetime
from collections import defaultdict
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import logging

if __name__ == '__main__':
    nltk.download('vader_lexicon')
    sia = SentimentIntensityAnalyzer()
    vid_dict = defaultdict(list)
    for snap in pathlib.Path(r'C:\Users\vorop\PycharmProjects\chia_research\data').iterdir():
        timestamp = datetime.datetime.strptime(snap.name, '%Y-%m-%d-%H-%M-%S.json')
        try:
            all_stats = json.load(snap.open('r'))
        except Exception as e:
            logging.error(e)
            continue
        for vid_id, vid_stat in all_stats.items():
            vid_dict['video_id'].append(vid_id)
            vid_dict['timestamp'].append(timestamp)
            for col in ['averageRating', 'viewCount', 'title', 'channelId', 'author', 'lengthSeconds']:
                vid_dict[col].append(vid_stat[col])
            for order in ['VIEW_COUNT', 'UPDATE_DATE', 'RATING', 'RELEVANCE']:
                vid_dict[f'order_{order}'].append(order in vid_stat['order'])
            for k, v in sia.polarity_scores(vid_stat['title']).items():
                vid_dict[f'title_sentiment_{k}'].append(v)
            for k, v in sia.polarity_scores(vid_stat['shortDescription']).items():
                vid_dict[f'short_description_sentiment_{k}'].append(v)
    z = pd.DataFrame.from_dict(vid_dict)
    pass
