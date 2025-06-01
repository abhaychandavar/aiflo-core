import json
from time import sleep

import aiohttp
from app.nodes.interfaces.baseNodeService import Node
from app.nodes.types.nodeTypes import NodeServiceExecutionResultType
from typing import AsyncGenerator
from app.config.llms import Settings
import uuid

class GPT_3_5_Turbo(Node):
    def __init__(self, config):
        self.config = config
        self.__prev_delta_text = ""
        super().__init__()

    def content_part_started(self, id) -> NodeServiceExecutionResultType:
        return {
            "id": id,
            "dataType": "CONTENT_PART_START"
        }
    
    def content_part_ended(self, id) -> NodeServiceExecutionResultType:
        return {
            "id": id,
            "dataType": "CONTENT_PART_DONE"
        }

    def get_output_text_delta(self, id, data) -> NodeServiceExecutionResultType:
        delta = f"{self.__prev_delta_text} {data.get("delta")}"
        return {
            "id": id,
            "delta": delta,
            "dataType": "PARTIAL_OUTPUT"
        }

    def get_output_text_done(self, id, data) -> NodeServiceExecutionResultType:
        return {
            "id": id,
            "text": data.get("text"),
            "dataType": "PARTIAL_OUTPUT"
        }
    
    def extract_data_from_generated_response(self, id, response) -> NodeServiceExecutionResultType:
        output_texts = []
        outputs = response.get("output")
        for output in outputs:
            contents = output.get("content")
            for content in contents:
                if content.get("type") == "output_text":
                    output_texts.append(content.get("text"))
        return {
            "id": id,
            "dataType": "OUTPUT",
            "text": " ".join(output_texts)
        }
    
    def content_generation_done(self, id, data) -> NodeServiceExecutionResultType:
        response = data.get("response")
        output = self.extract_data_from_generated_response(id, response)
        return output

    def extract_data_from_gpt_response(self, id, data) -> NodeServiceExecutionResultType | None:
        response_extractor = {
            "response.output_text.delta": lambda: self.get_output_text_delta(id, data),
            "response.output_text.done": lambda: self.get_output_text_done(id, data),
            "response.content_part.added": lambda: self.content_part_started(id),
            "response.content_part.done": lambda: self.content_part_ended(id),
            "response.completed": lambda: self.content_generation_done(id, data),
        };
        extractor = response_extractor.get(data.get("type"))
        if extractor is None:
            return None

        return extractor()
    
    async def execute(self, input: str, stream_data = False) -> AsyncGenerator[NodeServiceExecutionResultType, None]:
        execution_id = str(uuid.uuid4())
        if stream_data:
            id = execution_id+"out-"
            idx = 1
            async for chunk in self.__make_streaming_query(input):
                extracted_data = self.extract_data_from_gpt_response(id+str(idx), chunk)
                if not extracted_data:
                    continue
                yield extracted_data
                idx += 1
            return;
    
        res = await self.__query(input)
        extracted_output = self.extract_data_from_generated_response(execution_id+'out-1', res)
        yield extracted_output
    
    async def __get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.config.get("apiKey") or Settings.GPT_API_KEY}"
        }

    async def __make_streaming_query(self, input: str):
        url = "https://api.openai.com/v1/responses"
        payload = {
            "model": "gpt-3.5-turbo-0125",
            "instructions": self.config.get("instructions") or 
                            "You are a helpful assistant, respond politely with appropriate response",
            "input": input,
            "stream": True
        }

        headers = await self.__get_headers()

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith("data:"):
                        data = line[5:].strip()
                        if data == "[DONE]":
                            break
                        try:
                            yield json.loads(data)
                        except json.JSONDecodeError:
                            continue

    async def __query(self, input: str):
        url = "https://api.openai.com/v1/responses"
        payload = {
            "model": "gpt-3.5-turbo-0125",
            "instructions": self.config.get("instructions") or 
                            "You are a helpful assistant, respond politely with appropriate response",
            "input": input,
            "stream": False
        }

        headers = await self.__get_headers()

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                data = await response.text()
                return json.loads(data)
