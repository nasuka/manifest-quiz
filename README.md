# チームみらいマニフェスト クイズアプリ

このプロジェクトは、チームみらい（Team Mirai）の政治マニフェストをインタラクティブなクイズ形式で学習できるStreamlitアプリケーションです。

## 🌟 機能

- **ランダム出題**: 全分野からランダムに問題を出題
- **分野別出題**: 教育、医療、行政改革など特定分野に絞った出題
- **詳細な結果分析**: カテゴリ別スコアと学習推奨ポイントの表示
- **日本語完全対応**: チームみらいの日本語政策データを使用

## 🚀 クイック スタート

### 前提条件

- Python 3.12以上
- [Rye](https://rye-up.com/) パッケージマネージャー

### インストール

1. リポジトリをクローン:
```bash
git clone <repository-url>
cd manifest-quiz
```

2. 依存関係をインストール:
```bash
rye sync
```

3. アプリケーションを起動:
```bash
streamlit run src/manifest_quiz/app.py
```

アプリケーションが `http://localhost:8501` で起動します。

## 📊 対応分野

### 基本理念・政策
- チームみらいのビジョン
- 政策インデックス

### 3つのステップ
1. **ステップ１**: デジタル時代の当たり前をやりきる
2. **ステップ２**: 変化に対応できるしなやかな仕組みづくり  
3. **ステップ３**: 長期の成長に大胆に投資する

### 政策分野
- 📚 教育
- 👶 子育て
- 🏛️ 行政改革
- 🏭 産業
- 🔬 科学技術
- 🏥 医療
- 💰 経済財政
- ⚡ エネルギー
- 🗳️ デジタル民主主義

### 特別プラン
- 国政政党成立後100日プラン
- その他重要分野
- 改善提案の反映方針

## 📁 プロジェクト構成

```
manifest-quiz/
├── src/
│   └── manifest_quiz/
│       ├── __init__.py
│       └── app.py                 # メインアプリケーション
├── data/                          # マニフェストMarkdownファイル
│   ├── 01_チームみらいのビジョン.md
│   ├── 02_政策インデックス.md
│   ├── 10_ステップ１*.md
│   ├── 20_ステップ２*.md
│   ├── 30_ステップ３*.md
│   └── ...
├── quiz_*.csv                     # 分野別クイズデータ
├── quiz_all_combined.csv          # 統合クイズデータ
├── pyproject.toml                 # プロジェクト設定
├── CLAUDE.md                      # 開発ガイドライン
└── README.md
```

## 🔧 開発

### 開発コマンド

- **依存関係のインストール**: `rye sync`
- **アプリケーション実行**: `streamlit run src/manifest_quiz/app.py`
- **パッケージビルド**: `rye build`

### クイズデータの管理

クイズ問題は `quiz_all_combined.csv` で管理されています:

```csv
category,question,option1,option2,option3,option4,correct_answer,explanation
ステップ１教育,AIを活用した個別最適化教育について...,選択肢1,選択肢2,選択肢3,選択肢4,1,解説文...
```

#### クイズ問題の自動生成

OpenRouter Gemini 2.5 Proを使用して、マニフェストMDファイルから自動でクイズ問題を生成できます：

**前提条件:**
```bash
# OpenRouter API キーを環境変数に設定
export OPENROUTER_API_KEY="your_api_key_here"

# または .env ファイルに記載
echo "OPENROUTER_API_KEY=your_api_key_here" > .env
```

**全ファイルを一括生成:**
```bash
python generate_all_quizzes.py
```

**個別ファイルを処理:**
```bash
python -m manifest_quiz.quiz_generator --api-key YOUR_KEY --file data/01_チームみらいのビジョン.md
```

**生成したCSVファイルを統合:**
```bash
python combine_quizzes.py
```

**テスト実行:**
```bash
python test_quiz_generator.py
```

生成されたCSVファイルは自動的に既存の形式に合わせて作成され、日本語コンテンツから適切な4択クイズが生成されます。

新しい問題を手動で追加する場合は、上記のCSV形式に従ってデータを追加してください。

### 技術スタック

- **フレームワーク**: [Streamlit](https://streamlit.io/) - Webアプリケーション
- **パッケージマネージャー**: [Rye](https://rye-up.com/) - Python環境管理
- **データ処理**: [Pandas](https://pandas.pydata.org/) - CSV データハンドリング
- **ビルドシステム**: [Hatchling](https://hatch.pypa.io/) - パッケージビルド

## 📝 データについて

このプロジェクトで使用されているマニフェストデータは：

- 2025年5月30日時点版のチームみらい政策データ
- 教育、医療、行政改革、産業など幅広い政策分野をカバー
- idobata（井戸端）プラットフォームでの市民参加型議論をベースとした内容
- 日本の政治課題に対する革新的なデジタル技術活用アプローチ

## 🤝 貢献

プロジェクトへの貢献を歓迎します！

1. フォークしてください
2. フィーチャーブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトは適切なライセンスの下で配布されています。詳細は `LICENSE` ファイルを参照してください。

## 🔗 関連リンク

- [チームみらい公式サイト](https://team-mir.ai/)
- [マニフェスト詳細](https://policy.team-mir.ai/view/README.md)
- [idobata プラットフォーム](https://idobata.team-mir.ai/)

## 📧 連絡先

問題やご質問がございましたら、Issueを作成するか、プロジェクトメンテナーにお気軽にお問い合わせください。