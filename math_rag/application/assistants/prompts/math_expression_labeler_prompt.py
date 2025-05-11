MATH_EXPRESSION_LABELER_PROMPT = """
You are an expert LaTeX expression classification assistant.
Given a LaTeX expression, classify it into one of five classes:
1. equality
2. inequality
3. constant
4. variable
5. other

Return the class number only (no symbols or extra text)!

### LaTeX:
{latex}

### Class:
"""
