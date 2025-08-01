from abc import ABC, abstractmethod
import os
import demjson3
from openai import OpenAI


class AIManager(ABC):
    @abstractmethod
    def get_ai_res(self, system_prompt, user_prompt, output_format_type):
        pass

    @abstractmethod
    def get_ai_res_hist(self, system_prompt, history):
        pass

    @abstractmethod
    def get_request_cost(self, response):
        pass

    @abstractmethod
    def get_input_prompt_cost(self, text):
        pass


def get_dict_from_text(text):
    text = text.replace("\n", "").replace("\t", "")
    start_index = text.find("{")
    end_index = text.rfind("}")
    dictionary = demjson3.decode(text[start_index:end_index+1])
    return dictionary


class OpenAIManager(AIManager):
    def __init__(self, client):
        self.client = client

    def get_ai_res(self, system_prompt: str, user_prompt: str, output_format_type="JSON"):
        for _ in range(2):
            try:
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
                print("Output text:", response.output_text)
                request_cost = self.get_request_cost(response)
                print("request_cost", request_cost)
                if output_format_type == "JSON":
                    data = get_dict_from_text(response.output_text), request_cost
                else:
                    data = response.output_text, request_cost
                return data
            except Exception as e:
                print("Error in ai manager:", str(e))

    def get_ai_res_hist(self, system_prompt, history):
        input = [
            {
                "role": "developer",
                "content": system_prompt
            },
            # {
            #     "role": "user",
            #     "content": user_prompt
            # }
        ] + history
        response = self.client.responses.create(
            model=self.model_name,
            input=input
        )
        return response.output_text

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