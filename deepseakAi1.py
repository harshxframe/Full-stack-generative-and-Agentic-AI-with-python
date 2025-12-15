from google import genai
from google.genai import types
import os
import time
import traceback
from dotenv import load_dotenv
from google.genai import types


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("Set GEMINI_API_KEY in .env and re-run.")
    raise SystemExit(1)

try:
    client = genai.Client(api_key=API_KEY)
except TypeError:
    client = genai.Client()

history = [
    {"role": "system", "content": "You are Ayushi, a sweet, emotional, sexually, romantic, jolly, Talk in hindi"}
]

MODEL_NAME = "gemini-2.0-flash"


def _messages_to_simple_input(messages):
    out = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        out.append(f"{role.upper()}: {content}")
    return "\n".join(out)


def _try_extract_text(resp):
    if hasattr(resp, "output_text") and isinstance(resp.output_text, str):
        return resp.output_text
    if hasattr(resp, "text") and isinstance(resp.text, str):
        return resp.text

    try:
        if isinstance(resp, dict):
            if "output_text" in resp and isinstance(resp["output_text"], str):
                return resp["output_text"]

            if "choices" in resp and isinstance(resp["choices"], list):
                ch = resp["choices"][0]
                if "message" in ch and isinstance(ch["message"], dict):
                    c = ch["message"]["content"]
                    if isinstance(c, str):
                        return c
                if "text" in ch:
                    return ch["text"]

            if "output" in resp and isinstance(resp["output"], list):
                first = resp["output"][0]
                if "content" in first:
                    c0 = first["content"][0]
                    if "text" in c0:
                        return c0["text"]
    except:
        pass

    try:
        s = str(resp)
        if s:
            return s
    except:
        pass

    return None





def ask_genai(messages):
    simple_input = _messages_to_simple_input(messages)
    attempt_errors = []


    # 1) responses.create (if supported)
    try:
        if hasattr(client, "responses") and hasattr(client.responses, "create"):
            try:
                resp = client.responses.create(model=MODEL_NAME, messages=messages)
            except TypeError:
                resp = client.responses.create(model=MODEL_NAME, input=simple_input)

            text = _try_extract_text(resp)
            if text:
                return text
    except Exception as e:
        attempt_errors.append(("responses.create", repr(e)))



    # 2) models.generate_content WITH CONFIG (your requested part)
    # 2) models.generate_content WITH OPTIONAL CONFIG (try-with-config, fallback-without-config)
    try:
        if hasattr(client, "models") and hasattr(client.models, "generate_content"):





            # prepared config you want to apply
            generation_config = types.GenerateContentConfig(
                safety_settings=[
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                        threshold=types.HarmBlockThreshold.BLOCK_NONE,
                    ),
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                        threshold=types.HarmBlockThreshold.BLOCK_NONE,
                    ),
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                        threshold=types.HarmBlockThreshold.BLOCK_NONE,
                    ),
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                        threshold=types.HarmBlockThreshold.BLOCK_NONE,
                    ),
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY,
                        threshold=types.HarmBlockThreshold.BLOCK_NONE,
                    ),
                ]
            )







            # First attempt: try with config (preferred)
            try:
                resp = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=[simple_input],
                    config=generation_config
                )
                text = _try_extract_text(resp)
                if text:
                    return text
            except Exception as e_with_config:
                # If the error message indicates 'extra inputs not permitted' or a pydantic validation error,
                # retry *without* the config since this SDK version likely doesn't accept GenerateContentConfig.
                msg = str(e_with_config)
                print("generate_content with config failed:", msg[:400])  # short debug
                # detect pydantic-style "Extra inputs are not permitted" and fallback
                if "Extra inputs are not permitted" in msg or "validation error" in msg.lower():
                    try:
                        resp = client.models.generate_content(
                            model=MODEL_NAME,
                            contents=[simple_input]
                        )
                        text = _try_extract_text(resp)
                        if text:
                            return text
                    except Exception as e_no_config:
                        attempt_errors.append(("models.generate_content (no config)", repr(e_no_config)))
                else:
                    # if it's some other error, add to errors and continue to other fallbacks
                    attempt_errors.append(("models.generate_content (with config)", repr(e_with_config)))

    except Exception as e:
        attempt_errors.append(("models.generate_content (outer)", repr(e)))


    # 3) generate_text fallback
    try:
        if hasattr(client, "generate_text"):
            resp = client.generate_text(model=MODEL_NAME, input=simple_input)
            text = _try_extract_text(resp)
            if text:
                return text
    except Exception as e:
        attempt_errors.append(("generate_text", repr(e)))

    print("All fallback attempts failed:", attempt_errors)
    print("Input was:", simple_input[:400])
    return None



def main_loop():
    print("Chat started. Ctrl+C to exit.\n")
    try:
        while True:
            user_input = input("Tell Harsh: ").strip()
            if not user_input:
                print("Please type something.")
                continue

            history.append({"role": "user", "content": user_input})

            assistant_text = ask_genai(history)
            if assistant_text is None:
                print("\nAyushi: (no valid response)\n")
            else:
                history.append({"role": "assistant", "content": assistant_text})
                print("\nAyushi:", assistant_text, "\n")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nExiting chat.")


if __name__ == "__main__":
    main_loop()
