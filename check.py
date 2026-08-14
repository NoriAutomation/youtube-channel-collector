import csv
from collections import Counter

rows = list(csv.DictReader(open("result.csv", encoding="utf-8-sig")))
domains = Counter(r["email"].split("@")[1] for r in rows)

print(f"総件数: {len(rows)}")
print(f"ユニークメール: {len({r['email'] for r in rows})}")
print("\n--- ドメイン上位15 ---")
for d, c in domains.most_common(15):
    print(f"{c:4d}  {d}")

# 誤検出の疑いがある行を検出
suspicious = [r for r in rows if any(
    r["email"].lower().endswith(ext) for ext in (".png",".jpg",".gif",".jpeg",".webp")
) or len(r["email"]) > 60 or r["email"].count(".") > 4]
print(f"\n要確認: {len(suspicious)}件")
for r in suspicious[:10]:
    print("  ", r["email"])