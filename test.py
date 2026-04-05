from groq import Groq

api_key = "ADD Groq API KEY HERE"

client = Groq(api_key=api_key)

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", "content": "Say hello and tell me what you can do in 2 sentences."}
    ]
)

print(response.choices[0].message.content)