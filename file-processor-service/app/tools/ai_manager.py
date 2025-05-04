from abc import ABC, abstractmethod
import os
import demjson3
from openai import OpenAI


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