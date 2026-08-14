import os, re, csv, time, json
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()
youtube = build("youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY"))

EMAIL = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
SEEN_FILE = "seen.json"
OUT_FILE  = "result.csv"

# ---- 検索キーワード（1語につき100ユニット消費）----
KEYWORDS = [
    "お仕事のご依頼",
    "企業様 タイアップ",
    "案件 お問い合わせ",
    "PR案件 募集",
    "コラボ 依頼",
    "ビジネスのお問い合わせ",
]
PAGES_PER_KEYWORD = 3   # 1ページ50件 → 1キーワード最大150件

# ---- 取得済みチャンネルの記録（重複防止）----
seen = set()
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, encoding="utf-8") as f:
        seen = set(json.load(f))

quota = 0
new_ids = []

# ===== ① search でチャンネルIDを集める =====
for kw in KEYWORDS:
    token = None
    for _ in range(PAGES_PER_KEYWORD):
        try:
            res = youtube.search().list(
                q=kw, part="id", type="channel",
                maxResults=50, regionCode="JP",
                relevanceLanguage="ja", pageToken=token
            ).execute()
        except HttpError as e:
            print(f"[停止] {e}")
            token = None
            break

        quota += 100
        for item in res.get("items", []):
            cid = item["id"]["channelId"]
            if cid not in seen:
                seen.add(cid)
                new_ids.append(cid)

        token = res.get("nextPageToken")
        if not token:
            break
        time.sleep(0.2)

print(f"新規チャンネル: {len(new_ids)}件 / 消費: {quota}ユニット")

# ===== ② channels で概要欄を取ってメール抽出 =====
rows = []
for i in range(0, len(new_ids), 50):
    batch = new_ids[i:i+50]
    try:
        res = youtube.channels().list(
            part="snippet,statistics", id=",".join(batch), maxResults=50
        ).execute()
    except HttpError as e:
        print(f"[停止] {e}")
        break

    quota += 1
    for item in res.get("items", []):
        sn = item["snippet"]
        desc = sn.get("description", "")
        mails = EMAIL.findall(desc)
        if not mails:
            continue
        rows.append({
            "channel_name": sn["title"],
            "channel_url": f"https://www.youtube.com/channel/{item['id']}",
            "email": mails[0].lower(),
            "subscribers": item["statistics"].get("subscriberCount", ""),
        })
    time.sleep(0.2)

# ===== ③ メールアドレスで重複排除して保存 =====
existing = set()
write_header = not os.path.exists(OUT_FILE)
if not write_header:
    with open(OUT_FILE, encoding="utf-8-sig") as f:
        existing = {r["email"] for r in csv.DictReader(f)}

added = 0
with open(OUT_FILE, "a", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["channel_name","channel_url","email","subscribers"])
    if write_header:
        w.writeheader()
    for r in rows:
        if r["email"] in existing:
            continue
        existing.add(r["email"])
        w.writerow(r)
        added += 1

with open(SEEN_FILE, "w", encoding="utf-8") as f:
    json.dump(list(seen), f)

print(f"新規メール: {added}件 → {OUT_FILE}")
print(f"合計消費: {quota}ユニット（1日上限10,000）")