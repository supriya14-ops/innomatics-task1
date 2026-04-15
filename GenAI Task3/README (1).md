# GenAI_Task_3
AI Resume Screening System (GenAI Project)

Objective
This project builds an AI-powered Resume Screening System that evaluates candidates based on a job description.

Features
- Skill Extraction
- Resume vs Job Matching
- Scoring (0–100)
- Explainable Output
- Debug Case Handling

Approach
The system follows a pipeline:

Resume → Skill Extraction → Matching → Scoring → Explanation

Due to API quota limitations, a rule-based scoring fallback is implemented while maintaining the pipeline structure.

Test Cases
- Strong Candidate
- Average Candidate
- Weak Candidate
- Debug Case

Tech Stack
- Python
- LangChain
- Prompt Engineering

Output Example
Score: 75/100  
Explanation includes matched and missing skills.
