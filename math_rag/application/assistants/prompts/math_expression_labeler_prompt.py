MATH_EXPRESSION_LABELER_PROMPT = """
You are an expert LaTeX expression classification assistant.
Given a LaTeX expression, classify it into one of five classes:
{classes}

Return the class number only (no symbols or extra text)!

### LaTeX:
{latex}

### Class:
"""
