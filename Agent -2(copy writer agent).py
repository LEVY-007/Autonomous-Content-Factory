from groq import Groq

api_key = "ADD Groq API KEY HERE"

client = Groq(api_key=api_key)

# This is the fact-sheet from Agent 1
# In the real app this will be passed automatically
fact_sheet = """
PRODUCT NAME: ProductX v2.0
TARGET AUDIENCE: startup teams of 5-50 people
KEY FEATURES: AI-powered task prioritization | real-time collaboration | Slack and Jira integrations
VALUE PROPOSITION: Not mentioned
PRICING: $29/month per team
AVAILABILITY: April 1, 2026
AMBIGUOUS STATEMENTS: None found
"""

# Agent 2's instructions
agent2_instructions = """
You are a Creative Copywriter Agent. You receive a fact-sheet and produce 
three pieces of marketing content.

STRICT RULES:
- Only use facts from the fact-sheet. Never invent features, prices, or claims.
- Blog post: professional and trustworthy tone, around 500 words
- Social thread: punchy and engaging, exactly 5 posts numbered 1/ to 5/
- Email teaser: one paragraph, warm,compelling and marketing

Return in this exact format:
===BLOG===
[blog content here]
===SOCIAL===
[social thread here]
===EMAIL===
[email teaser here]
"""

# Call Groq with Agent 2's instructions
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": agent2_instructions},
        {"role": "user", "content": f"Create content using this fact-sheet:\n\n{fact_sheet}"}
    ]
)

output = response.choices[0].message.content
print("=== AGENT 2 OUTPUT ===")
print(output)