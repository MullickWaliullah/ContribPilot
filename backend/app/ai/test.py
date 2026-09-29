from ranking import _build_prompt, _extract_json

issue: dict = {
    "title": "ContribPilot",
    "description": "AI MENTOR FOR CONTRIBUTION",
    "labels": "bugs",
    "language": "python"
}

user: dict = {
    "skills": "react, python",
    "experience": "beginner"
}

# print(_build_prompt(issue, user))

text = """
```json
{
    "match_score": "87.6",
    "complexity_level": "BEGINNER",
    "is_beginner_friendly": "true",
    "required_technologies": "Python",
    "matching_skills": ["Python", "GitHub", "FastAPI"],
    "missing_or_mismatched_skills": null,
    "reasoning": null
}
"""

print(_extract_json(text))