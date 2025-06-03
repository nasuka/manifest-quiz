import streamlit as st
import random
import pandas as pd
import os
from pathlib import Path
# ページ設定
st.set_page_config(
    page_title="チームみらいマニフェスト クイズ（2025年5月30日時点版）",
    page_icon="🚀",
    layout="centered"
)

# 分野マッピング（ステップを統合）
FIELD_MAPPING = {
    "教育": ["ステップ１教育", "ステップ２教育", "ステップ３教育"],
    "子育て": ["ステップ１子育て", "ステップ３子育て"],
    "行政改革": ["ステップ１行政改革", "ステップ２行政改革"],
    "産業": ["ステップ１産業", "ステップ３産業"],
    "科学技術": ["ステップ１科学技術", "ステップ３科学技術"],
    "医療": ["ステップ１医療", "ステップ２医療", "ステップ３医療"],
    "経済財政": ["ステップ２経済財政", "ステップ３経済財政"],
    "エネルギー": ["ステップ３エネルギー"],
    "デジタル民主主義": ["ステップ１デジタル民主主義"],
    "基本理念・政策": ["チームみらいのビジョン", "政策インデックス"],
    "ステップ概要": ["ステップ１", "ステップ２", "ステップ３"],
    "特別プラン・その他": ["100日プラン", "その他重要分野", "改善提案の反映方針"]
}

# クイズデータ
@st.cache_data
def load_quiz_data():
    """CSVファイルからクイズ問題データを読み込む"""
    try:
        csv_path = "quiz_all_combined.csv"
        
        # CSVファイルを読み込み
        df = pd.read_csv(csv_path)
        
        # データを辞書形式に変換
        quiz_data = {}
        for _, row in df.iterrows():
            category = row['category']
            if category not in quiz_data:
                quiz_data[category] = []
            
            question_dict = {
                "question": row['question'],
                "options": [row['option1'], row['option2'], row['option3'], row['option4']],
                "correct": int(row['correct_answer']) - 1,  # CSVでは1-4、内部では0-3
                "explanation": row['explanation']
            }
            quiz_data[category].append(question_dict)
        
        return quiz_data
    
    except Exception as e:
        st.error(f"クイズデータの読み込みに失敗しました: {e}")
        # フォールバック: 最小限のデータを返す
        return {
            "エラー": [{
                "question": "クイズデータの読み込みに失敗しました",
                "options": ["再読み込みしてください", "", "", ""],
                "correct": 0,
                "explanation": "CSVファイルを確認してください"
            }]
        }

def initialize_session_state():
    """セッション状態を初期化"""
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = []
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = []
    if 'quiz_completed' not in st.session_state:
        st.session_state.quiz_completed = False
    if 'selected_mode' not in st.session_state:
        st.session_state.selected_mode = None
    if 'selected_field' not in st.session_state:
        st.session_state.selected_field = None
    if 'answer_shown' not in st.session_state:
        st.session_state.answer_shown = False

def generate_quiz_questions(quiz_data, num_questions=10, selected_field=None):
    """クイズ問題を生成（全問題またはフィールド別）"""
    all_questions = []
    
    if selected_field and selected_field in FIELD_MAPPING:
        # 特定分野の問題のみ
        target_categories = FIELD_MAPPING[selected_field]
        for category in target_categories:
            if category in quiz_data:
                for q in quiz_data[category]:
                    q['category'] = category
                    all_questions.append(q)
    else:
        # 全問題からランダム
        for category, questions in quiz_data.items():
            for q in questions:
                q['category'] = category
                all_questions.append(q)
    
    # 問題数が足りない場合は全問題を使用
    if len(all_questions) <= num_questions:
        return random.shuffle(all_questions) or all_questions
    
    return random.sample(all_questions, num_questions)

def display_question(question_data, question_num, total_questions):
    """問題を表示"""
    st.subheader(f"問題 {question_num + 1} / {total_questions}")
    st.write(f"**カテゴリ**: {question_data['category']}")
    st.write("---")
    
    st.write(f"### {question_data['question']}")
    
    # 選択肢を表示
    user_answer = st.radio(
        "選択してください:",
        question_data['options'],
        key=f"q_{question_num}",
        disabled=st.session_state.answer_shown
    )
    
    # 答えが表示されている場合は正解と解説を表示
    if st.session_state.answer_shown:
        correct_answer = question_data['options'][question_data['correct']]
        is_correct = user_answer == correct_answer
        
        st.write("---")
        
        if is_correct:
            st.success(f"✅ 正解！ **{correct_answer}**")
        else:
            st.error(f"❌ 不正解")
            st.info(f"正解は: **{correct_answer}**")
        
        st.write(f"**解説**: {question_data['explanation']}")
    
    return user_answer

def calculate_category_scores(user_answers, quiz_questions):
    """カテゴリ別のスコアを計算"""
    category_scores = {}
    category_totals = {}
    
    for i, (answer, question) in enumerate(zip(user_answers, quiz_questions)):
        category = question['category']
        
        if category not in category_scores:
            category_scores[category] = 0
            category_totals[category] = 0
        
        category_totals[category] += 1
        if answer == question['options'][question['correct']]:
            category_scores[category] += 1
    
    # パーセンテージに変換
    category_percentages = {}
    for category in category_scores:
        category_percentages[category] = (category_scores[category] / category_totals[category]) * 100
    
    return category_percentages, category_scores, category_totals

def get_recommendation_message(category_percentages):
    """スコアに基づいておすすめメッセージを生成"""
    recommendations = []
    
    for category, percentage in category_percentages.items():
        if percentage < 50:
            if "教育" in category:
                recommendations.append("📚 教育政策についてもっと詳しく学んでみましょう。AIを活用した個別最適化教育に注目です！")
            elif "行政改革" in category:
                recommendations.append("🏛️ 行政改革について学習を深めませんか？デジタル化による効率的な行政サービスがポイントです。")
            elif "子育て" in category:
                recommendations.append("👶 子育て支援政策をもう一度チェックしてみましょう。デジタル母子パスポートなど革新的な取り組みがあります。")
            elif "医療" in category:
                recommendations.append("🏥 医療政策について復習してみてください。オンライン診療など新しい医療のあり方に注目です。")
            elif "ビジョン" in category:
                recommendations.append("🎯 チームみらいの基本的なビジョンをもう一度確認してみましょう。")
            elif "産業" in category:
                recommendations.append("🏭 産業政策について学んでみましょう。AIシフトやDX推進がキーワードです。")
            elif "科学技術" in category:
                recommendations.append("🔬 科学技術政策を復習してみてください。研究環境改善やディープテック投資に注目です。")
            else:
                recommendations.append(f"📖 {category}について復習してみることをお勧めします。")
    
    if not recommendations:
        recommendations.append("🎉 素晴らしい！全分野で高いスコアを獲得しました。チームみらいの政策をよく理解されています！")
    
    return recommendations

def main():
    initialize_session_state()
    quiz_data = load_quiz_data()
    
    # ヘッダー
    st.title("🚀 マニフェスト クイズ")
    st.markdown("---")
    
    if not st.session_state.quiz_started:
        # スタート画面
        st.write("### クイズについて")
        st.write("このクイズでは、チームみらいのマニフェストに記載された内容に関する問題が出題されます。")
        st.write("問題数と出題範囲を選択して、理解度をチェックしましょう！")
        
        # 出題モード選択
        st.write("### 📋 出題モード選択")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🎲 ランダム出題**")
            st.write("全分野からランダムに出題")
            if st.button("ランダム出題を選択", type="secondary"):
                st.session_state.selected_mode = "random"
        
        with col2:
            st.write("**📚 分野別出題**")
            st.write("特定の分野に絞って出題")
            if st.button("分野別出題を選択", type="secondary"):
                st.session_state.selected_mode = "field"
        
        # 分野別出題の場合の分野選択
        if st.session_state.selected_mode == "field":
            st.write("### 🎯 出題分野を選択")
            
            # 分野リストを2列で表示
            field_options = list(FIELD_MAPPING.keys())
            cols = st.columns(2)
            
            for i, field in enumerate(field_options):
                col = cols[i % 2]
                with col:
                    # 各分野の問題数を表示
                    question_count = sum(len(quiz_data.get(cat, [])) for cat in FIELD_MAPPING[field])
                    if st.button(f"{field} ({question_count}問)", use_container_width=True):
                        st.session_state.selected_field = field
                        st.rerun()
            
            if st.session_state.selected_field:
                st.write(f"**選択された分野**: {st.session_state.selected_field}")
                
                # 問題数選択
                question_count = sum(len(quiz_data.get(cat, [])) for cat in FIELD_MAPPING[st.session_state.selected_field])
                max_questions = min(question_count, 20)
                
                num_questions = st.selectbox(
                    "出題数を選択してください",
                    options=[5, 10, 15, max_questions] if max_questions > 15 else [5, 10, max_questions],
                    index=1 if max_questions > 10 else 0
                )
                
                if st.button("この設定でクイズを始める", type="primary"):
                    st.session_state.quiz_started = True
                    st.session_state.quiz_questions = generate_quiz_questions(quiz_data, num_questions, st.session_state.selected_field)
                    st.rerun()
        
        # ランダム出題の場合
        elif st.session_state.selected_mode == "random":
            st.write("### 🎲 ランダム出題設定")
            
            num_questions = st.selectbox(
                "出題数を選択してください",
                options=[10, 15, 20, 30],
                index=0
            )
            
            if st.button("ランダムクイズを始める", type="primary"):
                st.session_state.quiz_started = True
                st.session_state.quiz_questions = generate_quiz_questions(quiz_data, num_questions)
                st.rerun()
        
        # 利用可能な分野一覧を表示
        if st.session_state.selected_mode is None:
            st.write("### 📖 利用可能な分野")
            for field, categories in FIELD_MAPPING.items():
                question_count = sum(len(quiz_data.get(cat, [])) for cat in categories)
                st.write(f"• **{field}**: {question_count}問 ({', '.join(categories)})")
    
    elif not st.session_state.quiz_completed:
        # クイズ実行中
        current_q = st.session_state.current_question
        total_q = len(st.session_state.quiz_questions)
        
        if current_q < total_q:
            question_data = st.session_state.quiz_questions[current_q]
            user_answer = display_question(question_data, current_q, total_q)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                if not st.session_state.answer_shown:
                    # 回答確定ボタン
                    if st.button("回答を確定", type="primary", use_container_width=True):
                        st.session_state.answer_shown = True
                        st.rerun()
                else:
                    # 次の問題へボタン
                    next_button_text = "次の問題へ" if current_q < total_q - 1 else "結果を見る"
                    if st.button(next_button_text, type="primary", use_container_width=True):
                        # 回答を保存
                        st.session_state.user_answers.append(user_answer)
                        
                        # 正解チェック
                        if user_answer == question_data['options'][question_data['correct']]:
                            st.session_state.score += 1
                        
                        st.session_state.current_question += 1
                        st.session_state.answer_shown = False  # 次の問題用にリセット
                        
                        # 最後の問題の場合
                        if st.session_state.current_question >= total_q:
                            st.session_state.quiz_completed = True
                        
                        st.rerun()
        
    else:
        # 結果画面
        st.write("## 🎉 クイズ完了！")
        
        total_score = st.session_state.score
        total_questions = len(st.session_state.quiz_questions)
        percentage = (total_score / total_questions) * 100
        
        # 総合スコア表示
        st.metric("総合スコア", f"{total_score}/{total_questions} ({percentage:.1f}%)")
        
        # カテゴリ別スコア
        category_percentages, category_scores, category_totals = calculate_category_scores(
            st.session_state.user_answers, st.session_state.quiz_questions
        )
        
        st.write("### 📊 カテゴリ別スコア")
        for category, percentage in category_percentages.items():
            score = category_scores[category]
            total = category_totals[category]
            st.write(f"**{category}**: {score}/{total} ({percentage:.1f}%)")
        
        # おすすめメッセージ
        st.write("### 💡 おすすめの学習ポイント")
        recommendations = get_recommendation_message(category_percentages)
        for rec in recommendations:
            st.write(rec)
        
        # 詳細結果（オプション）
        with st.expander("📝 詳細な解答結果を見る"):
            for i, (question, user_answer) in enumerate(zip(st.session_state.quiz_questions, st.session_state.user_answers)):
                correct_answer = question['options'][question['correct']]
                is_correct = user_answer == correct_answer
                
                st.write(f"**問題 {i+1}**: {question['question']}")
                st.write(f"あなたの回答: {user_answer} {'✅' if is_correct else '❌'}")
                if not is_correct:
                    st.write(f"正解: {correct_answer}")
                st.write(f"解説: {question['explanation']}")
                st.write("---")
        
        # リセットボタン
        if st.button("もう一度挑戦する", type="secondary"):
            for key in ['quiz_started', 'current_question', 'score', 'quiz_questions', 'user_answers', 'quiz_completed', 'selected_mode', 'selected_field', 'answer_shown']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    # フッター
    st.markdown("---")
    st.write("🔗 [チームみらい公式サイト](https://team-mir.ai/)")
    st.write("📖 [マニフェスト詳細](https://policy.team-mir.ai/view/README.md)")

if __name__ == "__main__":
    main()