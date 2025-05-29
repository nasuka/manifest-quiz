import streamlit as st
import random
import pandas as pd
import os
from pathlib import Path

# ページ設定
st.set_page_config(
    page_title="マニフェスト クイズ",
    page_icon="🚀",
    layout="centered"
)

# クイズデータ
@st.cache_data
def load_quiz_data():
    """CSVファイルからクイズ問題データを読み込む"""
    try:
        csv_path = "quiz_questions.csv"
        
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

def generate_quiz_questions(quiz_data, num_questions=10):
    """ランダムにクイズ問題を生成"""
    all_questions = []
    for category, questions in quiz_data.items():
        for q in questions:
            q['category'] = category
            all_questions.append(q)
    
    # 問題数が足りない場合は全問題を使用
    if len(all_questions) <= num_questions:
        return all_questions
    
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
        key=f"q_{question_num}"
    )
    
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
            if category == "教育政策":
                recommendations.append("📚 教育政策についてもっと詳しく学んでみましょう。AIを活用した個別最適化教育に注目です！")
            elif category == "行政改革":
                recommendations.append("🏛️ 行政改革について学習を深めませんか？デジタル化による効率的な行政サービスがポイントです。")
            elif category == "子育て支援":
                recommendations.append("👶 子育て支援政策をもう一度チェックしてみましょう。デジタル母子パスポートなど革新的な取り組みがあります。")
            elif category == "医療政策":
                recommendations.append("🏥 医療政策について復習してみてください。オンライン診療など新しい医療のあり方に注目です。")
            elif category == "ビジョン・基本方針":
                recommendations.append("🎯 チームみらいの基本的なビジョンをもう一度確認してみましょう。")
    
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
        st.write("このクイズでは、マニフェストドキュメントに記載された内容に関する問題が出題されます。")
        st.write("全10問の選択式問題に答えて、理解度をチェックしましょう！")
        
        # st.write("### 出題カテゴリ")
        # for category in quiz_data.keys():
        #     st.write(f"• {category}")
        
        if st.button("クイズを始める", type="primary"):
            st.session_state.quiz_started = True
            st.session_state.quiz_questions = generate_quiz_questions(quiz_data, 10)
            st.rerun()
    
    elif not st.session_state.quiz_completed:
        # クイズ実行中
        current_q = st.session_state.current_question
        total_q = len(st.session_state.quiz_questions)
        
        if current_q < total_q:
            question_data = st.session_state.quiz_questions[current_q]
            user_answer = display_question(question_data, current_q, total_q)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                if st.button("次の問題へ", type="primary", use_container_width=True):
                    # 回答を保存
                    st.session_state.user_answers.append(user_answer)
                    
                    # 正解チェック
                    if user_answer == question_data['options'][question_data['correct']]:
                        st.session_state.score += 1
                    
                    st.session_state.current_question += 1
                    
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
            for key in ['quiz_started', 'current_question', 'score', 'quiz_questions', 'user_answers', 'quiz_completed']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    # フッター
    # st.markdown("---")
    # st.write("🔗 [チームみらい公式サイト](https://team-mir.ai/)")
    # st.write("📖 [マニフェスト詳細](https://policy.team-mir.ai/view/README.md)")

if __name__ == "__main__":
    main()