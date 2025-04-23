from abc import ABC, abstractmethod
import os
import demjson3
from openai import OpenAI

#from prompts.flashcards_prompt import get_flashcards_system_prompt

class AIManager(ABC):
    @abstractmethod
    def get_ai_res(self, system_prompt, user_prompt, output_format_type):
        pass

    @abstractmethod
    def get_ai_res_hist(self, system_prompt, history, output_format_type):
        pass

    @abstractmethod
    def get_request_cost(self, response):
        pass

    @abstractmethod
    def get_input_prompt_cost(self, text):
        pass


def get_dict_from_text(text):
    start_index = text.find("{")
    end_index = text.rfind("}")
    dictionary = demjson3.decode(text[start_index:end_index+1])
    return dictionary


class OpenAIManager(AIManager):
    def __init__(self, client):
        self.client = client

    def get_ai_res(self, system_prompt: str, user_prompt: str, output_format_type="JSON"):
        response = self.client.responses.create(
            model=self.model_name,
            input=[
                {
                    "role": "developer",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )
        print(response)
        request_cost = self.get_request_cost(response)
        if output_format_type == "JSON":
            return get_dict_from_text(response.output_text), request_cost
        return response.output_text, request_cost
    
    def get_ai_res_hist(self, system_prompt, history, output_format_type):
        pass

    def get_request_cost(self, response):
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        cached_tokens = response.usage.input_tokens_details.cached_tokens
        return input_tokens * self.input_token_cost + \
            output_tokens * self.output_token_cost + \
            cached_tokens * self.cached_token_cost
    
    def get_input_prompt_cost(self, text):
        pass


class GPT41Nano(OpenAIManager):
    def __init__(self, client):
        self.model_name = "gpt-4.1-nano"
        self.input_token_cost = 0.100 / 1000000 # $0.100 / 1M tokens
        self.output_token_cost = 0.025 / 1000000 # $0.025 / 1M tokens
        self.cached_token_cost = 0.400 / 1000000 # $0.400 / 1M tokens
        super().__init__(client)


class AIFactory:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def get_ai(self, model=None):
        if model == "gpt-4.1-nano":
            return GPT41Nano(self.openai_client)
        return GPT41Nano(self.openai_client)


if __name__ == "__main__":
    from openai import OpenAI
    from dotenv import load_dotenv
    load_dotenv()
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    gpt = OpenAIManager(openai_client)
    response = gpt.get_ai_res(get_flashcards_system_prompt(), """
Developer quickstart
Take your first steps with the OpenAI API.
The OpenAI API provides a simple interface to state-of-the-art AI models for text generation, natural language processing, computer vision, and more. This example generates text output from a prompt, as you might using ChatGPT.

Generate text from a model
from openai import OpenAI
client = OpenAI()

response = client.responses.create(
    model="gpt-4.1",
    input="Write a one-sentence bedtime story about a unicorn."
)

print(response.output_text)
Data retention for model responses
Configure your development environment
Install and configure an official OpenAI SDK to run the code above.

Responses starter app
Start building with the Responses API

Text generation and prompting
Learn more about prompting, message roles, and building conversational apps.



Analyze image inputs
You can provide image inputs to the model as well. Scan receipts, analyze screenshots, or find objects in the real world with computer vision.

Analyze the content of an image
from openai import OpenAI
client = OpenAI()

response = client.responses.create(
    model="gpt-4.1",
    input=[
        {"role": "user", "content": "what teams are playing in this image?"},
        {
            "role": "user",
            "content": [
                {
                    "type": "input_image",
                    "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/3b/LeBron_James_Layup_%28Cleveland_vs_Brooklyn_2018%29.jpg"
                }
            ]
        }
    ]
)

print(response.output_text)
Computer vision guide
Learn to use image inputs to the model and extract meaning from images.



Extend the model with tools
Give the model access to new data and capabilities using tools. You can either call your own custom code, or use one of OpenAI's powerful built-in tools. This example uses web search to give the model access to the latest information on the Internet.

Get information for the response from the Internet
from openai import OpenAI
client = OpenAI()

response = client.responses.create(
    model="gpt-4.1",
    tools=[{"type": "web_search_preview"}],
    input="What was a positive news story from today?"
)

print(response.output_text)
Use built-in tools
Learn about powerful built-in tools like web search and file search.

Function calling guide
Learn to enable the model to call your own custom code.



Deliver blazing fast AI experiences
Using either the new Realtime API or server-sent streaming events, you can build high performance, low-latency experiences for your users.

Stream server-sent events from the API
from openai import OpenAI
client = OpenAI()

stream = client.responses.create(
    model="gpt-4.1",
    input=[
        {
            "role": "user",
            "content": "Say 'double bubble bath' ten times fast.",
        },
    ],
    stream=True,
)

for event in stream:
    print(event)
Use streaming events
Use server-sent events to stream model responses to users fast.

Get started with the Realtime API
Use WebRTC or WebSockets for super fast speech-to-speech AI apps.



Build agents
Use the OpenAI platform to build agents capable of taking action—like controlling computers—on behalf of your users. Use the Agent SDK for Python to create orchestration logic on the backend.

from agents import Agent, Runner
import asyncio

spanish_agent = Agent(
    name="Spanish agent",
    instructions="You only speak Spanish.",
)

english_agent = Agent(
    name="English agent",
    instructions="You only speak English",
)

triage_agent = Agent(
    name="Triage agent",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[spanish_agent, english_agent],
)


async def main():
    result = await Runner.run(triage_agent, input="Hola, ¿cómo estás?")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())

# ¡Hola! Estoy bien, gracias por preguntar. ¿Y tú, cómo estás?
Build agents that can take action
Learn how to use the OpenAI platform to build powerful, capable AI agents.



Explore further
We've barely scratched the surface of what's possible with the OpenAI platform. Here are some resources you might want to explore next.

Go deeper with prompting and text generation
Learn more about prompting, message roles, and building conversational apps like chat bots.

Analyze the content of images
Learn to use image inputs to the model and extract meaning from images.

Generate structured JSON data from the model
Generate JSON data from the model that conforms to a JSON schema you specify.

Call custom code to help generate a response
Empower the model to invoke your own custom code to help generate a response. Do this to give the model access to data or systems it wouldn't be able to access otherwise.

Search the web or use your own data in responses
Try out powerful built-in tools to extend the capabilities of the models. Search the web or your own data for up-to-date information the model can use to generate responses.

Responses starter app
Start building with the Responses API

Build agents
Explore interfaces to build powerful AI agents that can take action on behalf of users. Control a computer to take action on behalf of a user, or orchestrate multi-agent flows with the Agents SDK.

Full API Reference
View the full API reference for the OpenAI platform.
""")
    import json
    print(json.dumps(response, indent=3))