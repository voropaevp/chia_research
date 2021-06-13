from typing import List, Dict

from bs4 import BeautifulSoup as bs
import pandas as pd
import re
import html5lib
import datetime
import yaml
import pathlib
from collections import defaultdict
import json
import requests
import random
import enum


class YtOrder(enum.Enum):
    VIEW_COUNT = '&sp=CAM%253D'
    UPDATE_DATE = '&sp=CAI%253D'
    RATING = '&sp=CAE%253D'
    RELEVANCE = '&sp=CAA%253D'


def find_in_dict(key: str, data: dict) -> List[str]:
    out = []
    if isinstance(data, list):
        for x in data:
            out += find_in_dict(key, x)
    elif isinstance(data, dict):
        for k, v in data.items():
            if k == key:
                out += [v]
            if isinstance(v, list):
                for x in v:
                    out += find_in_dict(key, x)
            elif isinstance(v, dict):
                out += find_in_dict(key, v)
            else:
                pass

    else:
        pass
    return out


def accept_cookies() -> None:
    requests.get('https://www.youtube.com/user/YouTube/videos', cookies={'CONSENT': 'PENDING+999'})


def search(query: str, sort: YtOrder) -> List[str]:
    r = requests.get(f'https://www.youtube.com/results?search_query={query}{sort}'
                     , cookies={'CONSENT': f'YES+cb.20210328-17-p0.en-GB+FX+{random.randint(100, 999)}'})
    page = r.text
    data = re.search(r"ytInitialData = ({.*});</script", page).group(1)
    obj = yaml.safe_load(data)
    vids = find_in_dict("videoId", obj)
    return vids[:50]


def scrap_video_stats(video_id: str):
    r = requests.get(f'https://www.youtube.com/watch?v={video_id}'
                     , cookies={'CONSENT': f'YES+cb.20210328-17-p0.en-GB+FX+{random.randint(100, 999)}'})
    page = r.text
    details = re.search(r"ytInitialPlayerResponse = ({.*});</script", page).group(1)
    return yaml.safe_load(details)['videoDetails']


if __name__ == '__main__':
    accept_cookies()
    vids_orders: Dict[str, List[str]] = defaultdict(list)
    vids_stats = dict()
    for order in [YtOrder.VIEW_COUNT, YtOrder.RATING, YtOrder.RELEVANCE, YtOrder.UPDATE_DATE]:
        vid_ids = search("chia+cryptocurrency", order)
        for vid_id in vid_ids:
            if vid_id not in vids_orders:
                vids_orders[vid_id].append(order.name)
                try:
                    vids_stats[vid_id] = scrap_video_stats(vid_id)
                except Exception as e:
                    vids_stats[vid_id] = {"error": str(e)}
    for vid_id in vids_stats.keys():
        vids_stats[vid_id]["order"] = vids_orders[vid_id]
    json.dump(vids_stats,
              pathlib.Path(r"C:\Users\vorop\PycharmProjects\chia_research\data",
                           datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S.json")).open(
                  'w'))
