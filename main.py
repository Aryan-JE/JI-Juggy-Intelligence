from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5",
    input="Hello! Tell me you are working."
)

print(response.output_text)