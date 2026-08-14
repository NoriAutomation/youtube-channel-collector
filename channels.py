import os, re
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()
youtube = build("youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY"))

# test.py で取れたIDをそのまま貼る
channel_ids = [
    "UC32l5DPeQrMmaXs_-B3aayw",
    "UC5uVnrNuSPLSe-8-qXdv0fg",
    "UCPYYr92_Qzpb9XgTetcloyA",
    "UC17aYfyjlRsDxndrZcXIUnQ",
    "UCBj2Or5zTw_-xLtOO4-9KPA",
]

EMAIL = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

res = youtube.channels().list(
    part="snippet,statistics",
    id=",".join(channel_ids),   # 50件まで1回にまとめられる
    maxResults=50
).execute()

for item in res["items"]:
    title = item["snippet"]["title"]
    desc  = item["snippet"].get("description", "")
    subs  = item["statistics"].get("subscriberCount", "非公開")
    mails = EMAIL.findall(desc)
    print(f"{title} / 登録者{subs} / {mails if mails else 'なし'}")

print("\n消費クォータ: 1ユニット")