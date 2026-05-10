# import os
# from openai import OpenAI


# class Claude:

#     def __init__(self, model: str):

#         self.client = OpenAI(
#             api_key=os.getenv("GROQ_API_KEY"),
#             base_url="https://api.groq.com/openai/v1"
#         )

#         self.model = model

#     def add_user_message(self, messages: list, message):

#         messages.append({
#             "role": "user",
#             "content": str(message)
#         })

#     def add_assistant_message(self, messages: list, message):

#         messages.append({
#             "role": "assistant",
#             "content": str(message)
#         })

#     def text_from_message(self, message):

#         return str(message)

#     def chat(
#         self,
#         messages,
#         system=None,
#         temperature=1.0,
#         stop_sequences=[],
#         tools=None,
#         thinking=False,
#         thinking_budget=1024,
#     ):

#         formatted_messages = []

#         if system:
#             formatted_messages.append({
#                 "role": "system",
#                 "content": system
#             })

#         for msg in messages:

#             formatted_messages.append({
#                 "role": msg["role"],
#                 "content": str(msg["content"])
#             })

#         response = self.client.chat.completions.create(
#             model=self.model,
#             messages=formatted_messages,
#             temperature=temperature,
#         )

#         return response.choices[0].message.content

import os
from openai import OpenAI


class Claude:

    def __init__(self, model: str):

        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )

        self.model = model

    def add_user_message(self, messages: list, message):

        messages.append({
            "role": "user",
            "content": str(message)
        })

    def add_assistant_message(self, messages: list, message):

        messages.append({
            "role": "assistant",
            "content": str(message)
        })

    def text_from_message(self, message):

        return str(message)

    def chat(
        self,
        messages,
        system=None,
        temperature=1.0,
        stop_sequences=[],
        tools=None,
        thinking=False,
        thinking_budget=1024,
    ):

        formatted_messages = []

        if system:
            formatted_messages.append({
                "role": "system",
                "content": system
            })

        for msg in messages:

            role = msg["role"]
            content = str(msg["content"])

            formatted_messages.append({
                "role": role,
                "content": content
            })

        response = self.client.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            temperature=temperature,
        )

        return response.choices[0].message.content