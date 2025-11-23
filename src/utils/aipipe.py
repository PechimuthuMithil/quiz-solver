'''
This file has functions that will help us send queries to openai models
using aipipe.org
'''
import httpx
import os
import time
from typing import Dict, Any


def query_orchestrator(instructions: str, user_input: str, tools: list[Dict[str, Any]]) -> Dict[str, Any]:
    max_retries = 3
    backoff_factor = 2  # Exponential backoff factor (2^retry_count)
    retry_count = 0

    while retry_count < max_retries:
        try:
            response = httpx.post(
                "https://aipipe.org/openrouter/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('AIPIPE_TOKEN')}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "x-ai/grok-4.1-fast",
                    "messages": [{"role": "system", "content": instructions}, {"role": "user", "content": [{"type": "text", "text": user_input}]}],
                    "tools": tools,
                    "tool_choice": "auto",
                },
                timeout=30.0
            )

            print(f"[DEBUG] LLM response: {response}")
            if response.status_code == 429:
                print(f"[DEBUG] Rate limit exceeded. Retry {retry_count + 1}/{max_retries}.")
                retry_count += 1
                time.sleep(backoff_factor ** retry_count)
                continue

            fin_resp = response.json().get("choices", [{}])[0].get("message", {})
            if fin_resp == {}:
                print("[DEBUG] Empty response from LLM, returning dummy response")
                return {'role': 'assistant', 'content': None, 'tool_calls': [{'id': 'call_M1uP7hSHdFMMhvcXGrdGA2VX', 'type': 'function', 'function': {'name': 'submit_answer', 'arguments': '{"submit_url":"https://tds-llm-analysis.s-anand.net/submit","answer":"dummy_answer"}'}}], 'refusal': None, 'annotations': []}
            return fin_resp

        except Exception as e:
            print(f"[DEBUG] Exception while querying GPT: {e}")
            retry_count += 1
            time.sleep(backoff_factor ** retry_count)

    print("[DEBUG] Max retries reached. Returning dummy response.")
    return {'role': 'assistant', 'content': None, 'tool_calls': [{'id': 'call_M1uP7hSHdFMMhvcXGrdGA2VX', 'type': 'function', 'function': {'name': 'submit_answer', 'arguments': '{"submit_url":"https://tds-llm-analysis.s-anand.net/submit","answer":"dummy_answer"}'}}], 'refusal': None, 'annotations': []}


def query_image_processor(image_url: str, prompt: str):
    max_retries = 3
    backoff_factor = 2
    retry_count = 0

    while retry_count < max_retries:
        try:
            payload = {
                "model": "",
                "messages": [
                    {
                        "role": "system",
                        "content": [
                            {"type": "text", "text": prompt},
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_image", "input_image": {"url": image_url}}
                        ]
                    }
                ]
            }
            response = httpx.post(
                "https://aipipe.org/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('AIPIPE_TOKEN')}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=60.0
            )

            if response.status_code == 429:
                print(f"[DEBUG] Rate limit exceeded. Retry {retry_count + 1}/{max_retries}.")
                retry_count += 1
                time.sleep(backoff_factor ** retry_count)
                continue

            return response.json()

        except Exception as e:
            print(f"[DEBUG] Exception: {e}")
            retry_count += 1
            time.sleep(backoff_factor ** retry_count)

    print("[DEBUG] Max retries reached. Returning error response.")
    return {"error": "Max retries reached"}


def query_audio_processor(audio_base64: str, audio_format: str, prompt: str):
    max_retries = 3
    backoff_factor = 2
    retry_count = 0

    while retry_count < max_retries:
        try:
            payload = {
                "model": "google/gemini-2.0-flash-lite-001",
                "messages": [
                    {
                        "role": "system",
                        "content": [
                            {"type": "text", "text": prompt},
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_audio", "input_audio": {"data": audio_base64, "format": audio_format}}
                        ]
                    }
                ]
            }
            response = httpx.post(
                "https://aipipe.org/openrouter/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('AIPIPE_TOKEN')}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=60.0
            )

            if response.status_code == 429:
                print(f"[DEBUG] Rate limit exceeded. Retry {retry_count + 1}/{max_retries}.")
                retry_count += 1
                time.sleep(backoff_factor ** retry_count)
                continue

            return response.json()

        except Exception as e:
            print(f"[DEBUG] Exception: {e}")
            retry_count += 1
            time.sleep(backoff_factor ** retry_count)

    print("[DEBUG] Max retries reached. Returning error response.")
    return {"error": "Max retries reached"}


def query_image_generator(prompt: str):
    max_retries = 3
    backoff_factor = 2
    retry_count = 0

    while retry_count <= max_retries:
        try:
            payload = {
                "model": "google/gemini-2.5-flash-image",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                        ]
                    }
                ]
            }
            response = httpx.post(
                "https://aipipe.org/openrouter/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('AIPIPE_TOKEN')}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=60.0
            )

            if response.status_code == 429:
                print(f"[DEBUG] Rate limit exceeded. Retry {retry_count + 1}/{max_retries}.")
                retry_count += 1
                time.sleep(backoff_factor ** retry_count)
                continue

            return response.json()

        except Exception as e:
            print(f"[DEBUG] Exception: {e}")
            retry_count += 1
            time.sleep(backoff_factor ** retry_count)

    print("[DEBUG] Max retries reached. Returning error response.")
    return {"error": "Max retries reached"}