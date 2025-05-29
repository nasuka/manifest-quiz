# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Streamlit-based quiz application for チームみらい (Team Mirai) political manifesto. The project allows users to interact with political policy content through a quiz format.

## Development Commands

- **Install dependencies**: `rye sync` (uses Rye package manager)
- **Run application**: `streamlit run src/manifest_quiz/app.py`
- **Build package**: `rye build`

## Quiz Data Management

- Quiz questions are stored in `data/quiz_questions.csv`
- CSV format: category, question, option1-4, correct_answer (1-4), explanation
- To add new questions, edit the CSV file directly
- The app automatically loads and categorizes questions from CSV

## Project Structure

- `src/manifest_quiz/`: Main Python package
- `data/`: Contains Japanese political manifesto markdown files organized by policy steps and categories
  - Files are numbered and categorized (01_, 10_, 20_, 30_, 40_, 50_, 60_)
  - Content covers education, healthcare, administrative reform, industry, science & technology, etc.
  - Includes a comprehensive README.md with table of contents and contribution guidelines

## Architecture Notes

The project uses:
- **Rye** for Python package management and build system
- **Streamlit** as the web framework for the quiz interface
- **Hatchling** as the build backend
- Minimum Python version: 3.12

## Data Content

The manifesto data is in Japanese and covers:
- Vision and policy index
- Three main policy steps (デジタル時代, しなやかな仕組み, 長期の成長)
- 100-day plan for national party formation
- Various policy domains (education, childcare, administrative reform, industry, etc.)

The data is designed to be interactive and uses an "idobata" discussion platform for public engagement.