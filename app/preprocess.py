import logging
import math
import openai
import requests
import pytesseract
import re
import cv2
import json
import utils
from socket_util import get_socketio


def query_llama(llama_endpoint, system_prompt, prompt, model="llama3", images=None):
    """
    Query the llama AI LLM
    :param llama_endpoint: The endpoint of the llama AI LLM
    :param system_prompt: The System prompt to use
    :param prompt: The prompt to use
    :param model: The AI model to use
    :param images: Images for AI model to use. By default, this is not needed as only the llava model supports it.
    :return: The AI's response
    """
    if images is None:
        images = []

    req = requests.post(llama_endpoint, json={
        'model': model,
        'messages': [
            {
                'role': 'system',
                'content': system_prompt
            },
            {
                'role': 'user',
                'content': prompt,
                'images': images
            }
        ],
        'stream': False
    })

    print(req)
    body = req.json()
    return body['message']['content']


def query_openai(irrelevant, system_prompt, prompt):
    """
    Query the OpenAI API
    :param irrelevant: This parameter is irrelevant as it is the llama endpoint
    :param system_prompt: The system prompt to provide to OpenAI
    :param prompt: The prompt to provide to OpenAI
    :return: The OpenAI response
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content']
    except openai.OpenAIError as error:
        logging.error(error)
        return None


def remove_unnecessary_chars(string):
    """
    Removes any unnecessary characters (characters that aren't valid to be used within actual code)
    :param string: The string you want to remove unnecessary characters from
    :return: The cleaned string
    """
    pattern = r'[^a-zA-Z0-9_\-+=<>/*&|%!@#$^(){}\[\];:,.\'\"`~\\ ]'
    return re.sub(pattern, '', string)
    # return string


def extract_text_from_frame(frame):
    """
    Extracts all text from frame, removes unnecessary characters and returns it
    :param frame: The frame to extract text from
    :return: Extracted Text
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    text = pytesseract.image_to_string(binary)
    code_lines = [remove_unnecessary_chars(line) for line in text.split('\n')]
    return '\n'.join(code_lines)


def clean_code_text(text):
    """
    Removes any lines from a text blob that are definitely not proper code (special thanks to ChatGPT for the regex)
    :param text: The text to clean
    :return: The cleaned text
    """
    patterns_to_remove = [
        r'^\s*$',  # Empty lines or lines with only whitespace
        r'^\s*\d+\s*$',  # Lines with only numbers
        r'^\s*PROBLEMS.*$',  # Lines starting with PROBLEMS
        r'^\s*Error.*$',  # Lines indicating errors
        r'^\s*Traceback.*$',  # Traceback lines
        r'^\s*File.*line\s*\d+',  # File path and line number often in error messages
        r'^\s*===.*$',  # Lines with only equals signs (often in logs or outputs)
        r'^\s*---.*$',  # Lines with only dashes (often in logs or outputs)
        r'^\s*==>.*$',  # Lines starting with ==> (often in logs or outputs)
        r'^\s*\*.*$',  # Lines starting with an asterisk
        r'^\s*\&.*$',  # Lines starting with ampersand
    ]

    combined_pattern = re.compile('|'.join(patterns_to_remove), re.IGNORECASE)
    cleaned_lines = [line for line in text.split('\n') if not combined_pattern.match(line)]
    return '\n'.join(cleaned_lines)


def extract_code(text):
    """
    Since the AI responds with backticks, extract the text from between the backticks
    :param text: The AI response
    :return: The extracted text or None
    """
    match = re.search(r"```(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        return None


def get_full_code(code_json):
    unique_lines = set()

    for item in code_json:
        code_lines = item["code"].splitlines()
        unique_lines.update(code_lines)

    return "\n".join(unique_lines) + "\n"


def scan_video_for_code_frames(filename, llama_endpoint, interval_seconds=5, programming_language="Python", provide_formatted_code=True, provide_code_explanations=True, llm="llama"):
    """
    Scans a video for frames containing code at approximately every interval_seconds.
    :param filename: The files name
    :param llama_endpoint: The endpoint of the llama AI LLM
    :param interval_seconds: Interval in seconds to capture frames
    :param programming_language: The programming language of the video
    :param provide_formatted_code: Whether the formatted code is included in the response
    :param provide_code_explanations: Whether the code explanation is included in the response
    :return: JSON object with timestamps and detected code.
    """
    is_code_prompt = (
        f"You are a helpful coding assistant. Your task is to determine if the given text contains valid {programming_language} code. "
        "If the text contains valid code, respond with true. Do not worry if the code is not functional, "
        "you just need to reply with true if it contains valid code. Otherwise, respond with false. Do not include "
        "anything other than true or false in your response."
    )

    format_code_prompt = (
        f"You have determined this text contains valid {programming_language} code. Your task is to extract the valid "
        f"code, correct any syntax errors, properly indent it, and respond only with the fixed code."
        "If no valid Python code can be extracted, respond with ERROR. Do not include anything other than the fixed "
        "code or ERROR in your response."
    )

    describe_code_prompt = (
        f"You are a helpful coding assistant. You will be given blocks of {programming_language} code and your "
        "job is to describe what they do to the best of your ability. Do NOT include a title. "
        "Only include a simple explanation. Your explanation is to be a maximum of ~20-30 words. "
        "Do NOT go over this limit. If you cannot provide an explanation, simply respond with Unknown. "
        "Do not reply with anything other than a simple explanation or Unknown."
    )

    provide_full_code_prompt = (
        f"You are a helpful coding assistant. The language you are working in is {programming_language}. "
        f"You will be given blocks of code and your job is to take those blocks of code and "
        f"properly format them, ensuring that there are no duplicate. This includes functions doing the same thing. "
        f"If 2 functions do the same thing, you must determine the most updated one and use that. You are NOT to add "
        f"new imports, or use things that were not already being used. You are also to remove unnecessary lines, "
        f"ensure that everything is correct syntactically and that there are proper indentations. You must then "
        f"return the corrected version. You must NOT return anything other than the corrected code, or ERROR if you "
        f"failed to correct it."
    )

    to_query = llm == "llama" and query_llama or query_openai
    video_path = f"{utils.get_vid_save_path()}\\{filename}"
    socketio = get_socketio()
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * interval_seconds)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frame_count = 0
    code_frames = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            print(f"Processing frame {frame_count}")
            socketio.emit("processingProgressUpdate", f"{math.floor((frame_count / total_frames) * 100)}%")
            text = extract_text_from_frame(frame)
            is_code = to_query(llama_endpoint, is_code_prompt, text)
            if is_code and is_code.strip().lower() == 'true':
                formatted_code, code_explanation = None, None
                timestamp = frame_count / fps
                print(f"Code detected at timestamp: {timestamp}")

                if provide_formatted_code:
                    formatted_code = extract_code(to_query(llama_endpoint, format_code_prompt, text))

                    if not formatted_code:
                        print(f"Could not extract code from frame {frame_count}")
                        frame_count += 1
                        continue

                if provide_code_explanations:
                    code_explanation = to_query(llama_endpoint, describe_code_prompt, text)
                    print(f"Code from frame {frame_count} explanation: {code_explanation}")

                code_frames.append({"seconds": timestamp, "code": formatted_code, "explanation": code_explanation})
                socketio.emit("timestampsUpdate", code_frames)

        frame_count += 1

    full_code = None

    if len(code_frames) >= 1 and provide_formatted_code:
        formatted = to_query(llama_endpoint, provide_full_code_prompt, get_full_code(code_frames))
        full_code = extract_code(formatted)

    socketio.emit("finishedProcessing", full_code)
    cap.release()
    cv2.destroyAllWindows()
    return json.dumps(code_frames, indent=4)
