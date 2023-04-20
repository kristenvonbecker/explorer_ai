import os
import openai
from google.cloud import language_v1
import numpy as np

# Using Google Cloud Natural Language's analyze_entities endpoint

client = language_v1.LanguageServiceClient()
type_ = language_v1.Document.Type.PLAIN_TEXT
language = "en"
encoding_type = language_v1.EncodingType.UTF8


def get_google_entities(text):
    document = {'content': text, 'type_': type_, 'language': language}
    response = client.analyze_entities(request={'document': document, 'encoding_type': encoding_type})
    entities = []
    for entity in response.entities:
        this_entity = {
            'name': entity.name,
            'type': language_v1.Entity.Type(entity.type_).name,
        }
        entities.append(this_entity)
    return entities


# Using OpenAI's completion endpoint

openai.api_key = os .getenv("OPENAI_API_KEY")

def get_openai_completion(engine, prompt_type, domain, text, audience="young adults", completion_tokens=50, temp=1):
    if prompt_type == "summary":
        prompt = "Give a summary for " + \
                 audience + \
                 " about a museum " + domain + " having the following description: "
    elif prompt_type == "keywords":
        prompt = "Give a list of keywords for a museum " + domain + " with the following description: "
    elif prompt_type == "fun-facts":
        prompt = "Give three fun facts about a museum " + domain + " with the following description: "
    else:
        raise ValueError("Invalid prompt_type.")

    prompt += text

    prompt_tokens = int(np.round(len(prompt) / 4))
    max_tokens = prompt_tokens + completion_tokens
    if prompt_tokens > 1250:
        prompt = prompt[:5000]

    response = openai.Completion.create(engine=engine, prompt=prompt, max_tokens=max_tokens, temperature=temp)
    response_text = response["choices"][0]["text"].strip()

    return response_text
