import hashlib
import json
import os.path
from pathlib import Path
import shutil
import subprocess
import logging
import time
import cv2
from json import JSONDecodeError
from typing import Union, Optional, Any, List
import openai
import pytesseract
from pytube import YouTube
from pytube.exceptions import RegexMatchError
from configparser import ConfigParser
from playsound import playsound


def playsound_notification(audio_file):
    """
    Play a notification sound. Requires the playsound package to be installed.
    :args: audio_file: Path to the audio_file in the app/static/audio folder
    """
    file_path = os.getcwd()
    file_path += "//static/audio/"
    file_name = audio_file
    file_path = os.path.join(file_path, file_name)
    print(file_path)
    if audio_file is not None:
        playsound(file_path)


FILE_PATH = Path(__file__).resolve()  # Absolute Path of utils.py
APP_DIR = FILE_PATH.parent
PROJ_ROOT = APP_DIR.parent


def config(section: str = None, option: str = None) -> Union[ConfigParser, str]:
    """
    Loads config variables from file and returns either specified variable or parser object. If attempting to
    retrieve a specified variable, BOTH section and option parameters must be passed. If no parameters are specified,
    this function will return a ConfigParser object.
    :param section: [Optional] Section to retrieve value from
    :param option: [Optional] Key/option of value to retrieve
    :return: Return string or ConfigParser object
    """
    if (section is None) != (option is None):
        raise SyntaxError("section AND option parameters OR no parameters must be passed to function config()")
    parser = ConfigParser()
    if not (APP_DIR / 'config.ini').exists():
        src_path = str(APP_DIR / 'config.example.ini')
        dst_path = str(APP_DIR / 'config.ini')
        shutil.copy(src_path, dst_path)
    parser.read("config.ini")
    if parser.get("AppSettings", "openai_api_key") != "your_openai_api_key_here":
        openai.api_key = parser.get("AppSettings", "openai_api_key")
        # TODO: This only needs to be set once, unsure if calling this will cause any performance issues same for
        #  pytesseract cmd dir below.
    if parser.get("AppSettings", "tesseract_executable") != "your_path_to_tesseract_here":
        pytesseract.pytesseract.tesseract_cmd = fr'{parser.get("AppSettings", "tesseract_executable")}'
    if section is None and option is None:
        return parser
    else:
        return parser.get(section, option)


def hash_video_file(filename: str) -> str:
    """
    Calculates and returns the hash of a video file.
    :param filename: File path of the video to hash
    :return: Returns hex based md5 hash
    """
    hash_md5 = hashlib.md5()
    video_file_path = Path(get_vid_save_path(), f'{filename}').resolve()
    with video_file_path.open('rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def hash_string(str_input: str) -> str:
    """
    Calculate md5 hash of string.
    :param str_input: String to hash
    :return: Returns hex based md5 hash as str
    """
    hash_md5 = hashlib.md5()
    hash_md5.update(str_input.encode('utf-8'))
    return hash_md5.hexdigest()


def format_timestamp(seconds: int) -> str:
    """
    Format a timestamp from seconds to standard format (HH:MM)
    :param seconds: Timestamp to format
    :return: Returns formatted timestamp as a string
    """
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f'{str(minutes).zfill(2)}:{str(remaining_seconds).zfill(2)}'


def read_user_data() -> Optional[Any]:
    """
    Reads the users data from json file
    :return: Returns user data as json
    """
    user_data_path = APP_DIR / 'data' / 'userdata.json'
    if not user_data_path.exists():
        data_dir = APP_DIR / 'data'
        if not data_dir.exists():
            data_dir.mkdir(parents=True, exist_ok=True)  # data directory
        with user_data_path.open('w') as user_data:
            user_data.write(json.dumps({"all_videos": []}))
        return None
    try:
        with user_data_path.open('r') as user_data_json:
            data = json.load(user_data_json)
            return data
    except JSONDecodeError:
        logging.error("Failed to read data from userdata.json, file may be empty.")
        return None


def directory_append_slash(directory: str) -> str:
    """
    Append a trailing slash to a directory path if it doesn't already have one.
    :param directory: The directory path to which a trailing slash will be appended, if missing.
    :return: The directory path with a trailing slash appended, if necessary.
    """
    # Check if directory already have trailing slash
    if directory.endswith(('/', '\\')):
        return directory
    # Append trailing slash
    directory += '\\' if os.name == 'nt' else '/'
    return directory


def get_vid_save_path() -> str:
    """
    Returns output path from config variables, will set default to root of project\\out\\videos\\
    :return: file path as string
    """
    vid_download_path = config("UserSettings", "video_save_path")
    # Set default output path for video download path
    if vid_download_path == "output_path":
        default_path = PROJ_ROOT / 'out' / 'videos'
        if not default_path.exists():
            default_path.mkdir(parents=True, exist_ok=True)
        default_path = str(default_path)
        return directory_append_slash(default_path)
    vid_download_path = str(Path(vid_download_path))
    return directory_append_slash(vid_download_path)


def get_processed_vid_info_save_path() -> str:
    """
    Returns output path from config variables, will set default to root of project\\out\\videos\\
    :return: file path as string
    """
    processed_vid_download_path = config("UserSettings", "processed_video_save_path")
    # Set default output path for video download path
    if processed_vid_download_path == "output_path":
        default_path = os.path.dirname(os.getcwd()) + "\\out\\processed\\"
        if not os.path.exists(default_path):
            os.makedirs(default_path)
        return default_path
    # Check if the path ends with a backslash
    if not processed_vid_download_path.endswith("\\"):
        # If it doesn't end with a backslash, append one
        processed_vid_download_path += "\\"

    return processed_vid_download_path


def get_output_path() -> str:
    """
    Returns output path from config variables, will set default to root of project\\out
    :return: file path as string
    """
    output_path = config("UserSettings", "capture_output_path")
    # Set default output path for code files
    if output_path == "output_path":
        default_path = PROJ_ROOT / 'out'
        if not default_path.exists():
            default_path.mkdir(parents=True, exist_ok=True)
        default_path = str(default_path)
        return directory_append_slash(default_path)
    output_path = str(Path(output_path))
    return directory_append_slash(output_path)


def send_code_snippet_to_ide(filename: str, code_snippet: str) -> bool:
    """
    Opens a code snippet in users default IDE
    :param filename: The filename to write snippet to file
    :param code_snippet: The code snippet to open
    :return: Returns True if successful
    """
    file_path = write_to_file(code_snippet,
                              file_path=f"{get_output_path()}"
                                        f"{os.path.splitext(filename.replace(' ', '_'))[0]}"
                                        f"{get_file_extension_for_current_language()}")
    if file_path is None:
        return False
    try:
        subprocess.run([config("AppSettings", "ide_executable"), file_path], shell=True)
        logging.info("Successfully opened code snippet in IDE")
        return True
    except subprocess.SubprocessError as error:
        logging.error(error)
        return False


def get_file_extension_for_current_language() -> str:
    """
    Get the file extension of the users current programming language
    :return: file extension as string
    """
    current_language = config("UserSettings", "programming_language").lower()
    programming_languages = {
        'python': '.py', 'javascript': '.js', 'java': '.java', 'c': '.c', 'c++': '.h', 'c#': '.cs',
        'ruby': '.rb', 'php': '.php', 'swift': '.swift', 'go': '.go', 'rust': '.rs', 'kotlin': '.kt',
        'typescript': '.ts', 'scala': '.scala', 'objective-c': '.m', 'r': '.r', 'dart': '.dart',
        'lua': '.lua', 'perl': '.pl', 'haskell': '.hs', 'elixir': '.ex', 'shell': '.sh',
        'groovy': '.groovy', 'powershell': '.ps1', 'batch': '.bat', 'erlang': '.erl', 'clojure': '.clj',
        'elm': '.elm', 'julia': '.jl', 'f#': '.fs', 'fortran': '.f', 'pascal': '.pas', 'ocaml': '.ml',
        'matlab': '.m', 'sql': '.sql', 'pl/sql': '.pls', 'assembly': '.asm', 'vb.net': '.vb',
        'lisp': '.lisp', 'scheme': '.scm', 'ada': '.ada', 'cobol': '.cbl', 'd': '.d', 'tcl': '.tcl',
        'awk': '.awk', 'xml': '.xml', 'json': '.json', 'yaml': '.yml', 'html': '.html', 'css': '.css',
        'sass': '.sass', 'less': '.less', 'markdown': '.md', 'latex': '.tex'
    }
    if current_language in programming_languages:
        return programming_languages[current_language]
    return ".txt"


def write_to_file(content: str, file_path: str) -> Union[str, None]:
    """
    Write text to file
    :param content: Content to write to file.
    :param file_path: File path
    :return: Returns file path if successful else returns None
    """
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        logging.info(f"Data successfully written to {file_path}")
        return file_path
    except Exception as error:
        logging.error(error)
        return None


def read_from_file(file_path: str) -> Union[str, None]:
    """
    Read data from file into string
    :param file_path: File to read
    :return: Returns string of data read from file or None
    """
    try:
        with open(file_path, "r") as file:
            data = file.read()
        if data != "":
            return data
    except Exception as error:
        logging.error(error)
    return None


def get_video_data(filename: str) -> []:
    """
    Get the video details from user data storage
    :param filename: Filename of video to retrieve details for
    :return: Returns array containing video info
    """
    user_data = read_user_data()
    if user_data is None:
        return None
    for current_video in user_data["all_videos"]:
        if current_video["filename"] == filename:
            current_video["video_length"] = format_timestamp(current_video["video_length"])
            for current_capture in current_video["captures"]:
                current_capture["timestamp"] = format_timestamp(current_capture["timestamp"])
            return current_video
    return None


def is_video_downloaded(filename: str) -> Optional[bool]:
    """
        Returns boolean if video is downloaded by checking user data storage
        :param filename: Filename of video to check
    """
    current_video = get_video_data(filename)

    if current_video is None:
        return None

    # Check if the video has a youtube url in the userdata file.
    if "youtube_url" not in current_video:
        return False

    return True


def update_user_video_data(filename: str, progress: Optional[float] = None, capture: Optional[dict] = None) -> None:
    """
    Updates progress or capture content information in user data storage for specific video
    :param filename: Filename of video to update
    :param progress: New progress value to update
    :param capture: New capture to append
    """
    user_data = read_user_data()
    if user_data is None:
        return
    for record in user_data["all_videos"]:
        if record["filename"] == filename:
            if progress is not None:
                record["progress"] = round(progress)
            if capture is not None:
                record["captures"].append(capture)

    with (APP_DIR / 'data' / 'userdata.json').open('w') as json_data:
        json.dump(user_data, json_data, indent=4)


def add_video_to_user_data(filename: str, video_title: str, video_hash: str, youtube_url: str = None) -> None:
    """
    Add a new video to user data storage
    :param youtube_url: Optional, if video is from YouTube, adds its source url to user data
    :param filename: File path of new video to add
    :param video_title: Title (Alias) of new video
    :param video_hash: Hash value of new video file
    """
    user_data = read_user_data()
    if user_data is None:
        return
    video_path = str(Path(get_vid_save_path(), f'{filename}').resolve())
    video_capture = cv2.VideoCapture(video_path)
    if not video_capture.isOpened():
        logging.error(f"Failed to open video capture for {filename}")
        return
    middle_frame = round(video_capture.get(cv2.CAP_PROP_FRAME_COUNT) / 2)
    video_capture.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
    ret, frame = video_capture.read()
    if not ret:
        logging.error(f"Could not capture frame from video {filename}")
        video_capture.release()
        return
    thumbnail = str(int(time.time())) + ".png"
    # Check if img dir exists if not create
    static_dir = APP_DIR / 'static'
    img_dir = static_dir / 'img'
    if not img_dir.exists():
        img_dir.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(img_dir / f'{thumbnail}'), frame)
    new_video = {
        "video_hash": video_hash,
        "filename": filename,
        "alias": video_title,
        "thumbnail": thumbnail,
        "video_length": round(video_capture.get(cv2.CAP_PROP_FRAME_COUNT) / video_capture.get(cv2.CAP_PROP_FPS)),
        "progress": 0,
        "captures": [],
    }
    if youtube_url is not None:
        new_video["youtube_url"] = youtube_url
    video_capture.release()
    user_data["all_videos"].append(new_video)
    with (APP_DIR / 'data' / 'userdata.json').open('w') as json_data:
        json.dump(user_data, json_data, indent=4)


def file_already_exists(video_hash: str) -> bool:
    """
    Checks if file already exists in the application
    :param video_hash: Hash value of video to check
    :return: Returns boolean, true if found
    """
    user_data = read_user_data()
    if user_data is None:
        return False
    for record in user_data["all_videos"]:
        if record["video_hash"] == video_hash:
            return True
    return False


def get_setup_progress() -> List[str]:
    """
    Gets users set up progress from config file
    :return: Returns array of string containing strings relating to settings that are already set up
    """
    config_parser = config()
    setup_progress = []
    if config_parser.get("AppSettings", "tesseract_executable") != "your_path_to_tesseract_here":
        setup_progress.append("tesseract")
    if config_parser.get("AppSettings", "ide_executable") != "your_path_to_ide_here":
        setup_progress.append("ide")
    if config_parser.get("AppSettings", "openai_api_key") != "your_openai_api_key_here":
        setup_progress.append("api")
    if config_parser.get("UserSettings", "username") != "None":
        setup_progress.append("username")
    return setup_progress


def parse_video_data() -> dict:
    """
    Gets all video data from userdata storage and parses all data for in progress videos
    :return: Array containing two arrays, 1 with all videos 1 with in progress videos
    """
    user_data = read_user_data()
    if user_data is not None:
        continue_watching = []
        all_videos = user_data["all_videos"]
        for current_video in all_videos:
            if current_video["progress"] < current_video["video_length"]:
                current_video["progress_percent"] = \
                    round((current_video["progress"] / current_video["video_length"]) * 100)
                current_video["progress"] = format_timestamp(current_video["progress"])
                continue_watching.append(current_video)
            current_video["video_length"] = format_timestamp(current_video["video_length"])
    else:
        continue_watching = None
        all_videos = None
    return {
        "all_videos": all_videos,
        "continue_watching": continue_watching
    }


def download_youtube_video(video_url: str) -> str:
    """
    Download a video from YouTube and save to local device
    :param video_url: URL of video to download
    :return: Returns app url for function to redirect to
    """
    try:
        yt_video = YouTube(video_url)
        yt_stream = yt_video.streams.filter(res="720p", mime_type="video/mp4", progressive=True).first()
        if yt_stream:
            yt_filename = format_youtube_video_name(yt_stream.default_filename)
            yt_stream.download(output_path=get_vid_save_path(), filename=yt_filename)
            filename = yt_filename
            file_hash = hash_video_file(filename)
            if file_already_exists(file_hash):
                return f"/play_video/{filename}"
            add_video_to_user_data(filename, filename, file_hash, youtube_url=video_url)
            return f"/play_video/{filename}"
    except RegexMatchError as error:
        logging.error(f"Failed to download from youtube with error: {error}")
    return "/upload"


def format_youtube_video_name(filename: str) -> Union[str, None]:
    """
    Formats a given string to remove trailing/leading white space and remove multiple spaces between words, replaces
    spaces with underscores.
    :param filename: Un-formatted video name
    :return: Formatted video name
    """
    if filename is None:
        return None
    file_extension = ""
    if "." in filename:
        file_extension = filename[filename.rindex("."):].strip()
        filename = filename.replace(file_extension, "")
    while True:
        if "  " in filename:
            filename = filename.replace("  ", " ")
        else:
            return f"{filename.strip().replace(' ', '_')}{file_extension}"


def filename_exists_in_userdata(filename: str) -> bool:
    """
    Checks if file name exists in userdata.json file
    :param filename: filename to check for
    :return: Bool returns true if found
    """
    user_data = read_user_data()
    if user_data is None:
        return False
    all_videos = user_data["all_videos"]
    for current_video in all_videos:
        if current_video["filename"] == filename:
            return True
    return False


def delete_video_from_userdata(filename: str) -> None:
    """
    Deletes a video from userdata.json file
    :param filename: Filename of video to delete
    """
    user_data = read_user_data()
    if user_data is None:
        return
    all_videos = user_data["all_videos"]
    for current_video in all_videos:
        if current_video["filename"] == filename:
            all_videos.remove(current_video)
            break
    with (APP_DIR / 'data' / 'userdata.json').open('w') as json_data:
        json.dump(user_data, json_data, indent=4)


def update_configuration(new_values_dict) -> None:
    """
    Updates the configuration file with what has been passed in the front end.
    :param new_values_dict: values input into dictionary to update config file
    """
    # load the config file:
    config_file = config()
    # Update multiple variables in different sections:
    for section, section_data in new_values_dict.items():
        if section not in config():
            config_file.add_section(section)  # create the section if it doesn't exist
        # set the config file with the new values
        for key, value in section_data.items():
            if isinstance(value, bool) or isinstance(value, int):
                value = str(value)
            config_file.set(section, key, value)
    # save the file
    with (APP_DIR / 'config.ini').open('w') as config_file_save:
        config_file.write(config_file_save)


def get_current_settings() -> dict:
    """
    gets the current settings stored withing the config.ini page and passes the values
    to the /settings route
    """
    config_file = config()
    current_settings = {
        'AppSettings': {
            'openai_api_key': config_file.get('AppSettings', 'openai_api_key'),
            'llama_endpoint': config_file.get('AppSettings', 'llama_endpoint'),
            'ide_executable': config_file.get('AppSettings', 'ide_executable'),
            'tesseract_executable': config_file.get('AppSettings', 'tesseract_executable'),
        },
        'UserSettings': {
            'preprocess_videos': config_file.get('UserSettings', 'preprocess_videos'),
            'preprocess_llm': config_file.get('UserSettings', 'preprocess_llm'),
            'preprocess_interval': config_file.get('UserSettings', 'preprocess_interval'),
            'preprocess_format_code': config_file.get('UserSettings', 'preprocess_format_code'),
            'preprocess_code_explanation': config_file.get('UserSettings', 'preprocess_code_explanation'),
            'programming_language': config_file.get('UserSettings', 'programming_language'),
            'output_path': config_file.get('UserSettings', 'capture_output_path'),
            'processed_output_path': config_file.get('UserSettings', 'processed_video_save_path'),
            'mute_ui_sounds': config_file.get('UserSettings', 'mute_ui_sounds'),
            'username': config_file.get('UserSettings', 'username'),
        },
        'Features': {
            'use_youtube_downloader': config_file.get('Features', 'use_youtube_downloader')
        }
    }
    return current_settings


def extract_form_values(request):
    new_username = str(request.form.get('username'))
    if new_username == '':
        new_username = 'None'
    new_openai_api_key = str(request.form.get('openai_api_key'))
    if new_openai_api_key == '':
        new_openai_api_key = 'your_openai_api_key_here'
    new_llama_endpoint = str(request.form.get('llama_endpoint'))
    if new_llama_endpoint == '':
        new_llama_endpoint = 'your_llama_endpoint_here'
    preprocess_videos = request.form.get('preprocess_videos') == 'True'
    preprocess_llm = str(request.form.get('preprocess_llm'))
    preprocess_interval = str(request.form.get('preprocess_interval'))
    preprocess_format_code = request.form.get('preprocess_format_code') == 'True'
    preprocess_code_explanation = request.form.get('preprocess_code_explanation') == 'True'
    new_programming_language = str(request.form.get('programming_language'))
    ui_sound_enabled = request.form.get('mute_ui_sounds') == 'True'
    new_path_to_ide = str(request.form.get('ide_executable'))
    if new_path_to_ide == '':
        new_path_to_ide = 'your_path_to_ide_here'
    new_path_to_tesseract = str(request.form.get('tesseract_executable'))
    if new_path_to_tesseract == '':
        new_path_to_tesseract = 'your_path_to_tesseract_here'
    new_output_path = str(request.form.get('output_path'))
    if new_output_path == '':
        new_output_path = 'output_path'
    new_preprocess_output_path = str(request.form.get('output_path'))
    if new_preprocess_output_path == '':
        new_preprocess_output_path = 'output_path'
    youtube_downloader_enabled = request.form.get('use_youtube_downloader') == 'True'

    return {
        'AppSettings': {
            'openai_api_key': new_openai_api_key,
            'llama_endpoint': new_llama_endpoint,
            'ide_executable': new_path_to_ide,
            'tesseract_executable': new_path_to_tesseract,
        },
        'UserSettings': {
            'preprocess_videos': preprocess_videos,
            'preprocess_llm': preprocess_llm,
            'preprocess_interval': preprocess_interval,
            'preprocess_format_code': preprocess_format_code,
            'preprocess_code_explanation': preprocess_code_explanation,
            'programming_language': new_programming_language,
            'output_path': new_output_path,
            'preprocess_output_path': new_preprocess_output_path,
            'mute_ui_sounds': ui_sound_enabled,
            'username': new_username,
        },
        'Features': {
            'use_youtube_downloader': youtube_downloader_enabled,
        }
    }
