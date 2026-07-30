# トラストシステム 新卒採用サイト制作 作業レポート

**作成日：** 2026年4月  
**担当：** 梶田（ディレクション）× Claude（実装）  
**公開URL：** https://kajiyaan.github.io/trustsystem_recruit/

---

## 概要

1枚の採用HTMLから出発し、AIとの対話だけで本格的なマルチページ採用サイトを制作。  
デザイン・コーディング・GitHub Pagesへのデプロイまでを、専門的なプログラミング知識なしに完結させた事例。

**総制作時間（人間の実作業時間）：** 約2〜3時間  
**AIが代替した作業時間（推定）：** 40〜60時間相当

---

## フェーズ1｜情報収集・1枚物サイト制作（Claude使用前）

> この作業はClaude使用前に別セッションで完了済み。

| 時間 | 梶田さんの指示 | Claudeの作業 |
|------|--------------|-------------|
| 約5分 | 公式サイト・Wantedly・マイナビを理解して | 各サイトをフェッチ・解析し採用情報を整理 |
| 約10分 | GAテクノロジーズ風ダークテーマで作成 | 参考サイトを分析しHTML一式を生成 |
| 約5分 | サントリー採用サイト風に変更 | 白背景エディトリアルデザインで全面再制作 |
| 約3分 | やっぱりダークテーマに戻して | アップロードされたHTMLから復元 |
| 約25分 | ロゴ差込・バッジ追加・Wantedlyストーリー追加・福利厚生リニューアル等 | base64変換・セクション追加・コンテンツ整理 |
| 約15分 | PDF経由でまとめて修正指示 | プロジェクト事例・カルチャー・募集要項等を修正 |
| 約20分 | 細部修正・GitHub公開サポート | フォントサイズ調整・GitHub Pages設定案内 |

**フェーズ1 合計：約75分**  
**成果物：** `trustsystem_recruit.html`（1枚の完成HTML）

---

## フェーズ2｜マルチページ化・機能追加（本セッション）

> ここからが本レポートの主体。Claude（claude-sonnet-4-6）との対話で実施。

### 作業1｜1枚HTMLを13ページに分割

**課題：** 1枚のHTMLでは各ページにURLが付かず、採用サイトとして使いにくい。

**対応：**
- Pythonスクリプト `build.py` を作成
- HTMLコメントマーカー（`<!-- NAV -->`, `<!-- HERO -->` 等）を目印にセクションを自動抽出
- 13ページを自動生成するビルドシステムを構築

**生成されたページ：**

| ファイル | 内容 |
|---------|------|
| `index.html` | ヒーロー・数字・マーキー |
| `about.html` | 会社について・取引先・**会社概要・地図**（後から追加） |
| `business.html` | 事業内容・プロジェクト事例 |
| `culture.html` | カルチャー |
| `career.html` | キャリアパス |
| `welfare.html` | 福利厚生 |
| `stories.html` | Wantedly・SNS・X/Instagram |
| `recruit.html` | 募集要項 |
| `entry.html` | エントリー |
| `interview.html` | インタビュー一覧 |
| `interview_01.html` | H・Sさんインタビュー詳細 |
| `interview_02.html` | N・Tさんインタビュー詳細 |
| `interview_03.html` | M・Eさんインタビュー詳細 |

**ポイント：** `build.py` を実行するたびに全ページが再生成される。ソースHTMLを更新すれば一括反映できる構造。

> **※現在は廃止：** その後ライトテーマへの全面作り直し・会社概要追加・インタビューページ追加などを各HTMLに直接加えたため、`build.py` の入力元ソースHTMLとは大きく乖離した。現在は各HTMLファイル自体が原本で、共通パーツの同期は `sync.py` が担う（後述）。

---

### 作業2｜ナビリンクの修正

**課題：** 元HTMLのナビリンクがGitHub Pages用の絶対URLだったため、ページ遷移が壊れていた。

**対応：** `build.py` 内で正規表現を使って全リンクを相対パスに自動変換。

```python
# 例：絶対URLをページリンクに変換
nav_html = re.sub(r'href="https?://[^"]*#([a-z]+)"', replace_href, nav_html)
```

---

### 作業3｜社員インタビューページの新設

**課題：** Wantedlyに掲載中の3名のインタビューを採用サイトに統合したい。

**対応：**
- `interview.html`（カード一覧）と `interview_01〜03.html`（詳細ページ）を手書きで設計・実装
- 各ページ共通のデザイン言語（ダークテーマ・Bebas Neue・Cormorant Garamond）を統一
- 前後ナビゲーション（PREV / NEXT）付き

**インタビュー内容（3名）：**
1. **H・Sさん**（東京電機大学情報系・2019年入社・2024年リーダー昇格）
2. **N・Tさん**（新潟大学教育学部・文系出身・2019年入社・2024年リーダー昇格）
3. **M・Eさん**（中央大学理学部・IT未経験・2020年入社・2024年リーダー昇格）

---

### 作業4｜社員写真の差し替え

**課題：** 当初はWantedlyからダウンロードした写真を使用していたが、別途用意したWebP画像に差し替えたい。

**対応：** `img/interview_01〜03.webp` を追加し、全4ファイルのimgタグ参照を一括変更。

---

### 作業5｜ハンバーガーメニューの実装

**課題：** スマートフォン表示（768px以下）でナビが崩れ、「募集要項」が縦に折れて「Entry」ボタンが消えていた。

**対応：**
- `css/style.css` にハンバーガーボタン・ドロワーメニュー・オーバーレイのスタイルを追加
- `build.py` 内で全ページのナビにハンバーガーボタンとモバイルメニューHTMLを自動挿入
- インタビューページ4つにも同様のHTMLとJSを追加

**実装したUI：**
- 右上に「☰」ボタン表示（768px以下のみ）
- タップで右からスライドインするドロワーメニュー
- 背景にオーバーレイ（タップで閉じる）
- メニュー項目クリックで自動クローズ

---

### 作業6｜ファビコンの追加

**課題：** ブラウザタブにサイトアイコンが表示されていなかった。

**対応：** ユーザーが提供したXロゴ画像（`img/favicon.png`）を全ページの `<head>` に追加。

```html
<link rel="icon" type="image/png" href="img/favicon.png">
```

---

### 作業7｜プライバシーポリシーリンクの追加

**課題：** 採用サイトとして応募者への個人情報の取り扱い明示が必要。

**対応：** エントリーページのボタン下に同意文とリンクを追加。本社サイトの既存ページ（https://www.trustsystem.co.jp/privacypolicy）を活用。

---

### 作業8｜会社概要セクションの追加

**課題：** aboutページに会社の基本情報が不足していた。

**対応：** `about.html` に以下を追加：
- **会社概要テーブル**（商号・事業内容・設立・資本金・役員・所在地・電話番号）
- 役員の役職名と氏名を列で整列
- **Googleマップ埋め込み**（秋葉原UDX）

---

### 作業9｜GitHub Pagesへのデプロイ

**対応：**
```bash
cd trustsystem_recruit
git init
git remote add origin https://github.com/kajiyaan/trustsystem_recruit.git
git add .
git commit -m "Initial commit"
git push -u origin main
```

GitHubリポジトリの Settings → Pages → Source: main branch に設定するだけで自動公開。

---

## フェーズ3｜AIO（生成AI検索）対策・保守性の改善

生成AI検索（ChatGPT・Perplexity・Google AI Overviews等）に正しく認識・引用されるための土台を整備した。

### 作業10｜head メタ情報の整備

| 項目 | 対応 |
|------|------|
| meta description | 全13ページにページ固有の説明文を追加（従来は0件） |
| 構造化データ | schema.org の `Organization`（商号・住所・電話・設立・親会社・公式サイト）をJSON-LDで全ページに埋め込み |

### 作業11｜見出し構造の修正

about / business / culture / career / welfare / recruit / entry / stories の8ページが `<h1>` を持たず `<h2>` から始まっていたため、各ページのメインタイトルを `<h1>` に修正。クローラーがページ主題を判別できるようになった。

### 作業12｜OGP・Twitter Card の設定

SNSやチャット型AIでURLが共有された際に、タイトル・説明・画像が正しく表示されるよう全13ページに設定。

- `img/ogp.jpg`（1200×630・84KB）を新規作成。ヒーロー写真＋ロゴ＋「新卒採用 2027」をPillowで合成
- `og:title` / `og:description` / `og:image` / `og:url` / `twitter:card`（summary_large_image）等を付与
- あわせて `<link rel="canonical">` を全ページに追加（重複コンテンツ対策）

### 作業13｜募集要項の構造化データ（JobPosting）

`recruit.html` の募集要項を schema.org の `JobPosting` としてマークアップ。職種・初任給（233,000〜255,000円／月）・勤務地・応募資格・待遇を、AIや検索エンジンが求人情報として直接読み取れる形にした。

### 作業14｜sitemap.xml / robots.txt

- `sitemap.xml`：全13ページのURL・更新日・優先度を `sync.py` が自動生成
- `robots.txt`：GPTBot・OAI-SearchBot・ClaudeBot・PerplexityBot・Google-Extended を明示的に許可

> **注意：** GitHub Pages のプロジェクトページ（`kajiyaan.github.io/trustsystem_recruit/`）では、`robots.txt` はドメイン直下（`kajiyaan.github.io/robots.txt`）しか参照されないため、現URLでは効力を持たない。独自ドメインへ移行した時点で有効になる。`sitemap.xml` はSearch Console等へURLを直接送信すれば現状でも利用可能。

### 作業15｜AIO仕上げ・不要ファイルの整理

| 項目 | 内容 |
|------|------|
| 応募期限 | `JobPosting` に `validThrough`（2026-08-31）を追加。期限のない求人は求人検索から外れることがあるため |
| インタビュー記事 | 3ページに `Article` 構造化データを追加。公開日はgit履歴上の実際の公開日（01・02＝2026-04-19、03＝2026-05-01）を使用 |
| よくある質問 | `recruit.html` にFAQセクションを新設し `FAQPage` 構造化データを付与。Q&A形式はAI検索に引用されやすい。回答はすべてサイト内の既出情報にもとづく |
| 見出し階層 | h1→h3と飛んでいた5ページ（business/career/culture/stories/welfare）を修正。全13ページでスキップゼロに |
| 画像の軽量化 | ヒーロー画像をWebP化（1,399KB → 158KB、89%削減） |
| 不要ファイル削除 | 未参照の画像8点（旧ロゴ4点・旧インタビュー写真4点、計712KB）を削除。`img/` は3.1MB → 1.3MB |

### 作業16｜`build.py` の廃止と `sync.py` の新設

**課題：** `build.py` は入力元のソースHTMLが既に存在せず実行不能な状態だった。仮に動作しても、生成されるのは旧ダークテーマの9ページで、その後の改修内容（ライトテーマ・会社概要・インタビュー4ページ等）がすべて失われる状態だった。

**対応：** 各HTMLを原本と位置づけ、共通部分だけを上書きする `sync.py` に作り直した。

```bash
python sync.py
```

- 管理対象：`<title>` / `meta description` / OGP・Twitter Card / canonical / JSON-LD / `<nav>`（モバイルメニュー含む）/ `<footer>`、および `sitemap.xml`・`robots.txt` の生成
- ページ固有の本文・独自スタイルには一切触れない
- 冪等（同じ内容なら `unchanged` と表示して書き込まない）
- ページの追加は `PAGES` に1行足すだけ

**副次的に解消された不整合：**
- インタビュー4ページのフッターが `© 2025` のまま古かった（他ページは2026）
- フッターロゴのマークアップがページ間で不統一だった
- 未使用の旧ダークテーマ `css/style.css`（28KB）と、デザイン比較用の重複ページ `index_b.html` を削除

---

## ファイル構成

```
trustsystem_recruit/
├── sync.py               # 共通パーツ同期スクリプト（head/nav/footerを全ページに反映）
├── index.html
├── about.html
├── business.html
├── culture.html
├── career.html
├── welfare.html
├── stories.html
├── recruit.html
├── entry.html
├── interview.html
├── interview_01.html
├── interview_02.html
├── interview_03.html
├── css/
│   └── style_light.css   # 共通スタイルシート（ライトテーマ）
└── img/
    ├── logo_main.png      # ロゴ（ナビ・フッター共通）
    ├── img_1.jpeg         # ヒーロー背景
    ├── favicon.png        # ファビコン
    ├── interview_01.webp  # インタビュー写真
    ├── interview_02.webp
    └── interview_03.webp
```

---

## 使用技術・ツール

| カテゴリ | 内容 |
|---------|------|
| フロントエンド | HTML5 / CSS3（カスタムプロパティ・Grid・Flexbox・メディアクエリ） |
| JavaScript | バニラJS（IntersectionObserver・スクロールイベント・ハンバーガーメニュー） |
| フォント | Bebas Neue / Cormorant Garamond / Noto Sans JP（Google Fonts） |
| ビルド | Python 3（正規表現・ファイルI/O） |
| バージョン管理 | Git / GitHub |
| 公開 | GitHub Pages（無料・独自ドメイン設定も可能） |
| AI | Claude（claude-sonnet-4-6） |

---

## 同じサイトを作るには

1. **公式サイト・採用情報を集める**  
   Claudeに「このサイトを理解して」と伝えてURLを渡すだけで分析してくれる。

2. **デザインの方向性を伝える**  
   参考サイトのURLや「ダーク系・モダン・IT企業らしく」など言葉で指示。

3. **コンテンツを追加・修正していく**  
   「福利厚生にこの項目を追加して」「数字を290名に修正して」など自然な言葉で。

4. **マルチページ化を依頼する**  
   「各セクションを別ページに分けたい」と伝えるとbuild.pyのような仕組みを提案してくれる。

5. **GitHubにアップしてURLを取得**  
   操作方法もClaudeに「GitHub Pagesで公開する方法を教えて」と聞けばステップ案内してくれる。

---

## AIを使った効果

### 時間短縮

| 作業内容 | 従来（人間のみ） | Claude使用 |
|---------|--------------|----------|
| デザイン・HTML制作 | 2〜3日 | 約10分 |
| マルチページ化 | 半日〜1日 | 約15分 |
| インタビューページ制作（3名分） | 1日 | 約20分 |
| スマホ対応（ハンバーガーメニュー） | 2〜4時間 | 約10分 |
| 細部の修正・調整 | 都度1〜2時間 | 数分/件 |
| **合計** | **約1〜2週間** | **約3時間** |

### 専門知識なしで実現できたこと

- Pythonによるビルドスクリプト作成
- 正規表現を使ったURL一括変換
- CSS Grid / Flexboxによるレスポンシブデザイン
- Git / GitHub Pages によるデプロイ
- Google Mapsの埋め込み
- WebP画像・ファビコンの設定

### AIの特に有用だった点

1. **エラーの自律修正** — ナビリンクが壊れていたとき、原因を特定して修正コードまで提示
2. **意図の汲み取り** — 「前のデザインに戻して」など曖昧な指示でも的確に対応
3. **実際にブラウザで確認** — スクリーンショットを撮って表示崩れを自分で発見・修正
4. **複数ファイルの一括処理** — 「全ページに追加して」の一言で13ファイルを同時更新
5. **提案力** — 「どうすればいいか」を聞くと複数案を比較提示してくれる

---

## 今後の展望・残タスク

| 項目 | 優先度 | 備考 |
|------|--------|------|
| ~~各ページのmeta description追加~~ | — | **対応済み**（フェーズ3） |
| ~~OGP（SNSシェア用サムネイル）設定~~ | — | **対応済み**（フェーズ3） |
| ~~sitemap.xml / robots.txt~~ | — | **対応済み**（フェーズ3）※robots.txtは独自ドメイン移行後に有効化 |
| ~~JobPosting構造化データ~~ | — | **対応済み**（フェーズ3） |
| ~~FAQセクションの追加~~ | — | **対応済み**（作業15） |
| ~~ヒーロー画像のWebP変換~~ | — | **対応済み**（作業15・89%削減） |
| **Search Consoleへのsitemap送信** | **高** | **貴社側の作業。**Googleアカウントでの操作が必要なため未実施 |
| 応募期限の更新 | 都度 | `sync.py` の `JOB_POSTING['validThrough']` を書き換えて再実行 |
| 独自ドメインの設定 | 高（本番移行時） | CNAME設定が必要。robots.txtもこの時点で有効になる |
| インタビュー追加（4人目以降） | 随時 | interview_04.html作成後、`sync.py` のPAGESに追記 |

---

*このレポートはClaude（claude-sonnet-4-6）との対話作業を梶田が監修・整理したものです。*
