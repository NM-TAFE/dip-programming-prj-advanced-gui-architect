import cv2
import pytesseract
import multiprocessing
from multiprocessing import Pool
import re
import openai
import time
import ast
import os

# Set OpenAI API key
openai.api_key = 'YOUR_API_KEY_HERE'

# Specify project ID - optional
ocrroo_project_id = 'proj_QuVLGAnwfmfgut4JVVyDki97'

# Specify project headers
project_headers = {
    "Authorization" : "Bearer " + openai.api_key,
    # "OpenAI-Project" : ocrroo_project_id
}


# ChatGPT
# python multiprocessing program to extract only programming code from video using opencv and tesseract ocr with limited memory saving frames into text file

# Set up pytesseract path (if required)
# For example, on Windows:
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\user\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'


# Function to check if the text is likely to be programming code
def is_code(text):
    code_pattern = re.compile(r"""
        (\b(if|else|while|for|return|int|float|double|char|void|import|from|class|def|print|include|main)\b|  # common keywords
        [\{\}\[\]\(\)<>;:=]|  # common symbols
        \b\d+\b|  # numbers
        [\w]+\.\w+|  # object properties or functions
        [#]\w+|  # comments in some languages
        ['"][\s\S]*['"])  # strings
    """, re.VERBOSE)

    return bool(code_pattern.search(text))


# Function to process each frame
def process_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    text = pytesseract.image_to_string(binary)
    if any(is_code(line) for line in text.split('\n')):
        return frame
    else:
        return None


# Function to process frames in chunks
def process_chunk(frames):
    return [process_frame(frame) for frame in frames]


# Function to process video frames in chunks
def process_video(video_path, chunk_size=1000):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    pool = Pool(processes=multiprocessing.cpu_count())
    chunk_frames = []

    for start in range(0, frame_count, chunk_size):
        frames = []
        counter = 0
        for _ in range(chunk_size):
            ret, frame = cap.read()
            if not ret:
                break
            # Skip 50 frames to avoid memory leak error
            if counter % 50 == 0:
                frames.append(frame)
            counter += 1

        if frames:
            chunk_result = pool.apply_async(process_chunk, (frames,))
            chunk_frames.append(chunk_result)

    cap.release()
    pool.close()
    pool.join()

    frames_with_code = [frame for result in chunk_frames for frame in result.get() if frame is not None]
    return frames_with_code


def extract_code_from_frame(frame):
    """
    Extracts code from a given frame using Tesseract OCR.
    """
    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to preprocess the image
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Use Tesseract to extract text
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(binary, config=custom_config)

    # Filter out non-code lines
    code_lines = [line.strip() for line in text.split('\n') if is_code(line)]
    return '\n'.join(code_lines)

# Function to save frames containing code as images
def save_frames(frames, output_dir, output_file):
    unique_code = set()
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i, frame in enumerate(frames):
        cv2.imwrite(f"{output_dir}/frame_{i}.png", frame)
        # Extract code from the frame
        code = extract_code_from_frame(frame)
        if code not in unique_code:
            unique_code.add(code)

    # Write the unique extracted code to a text file
    with open(output_file, 'w') as f:
        for code in unique_code:
            f.write(code + '\n')

def is_valid_python_code(code_line):
    """
    Validate if a line of Python code is syntactically correct.
    """
    try:
        ast.parse(code_line)
        return True
    except SyntaxError:
        return False

def process_code_file(input_filename, output_filename):
    """
    Read a code file, trim off lines starting with '>>>', validate remaining lines,
    and write valid lines to an output file.
    """
    valid_lines = []

    with open(input_filename, 'r') as infile:
        for line in infile:
            trimmed_line = line.strip()
            # Skip lines that start with '>>>'
            if not trimmed_line.startswith('>>>'):
                # Check if the line is valid Python code
                if is_valid_python_code(trimmed_line):
                    valid_lines.append(trimmed_line)

    # Write valid lines to the output file
    with open(output_filename, 'w') as outfile:
        for valid_line in valid_lines:
            outfile.write(valid_line + '\n')


def remove_duplicate_lines(input_file, output_file):
    try:
        with open(input_file, 'r') as file:
            lines = file.readlines()

        # Remove duplicate lines while preserving the order
        seen = set()
        unique_lines = []
        for line in lines:
            if line not in seen:
                unique_lines.append(line)
                seen.add(line)

        # Write the unique lines to the output file
        with open(output_file, 'w') as file:
            file.writelines(unique_lines)

    except FileNotFoundError:
        print(f"The file {input_file} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

def process_text_file(input_file, output_file):
    with open(input_file, 'r') as file:
        text = file.read()

    retries = 5
    for _ in range(retries):
        try:
            prompt = f"Fix up the following programming code snippet, fix up any indentation errors, syntax errors, " \
                     f"and anything else that is incorrect: '{text}'"
            response = openai.ChatCompletion.create(
                headers=project_headers,
                model="gpt-3.5-turbo",
                messages=[
                    # {"role": "system",
                    #  "content": f"You are a coding assistant. You reply only in programming code "
                    #             "that is correct and formatted. Do NOT reply with any explanation, "
                    #             f"only code. If you are given something that is not programming code, "
                    #             "you must NOT include it in your response. If nothing is present, "
                    #             "simply return 'ERROR' and nothing else. Do NOT return leading or "
                    #             "trailing"
                    #             "backticks and do NOT return the language before the code snippet."},
                    {"role": "system",
                      "content": "You are a coding assistant. You reply only in programming code "
                                 "that is correct and formatted. Do NOT reply with any explanation, "
                                 "only code. If you are given something that is not programming code, "
                                 "you must NOT include it in your response. Do NOT return leading or "
                                 "trailing "
                                 "backticks and do NOT return the language before the code snippet."},
                    {"role": "user", "content": prompt}
                ]
            )

            processed_text = response.choices[0].message['content']
            with open(output_file, 'w') as f:
                f.write(processed_text)
            break
        except openai.error.APIConnectionError as e:
            print(f"APIConnectionError: {e}. Retrying...")
            time.sleep(5)

        except openai.error.OpenAIError as e:
            print(f"OpenAIError: {e}")
            break


# Main function
if __name__ == '__main__':
    import os

    video_path = 'oop(1).mp4'
    output_dir = 'frames_with_code'
    raw_code_file = 'extracted_code.txt'
    valid_code_file = 'valid_code.txt'
    clean_code_file = 'clean_code.txt'
    gpt_output_file = "gpt_output.txt"

    frames_with_code = process_video(video_path)

    save_frames(frames_with_code, output_dir, raw_code_file)

    process_code_file(raw_code_file, valid_code_file)

    remove_duplicate_lines(valid_code_file, clean_code_file)

    process_text_file(clean_code_file, gpt_output_file)

    print(f"Code-containing frames extraction complete. Check '{output_dir}' for the output images. Check '{gpt_output_file}' for the output file.")
