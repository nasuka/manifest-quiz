#!/usr/bin/env python3
"""
Quiz generator using OpenRouter's Gemini 2.5 Pro to create quiz questions from manifesto MD files.
"""

import os
import csv
import json
import requests
from pathlib import Path
from typing import List, Dict, Any
import re
from dotenv import load_dotenv
load_dotenv()

class QuizGenerator:
    def __init__(self, openrouter_api_key: str):
        """Initialize the quiz generator with OpenRouter API key."""
        self.api_key = openrouter_api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "google/gemini-2.5-pro-preview"
    
    def _call_openrouter_api(self, messages: List[Dict[str, str]]) -> str:
        """Call OpenRouter API with the given messages."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/manifest-quiz",
            "X-Title": "Manifest Quiz Generator"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 4000
        }
        
        response = requests.post(self.base_url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def _extract_category_from_filename(self, filename: str) -> str:
        """Extract category name from filename."""
        # Remove file extension and number prefix
        category = re.sub(r'^\d+_', '', filename.replace('.md', ''))
        return category
    
    def _create_quiz_prompt(self, content: str, category: str) -> str:
        """Create a prompt for generating quiz questions."""
        return f"""
以下の日本語のマニフェスト文書を読んで、内容に基づいて4択クイズを5-8問作成してください。

文書内容:
{content}

要件:
1. 4択クイズの形式で出力してください
2. 各問題は文書の重要な内容を扱うこと
3. 選択肢は1つが正解、3つが不正解になるように作成
4. 正解番号は1-4の数字で指定
5. 各問題に簡潔な解説を付ける
6. カテゴリ名は「{category}」を使用

出力形式（CSVの行として）:
category,question,option1,option2,option3,option4,correct_answer,explanation

# サンプル出力
category,question,option1,option2,option3,option4,correct_answer,explanation
チームみらいのビジョン,チームみらいが掲げる理念は何ですか？,テクノロジーで誰も取り残さない日本をつくる,デジタル格差をなくして平等な社会をつくる,AIで人間の仕事を代替する未来をつくる,すべての人にスマートフォンを配布する,1,チームみらいの中心的な理念は「テクノロジーで誰も取り残さない日本をつくる」です。
ステップ１教育,チームみらいが提案する「すべての子どもに届ける」ものは？,タブレット端末,専属AI家庭教師,プログラミング教育,デジタル教材,2,「すべての子どもに専属AI家庭教師を届ける」ことが提案されています。
ステップ１科学技術,チームみらいが重視する研究者支援の基本方針は？,競争力の強化,効率性の追求,研究環境の包括的改善,成果主義の徹底,3,研究者が研究に専念できる包括的な環境改善を重視しています。


例:
{category},この政策の目標は何ですか？,デジタル化を進める,格差を解消する,経済成長を促進する,教育を改善する,1,この政策はデジタル化を通じて社会課題の解決を目指しています。

実際のクイズ問題を作成してください（ヘッダー行は不要）:
"""
    
    def generate_quiz_for_file(self, md_file_path: str, output_csv_path: str) -> None:
        """Generate quiz questions for a single MD file and save to CSV."""
        # Read the markdown file
        with open(md_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract category from filename
        filename = Path(md_file_path).name
        category = self._extract_category_from_filename(filename)
        
        # Create prompt and call API
        prompt = self._create_quiz_prompt(content, category)
        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = self._call_openrouter_api(messages)
            
            # Parse the response and save to CSV
            self._save_quiz_to_csv(response, output_csv_path)
            print(f"Generated quiz for {filename} -> {output_csv_path}")
            
        except Exception as e:
            print(f"Error generating quiz for {filename}: {e}")
    
    def _save_quiz_to_csv(self, response: str, output_path: str) -> None:
        """Save the quiz response to a CSV file."""
        lines = response.strip().split('\n')
        
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(['category', 'question', 'option1', 'option2', 'option3', 'option4', 'correct_answer', 'explanation'])
            
            # Write quiz data
            for line in lines:
                if line.strip() and ',' in line:
                    # Split by comma but be careful with commas in content
                    parts = []
                    current_part = ""
                    in_quotes = False
                    
                    for char in line:
                        if char == '"':
                            in_quotes = not in_quotes
                        elif char == ',' and not in_quotes:
                            parts.append(current_part.strip())
                            current_part = ""
                            continue
                        current_part += char
                    
                    if current_part:
                        parts.append(current_part.strip())
                    
                    if len(parts) >= 8:
                        writer.writerow(parts[:8])
    
    def generate_quizzes_for_all_md_files(self, data_dir: str, output_dir: str = None) -> None:
        """Generate quiz files for all MD files in the data directory."""
        data_path = Path(data_dir)
        output_path = Path(output_dir) if output_dir else Path.cwd()
        
        # Find all MD files
        md_files = list(data_path.glob("*.md"))
        
        # Filter out README and LICENSE files
        md_files = [f for f in md_files if f.name not in ['README.md', 'LICENSE']]
        
        print(f"Found {len(md_files)} MD files to process")
        
        for md_file in md_files:
            # Create output filename
            base_name = md_file.stem
            output_csv = output_path / f"quiz_{base_name}.csv"
            
            # Skip if CSV already exists and is recent
            if output_csv.exists():
                print(f"Quiz file already exists: {output_csv}")
                continue
            
            self.generate_quiz_for_file(str(md_file), str(output_csv))


def main():
    """Main function to run the quiz generator."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate quiz questions from manifesto MD files')
    parser.add_argument('--api-key', required=True, help='OpenRouter API key')
    parser.add_argument('--data-dir', default='data', help='Directory containing MD files')
    parser.add_argument('--output-dir', default='.', help='Output directory for CSV files')
    parser.add_argument('--file', help='Process specific MD file only')
    
    args = parser.parse_args()
    
    generator = QuizGenerator(args.api_key)
    
    if args.file:
        # Process single file
        output_name = f"quiz_{Path(args.file).stem}.csv"
        output_path = Path(args.output_dir) / output_name
        generator.generate_quiz_for_file(args.file, str(output_path))
    else:
        # Process all files
        generator.generate_quizzes_for_all_md_files(args.data_dir, args.output_dir)


if __name__ == "__main__":
    main()