# youtube-channel-collector
YouTube Data APIを用いたチャンネル情報の自動収集ツール

YouTube Data API v3 を用いて、指定したキーワードに該当するチャンネルの公開情報を収集し、CSV形式で出力するツールです。

## 機能

- キーワード指定によるチャンネルの自動探索
- チャンネル名 / URL / 登録者数 / 概要欄の公開情報を取得
- 正規表現による情報抽出
- 取得済みチャンネルの記録による重複取得の防止
- 出力データの重複排除
- Excel で文字化けしない形式（utf-8-sig）での CSV 出力

## 設計上の工夫

### APIクォータの最適化

YouTube Data API v3 は 1 日あたり 10,000 ユニットの無料枠があり、
`search.list` は 1 回 100 ユニット、`channels.list` は 1 ユニットを消費します。

`channels.list` は ID を 50 件までまとめて 1 リクエストに含められるため、
バッチ処理により消費量を 1/50 に圧縮しています。

加えて、取得済みチャンネル ID を `seen.json` に記録することで、
再実行時の重複取得を回避しています。

この設計により、無料枠の範囲内で 1 日あたり 1,000 件規模の収集が可能です。

### キーワード設計による取得率の改善

当初は一般的なジャンル名（例：「ビジネス 解説」）で検索していましたが、
概要欄に連絡先を記載しているチャンネルが使用する語句
（例：「お仕事のご依頼」「案件 お問い合わせ」）へ変更したところ、
目的の情報の取得率が約 7 倍に向上しました。

| キーワード設計 | 取得チャンネル数 | 抽出成功数 | 取得率 |
|---|---|---|---|
| ジャンル名ベース | 438 | 29 | 6.6% |
| 意図ベース | 789 | 372 | 47.1% |

## 構成

## 使い方

### 1. 必要なライブラリのインストール

bash
pip install google-api-python-client python-dotenv

### 2. APIキーの設定

Google Cloud Console で YouTube Data API v3 を有効化し、API キーを取得します。
プロジェクトルートに `.env` を作成し、以下を記載してください。

### 3. 実行

bash
python collect.py


`result.csv` が出力されます。

## 注意事項

本ツールで取得したデータの取り扱いは、
[YouTube API Services Terms of Service](https://developers.google.com/youtube/terms/api-services-terms-of-service) および
[Developer Policies](https://developers.google.com/youtube/terms/developer-policies) に従う必要があります。

特に以下の点にご留意ください。

- API Data の第三者への販売・再配布は禁止されています
- 認証を伴わない取得データの保存は 30 日以内に制限されています
- 複数のプロジェクトを作成してクォータ制限を回避する行為は禁止されています

## 動作環境

Python 3.9 以上 / Windows・macOS
