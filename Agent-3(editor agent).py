from groq import Groq

api_key = "ADD Groq API KEY HERE"

client = Groq(api_key=api_key)

# Fact-sheet from Agent 1
fact_sheet = """
PRODUCT NAME: ProductX v2.0
TARGET AUDIENCE: startup teams of 5-50 people
KEY FEATURES: AI-powered task prioritization | real-time collaboration | Slack and Jira integrations
VALUE PROPOSITION: Not mentioned
PRICING: $29/month per team
AVAILABILITY: April 1, 2026
AMBIGUOUS STATEMENTS: None found
"""

# Content from Agent 2
blog = """
As a startup team, you understand the importance of efficient collaboration and task management. 
With the ever-increasing demands of the modern workplace, it's easy to get bogged down in mundane 
tasks and lose sight of your goals. That's where ProductX v2.0 comes in – a cutting-edge solution 
designed specifically for startup teams like yours. With its AI-powered task prioritization, you'll 
be able to focus on the most critical tasks and make the most of your team's time.
"""

social = """
1/ Introducing ProductX v2.0, the ultimate solution for startup teams! With AI-powered task 
prioritization, real-time collaboration, and integrations with Slack and Jira, you'll be unstoppable.
2/ Tired of wasting time on mundane tasks? ProductX v2.0's AI-powered task prioritization helps 
you focus on what really matters.
3/ Collaboration just got a whole lot easier! ProductX v2.0's real-time collaboration feature lets 
your team work together seamlessly, no matter where they are.
4/ Good news for startup teams on a budget! ProductX v2.0 is priced at just $29/month per team.
5/ Mark your calendars! ProductX v2.0 will be available starting April 1, 2026.
"""

email = """
Get ready to revolutionize your team's productivity with ProductX v2.0! This cutting-edge solution 
is specifically designed for startup teams like yours, with AI-powered task prioritization, 
real-time collaboration, and seamless integrations with Slack and Jira. Priced at just $29/month 
per team, available starting April 1, 2026.
"""

# Agent 3's instructions
agent3_instructions = """
You are an Editor-in-Chief Agent. Your job is to review marketing content 
against the original fact-sheet and check for two things:

1. HALLUCINATIONS: Did the copywriter invent any features, prices, or claims 
   not present in the fact-sheet?
2. TONE ISSUES: Is the content too salesy, robotic, or off-brand?

Return your response in this exact format:
BLOG_STATUS: APPROVED or REJECTED
BLOG_NOTE: [reason if rejected, or Looks good]
SOCIAL_STATUS: APPROVED or REJECTED
SOCIAL_NOTE: [reason if rejected, or Looks good]
EMAIL_STATUS: APPROVED or REJECTED
EMAIL_NOTE: [reason if rejected, or Looks good]
"""

# Combine everything for Agent 3 to review
editor_input = f"""
FACT-SHEET:
{fact_sheet}

BLOG:
{blog}

SOCIAL:
{social}

EMAIL:
{email}
"""

# Call Groq with Agent 3's instructions
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": agent3_instructions},
        {"role": "user", "content": editor_input}
    ]
)

editor_output = response.choices[0].message.content
print("=== AGENT 3 OUTPUT ===")
print(editor_output)