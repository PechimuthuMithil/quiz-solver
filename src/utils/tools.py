'''
This file holds functions to parse the quiz page.
The quiz page contains one task only.
Here are some types of questions you can expect:
- Scraping a website (which may require JavaScript) for information
- Sourcing from an API (with API-specific headers provided where required)
- Cleansing text / data / PDF / … you retrieved
- Processing the data (e.g. data transformation, transcription, vision)
- Analysing by filtering, sorting, aggregating, reshaping, or applying statistical / ML models. Includes geo-spatial / network analysis
- Visualizing by generating charts (as images or interactive), narratives, slides
'''
# [TODO] Might need to make some class out of these functions

from playwright.sync_api import sync_playwright
# from vosk import Model, KaldiRecognizer, SetLogLevel
from pydub import AudioSegment
import src.utils.aipipe as aipipe
import subprocess
import requests
import tempfile
# import mimetypes
import shutil
import base64
# import wave
# import json
# import venv
import sys
import os

def cleanup_memory():
# Clean up all files in memory directory
	memory_dir = "memory"
	for filename in os.listdir(memory_dir):
		file_path = os.path.join(memory_dir, filename)
		try:
			if os.path.isfile(file_path) or os.path.islink(file_path):
				os.unlink(file_path)
				print(f"[DEBUG] Deleted file: {file_path}")
			elif os.path.isdir(file_path):
				shutil.rmtree(file_path)
				print(f"[DEBUG] Deleted directory: {file_path}")
		except Exception as e:
			print(f"[ERROR] Failed to delete {file_path}. Reason: {e}")

def download_file_from_url(url):
# Download a file from the given URL and save it to the destination path (absolute)
# return error if any
	try:
		dest_path = os.path.join("memory", os.path.basename(url))
		if url.startswith("file://"):
			local_path = url[7:]  # Remove 'file://' prefix
			shutil.copy(local_path, dest_path)
			print("[DEBUG] File copied from local path to:", dest_path)
			return os.path.abspath(dest_path)
		with requests.get(url, stream=True) as resp:
			resp.raise_for_status()
			with open(dest_path, 'wb') as f:
				for chunk in resp.iter_content(chunk_size=8192): # Can adjust chunk size as needed
					f.write(chunk)
		print("[DEBUG] File downloaded to:", dest_path)
		#return absolute dest_path
		return os.path.abspath(dest_path)
	except Exception as e:
		print(f"[ERROR] Failed to download file from {url}: {e}")
		return (-1, e)

# def get_audio_files_transcribed(audio_urls):
# # Extract audio file URLs from the given HTML content.
# # Store the files in memory directory and return a list of file paths.
# 	trancribed_results = []
# 	for url in audio_urls:
# 		download_path = download_file_from_url(url)
# 		if isinstance(download_path, tuple) and download_path[0] == -1:
# 			# Error in downloading file
# 			return (-1, download_path[1])
# 		audio_file_name = os.path.basename(download_path).split('.')[0]
# 		audio = AudioSegment.from_file(download_path)
# 		# normalize to Vosk-friendly format
# 		audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)  # 2 bytes = 16-bit
		
# 		SetLogLevel(-1) # Suppress Vosk logging messages
# 		model_path = "models/vosk-model-en-us-0.22" 
# 		model = Model(model_path)
# 		wav_audio_file_path = os.path.join("memory", f"{audio_file_name}.wav")
# 		# Path to your audio file (must be WAV format, 16kHz, mono)
# 		audio.export(wav_audio_file_path, format="wav")
# 		print("[DEBUG] Converted audio exported to:", wav_audio_file_path)
# 		wf = wave.open(wav_audio_file_path, "rb")
# 		if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
# 			print("Audio file must be WAV format, 16kHz, mono, 16-bit PCM.")
# 			exit(1)

# 		recognizer = KaldiRecognizer(model, wf.getframerate())
# 		recognizer.SetWords(True) # Optional: get word-level timestamps

# 		while True:
# 			data = wf.readframes(4000) # Read audio in chunks
# 			if len(data) == 0:
# 				break
# 			recognizer.AcceptWaveform(data)

# 		trancribed_results.append(json.loads(recognizer.FinalResult()).get("text", ""))
# 	return trancribed_results
# print("Testing get_audio_files_transcribed function")
# test_urls = ["https://tds-llm-analysis.s-anand.net/demo-audio.opus",]
# transcriptions = get_audio_files_transcribed(test_urls)
# for i, transcription in enumerate(transcriptions):
# 	print(f"Transcription {i+1}: {transcription}")
		


def get_html_content(url):
# Fetch the HTML content of the given URL.
# Return the HTML as a string.
# I want to also unwrap any hype.rlinks to get full URLs.
# After reaging https://scrapfly.io/blog/posts/scraping-using-browsers,
# I feel using Playwright is a better option for this task.
	html = "" 
	with sync_playwright() as pw:
		browser = pw.chromium.launch(headless=True)
		print("[DEBUG] Browser launched")
		page = browser.new_page()
		print("[DEBUG] New page created")
		page.goto(url)
		print("[DEBUG] Navigated to URL:", url)
		 # Resolve all relative URLs to absolute URLs in the DOM
		page.evaluate("""
		() => {
			const resolveUrl = (base, relative) => new URL(relative, base).href;

			// Resolve all <a> href attributes
			document.querySelectorAll('a[href]').forEach(a => {
				a.setAttribute('href', resolveUrl(window.location.href, a.getAttribute('href')));
			});

			// Resolve all <audio> src attributes
			document.querySelectorAll('audio[src]').forEach(audio => {
				audio.setAttribute('src', resolveUrl(window.location.href, audio.getAttribute('src')));
			});

			// Resolve other elements with src attributes (e.g., <img>, <video>, etc.)
			document.querySelectorAll('[src]').forEach(el => {
				el.setAttribute('src', resolveUrl(window.location.href, el.getAttribute('src')));
			});
		}
		""")
		print("[DEBUG] Resolved relative URLs to absolute URLs")


		html = page.content()
		print("[DEBUG] HTML content retrieved")
		browser.close()
	return html
# print("Testing get_html_content function")
# test_url = "https://tds-llm-analysis.s-anand.net/demo-audio?email=21f3001995%40ds.study.iitm.ac.in&id=3727"
# html_content = get_html_content(test_url)
# print("HTML content length:", len(html_content))
# print(html_content)

def submit_answer(email, secret, task_url, submit_url, answer):
# Send a post request to the given submit_url with the following payload:
# {
#   "email": "your email",
#   "secret": "your secret",
#   "url": task_url,
#   "answer": answer
# }
	# task url can have query parameters etc, need to remove it
	task_url = task_url.split('?')[0]
	payload = {
		"email": email,
		"secret": secret,
		"url": task_url,
		"answer": answer
	}
	headers = {
		"Content-Type": "application/json"
	}
	response = requests.post(submit_url, json=payload, headers=headers)
	if response.status_code == 200:
		print("[DEBUG] Answer submitted successfully.")
		print("[DEBUG] Response:", response.json())
		# check if the answer was correct
		response_json = response.json()
		if response_json.get("correct", False):
			print("[DEBUG] The submitted answer is correct!")
		else:
			print("[DEBUG] The submitted answer is incorrect.")
			print("[DEBUG] Reason:", response_json.get("reason", ""))
	else:
		print("[DEBUG] Failed to submit answer. Status code:", response.status_code)
		print("Response:", response.text)
	return response_json.get("url", None)
	# [TODO] set some global variable if needed to indicate submission status
# print("Testing submit_answer function")
# email = "dummy"
# secret = "dummy"
# task_url = "https://tds-llm-analysis.s-anand.net/demo-audio"
# submit_url = "https://tds-llm-analysis.s-anand.net/submit"
# answer = 6969
# submit_answer(email, secret, task_url, submit_url, answer)

def execute_python_code(requirements, code):
    # temp dir to install packages
    pkg_dir = tempfile.mkdtemp()

    # 1. Install requirements using uv --target
    if requirements:
        subprocess.run(
            ["uv", "pip", "install", "--target", pkg_dir] + requirements,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    wrapped_code = f"""
import sys
import os

# Allow reading from any path, but restrict output to memory/output
_original_open = open
_output_dir = {repr(os.path.abspath('memory'))}

def restricted_open(file, mode='r', *args, **kwargs):
    file_path = os.path.abspath(file)
    
    # Allow reading from anywhere
    if 'r' in mode:
        return _original_open(file, mode, *args, **kwargs)
    
    # Restrict writing to output directory
    if 'w' in mode or 'a' in mode or '+' in mode:
        if not file_path.startswith(_output_dir):
            # Redirect to output directory
            file_name = os.path.basename(file)
            file_path = os.path.join(_output_dir, file_name)
            print(f"[WARNING] Files can be only written to {{_output_dir}} but got {{os.path.abspath(os.path.dirname(file))}}. File output redirected to: {{file_path}}", file=sys.stderr)
        return _original_open(file_path, mode, *args, **kwargs)
    
    return _original_open(file, mode, *args, **kwargs)

# Replace the built-in open function
import builtins
builtins.open = restricted_open

# User code starts here
{code}
"""
		
    # 2. Write temporary python file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp:
        tmp.write(wrapped_code.encode("utf-8"))
        tmp_path = tmp.name

    # 3. Execute code using system python with PYTHONPATH
    env = os.environ.copy()
    env["PYTHONPATH"] = pkg_dir

    proc = subprocess.Popen(
        ["python3", tmp_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )

    try:
        # Add a timeout to the process
        stdout, stderr = proc.communicate(timeout=30)  # Timeout set to 30 seconds
    except subprocess.TimeoutExpired:
        proc.kill()  # Kill the process if it exceeds the timeout
        stdout, stderr = proc.communicate()  # Retrieve any output after killing
        print("[ERROR] Code execution timed out (30s).", file=sys.stderr)

    # 4. Cleanup
    os.remove(tmp_path)
    shutil.rmtree(pkg_dir)

    return stdout, stderr
# print("Testing execute_python_code function")
# test_requirements = ["requests","numpy"]
# test_code = """with open('/home/test_output.txt', 'w') as f:\tf.write('This is a test output file.')"""
# stdout, stderr = execute_python_code(test_requirements, test_code)
# print("STDOUT:\n", stdout)
# print("STDERR:\n", stderr)

def get_image_as_base64_url(url):
	try:
		download_path = download_file_from_url(url)
		file_extension = os.path.basename(download_path).split('.')[-1].lower()
		if file_extension == "svg":
			file_extension = file_extension+"+xml"
		if isinstance(download_path, tuple) and download_path[0] == -1:
			# Error in downloading file
			return (-1, download_path[1])
		with open(download_path, "rb") as img_file:
			encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
		return f"data:image/{file_extension};base64,{encoded_string}"
	
	except Exception as e:
		print(f"[ERROR] Failed to encode image from {url} to base64: {e}")
		return (-1, e)
# print("Testing get_image_as_base64_url function")
# string = get_image_as_base64_url("file:///home/mithilpn/iitm/tds/p2/test/some_images2.svg")
# print("Base64 URL string length:", len(string))
# print(string)

def analyse_image_to_text(url, question): # [TODO] Fix!
	instructions = (
		"You are an expoert image analyst."
		"You are to thoroughly understand the image attached via the URL, and answer ONLY the following question below based on the image content:"
		f"{question}"
		"Strictly return ONLY the answer without any additional text."
	)
	if url.startswith("file://"):
		# local file, need to convert to base64 url
		base64_url = get_image_as_base64_url(url)
		if isinstance(base64_url, tuple) and base64_url[0] == -1:
			print(f"[ERROR] Failed to convert local image {url} to base64 URL: {base64_url[1]}")
			return ""
		url = base64_url
	response = aipipe.query_image_processor(url, instructions)
	return response
# print("Testing analyse_image_to_text function")
# test_url = "file:///home/mithilpn/iitm/tds/p2/test/00000.jpg"
# # test_url = "file:///home/mithilpn/iitm/tds/p2/test/some_images2.png"
# print("Test URL:", test_url)
# response = analyse_image_to_text(test_url, "What is this image?")
# print("Response:", response)

def convert_audio_to_16kHz_base64(url):
	try:
		download_path = download_file_from_url(url)
		audio_file_name = os.path.basename(download_path).split('.')[0]
		audio = AudioSegment.from_file(download_path)
		wav_audio_file_path = os.path.join("memory", f"{audio_file_name}.wav")
		# Path to your audio file (must be WAV format, 16kHz, mono)
		audio.export(wav_audio_file_path, format="wav")
		if isinstance(download_path, tuple) and download_path[0] == -1:
			return (-1, download_path[1])
		with open(wav_audio_file_path, "rb") as audio_file:
			encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
		return encoded_string
	
	except Exception as e:
		print(f"[ERROR] Failed to encode audio from {url} to base64: {e}")
		return (-1, e)
	
def process_audio_url(url, question=""):
    instructions = (
        "You are the best audio processor.\n"
        "First transcribe the audio if possible.\n"
        "Then answer this question (if blank, don't give any Analysis):\n"
        f"{question}\n\n"
        "Return output in this format:\n"
        "Transcription: <text>\n"
        "Analysis: <answer>\n"
		"Strictly return ONLY the output"
    )
	
    audio_format = "wav"
    audio_base64 = convert_audio_to_16kHz_base64(url)
    response = aipipe.query_audio_processor(audio_base64, audio_format, instructions)
    return response.get("choices", [{}])[0].get("message", {}).get("content", "")
# print("Testing process_audio_url function")
# test_url = "https://tds-llm-analysis.s-anand.net/demo-audio.opus"
# response = process_audio_url(test_url, "What is the gender of the speaker?")
# print("Response:", response)

def generate_image_from_text(prompt): # [TODO] Fix!
	instructions = (
		"You are an expert image generator.\n"
		"Generate a the best describing image based on the following prompt:\n"
		f"{prompt}\n\n"
		"Return output as a base64-encoded image URL string."
		"Strictly return ONLY the base64 URL string."
	)
	response = aipipe.query_image_generator(instructions)
	print("Response:", response)
	image_base64 =  response.get("choices", [{}])[0].get("message", {}).get("content", "")
	# convert image to file
	image_data = image_base64.split(",")[1] if "," in image_base64 else image_base64
	image_bytes = base64.b64decode(image_data)
	temp_name = tempfile.NamedTemporaryFile(delete=False, suffix="." + image_base64.split(";")[0].split("/")[1] if ";" in image_base64 else "png")
	image_path = os.path.join("memory", os.path.basename(temp_name.name))
	with open(image_path, "wb") as img_file:
		img_file.write(image_bytes)
	return image_path
# print("Testing generate_image_from_text function")
# test_prompt = "A beautiful sunrise over the mountains with a river flowing through a forest."
# image_path = generate_image_from_text(test_prompt)
# print("Generated image saved at:", image_path)
