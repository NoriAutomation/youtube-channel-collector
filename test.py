import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()
key = os.getenv("YOUTUBE_API_KEY")
if not key:
    raise SystemExit(".env が読めていません。ファイル名と配置を確認してください")

youtube = build("youtube", "v3", developerKey=key)

res = youtube.search().list(
    q="ビジネス 解説",
    part="snippet",
    type="channel",
    maxResults=5,
    regionCode="JP",
    relevanceLanguage="ja"
).execute()

for i, item in enumerate(res["items"], 1):
    s = item["snippet"]
    print(f"{i}. {s['channelTitle']}  /  {s['channelId']}")

print("\n消費クォータ: 100ユニット（本日残り約9,900）")