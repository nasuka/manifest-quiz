#!/usr/bin/env python3
"""
Convenience script to generate all quiz files from MD files using OpenRouter Gemini 2.5 Pro.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# Add src to path to import our quiz generator
sys.path.append(str(Path(__file__).parent / "src"))

from manifest_quiz.quiz_generator import QuizGenerator


def main():
    """Generate quiz files for all MD files in the data directory."""
    # Get API key from environment or prompt user
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        api_key = input("Enter your OpenRouter API key: ").strip()
        if not api_key:
            print("API key is required. Set OPENROUTER_API_KEY environment variable or provide it when prompted.")
            sys.exit(1)
    
    # Initialize generator
    generator = QuizGenerator(api_key)
    
    # Generate quizzes for all MD files
    data_dir = "data"
    output_dir = "."
    
    print(f"Generating quiz files from MD files in {data_dir}/")
    print(f"Output directory: {output_dir}")
    print("=" * 50)
    
    try:
        generator.generate_quizzes_for_all_md_files(data_dir, output_dir)
        print("=" * 50)
        print("Quiz generation completed!")
    except Exception as e:
        print(f"Error during quiz generation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()