from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import os
import requests
import zipfile
import io
import logging
import re
import subprocess
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:1420"}})

# define logs
log_directory = os.path.abspath(os.path.join(os.getcwd(), '..', 'python', 'logs'))
log_file = os.path.join(log_directory, 'server_log.log')

# create log directory if it doesn't exist
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# configure logging
logging.basicConfig(filename=log_file, 
                    level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('flask').setLevel(logging.ERROR)
logging.getLogger('werkzeug').setLevel(logging.ERROR)

# remove ANSI from logs
def remove_ansi_escape_sequences(log_line):
    ansi_escape = re.compile(r'(?:\x1B[@-_][0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', log_line)

# get latest commit hash
def get_latest_commit_hash():
    api_url = "https://api.github.com/repos/blaisewf/rvc-cli/commits/main"
    response = requests.get(api_url)
    response.raise_for_status()
    commit_data = response.json()
    return commit_data['sha']

# save last commit hash to version.json
def save_commit_info(commit_hash):
    version_file_path = os.path.abspath(os.path.join(os.getcwd(), '..', 'python', 'version.json'))
    logging.info(f"Saving commit {commit_hash} to {version_file_path}")
    with open(version_file_path, 'w') as version_file:
        json.dump({'commit_hash': commit_hash}, version_file)
    logging.info(f"Saved commit {commit_hash} to version.json")

# load last commit hash from version.json
def load_commit_info():
    version_file_path = os.path.abspath(os.path.join(os.getcwd(), '..', 'python', 'version.json'))
    logging.info(f"Loading commit info from {version_file_path}")
    if not os.path.exists(version_file_path):
        logging.info("No commit info found. Downloading RVC repository from GitHub...")
        return None
    with open(version_file_path, 'r') as version_file:
        data = json.load(version_file)
        return data.get('commit_hash')
    
def checkUpdate():
    latest_commit_hash = get_latest_commit_hash()
    saved_commit_hash = load_commit_info()

    if saved_commit_hash == latest_commit_hash:
        logging.info("RVC repository is up to date. No need to download.")
        yield 'data: RVC repository is up to date. No need to download.\n\n'
        return False

# download RVC repository from GitHub and extract it
def downloadRepo():
    extraction_path = os.path.abspath(os.path.join(os.getcwd(), '..', 'python'))
    new_folder_name = os.path.join(extraction_path, 'rvc')

    latest_commit_hash = get_latest_commit_hash()
    logging.info(f"Latest commit hash: {latest_commit_hash}")

    saved_commit_hash = load_commit_info()

    if saved_commit_hash == latest_commit_hash:
        logging.info("RVC repository is up to date. No need to download.")
        yield 'data: RVC repository is up to date. No need to download.\n\n'
        return


    yield 'data: Downloading RVC repository from GitHub...\n\n'
    
    url = "https://github.com/blaisewf/rvc-cli/archive/refs/heads/main.zip"
    logging.info(remove_ansi_escape_sequences("Downloading RVC repository from GitHub..."))

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        yield 'data: Downloading RVC repository from GitHub... Done!\n\n'
        logging.info(remove_ansi_escape_sequences("Downloading RVC repository from GitHub... Done!"))

        os.makedirs(extraction_path, exist_ok=True)

        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
            zip_file.extractall(extraction_path)
            yield 'data: Extracting RVC repository from GitHub... Done!\n\n'

        old_folder_name = os.path.join(extraction_path, 'rvc-cli-main')

        if os.path.exists(old_folder_name):
            os.rename(old_folder_name, new_folder_name)
            yield 'data: Renaming extracted folder to "rvc"... Done!\n\n'
            logging.info(remove_ansi_escape_sequences(f"Renamed folder from 'rvc-cli-main' to 'rvc'"))

        yield 'data: RVC repository downloaded successfully.\n\n'
        save_commit_info(latest_commit_hash)
        logging.info(f"Saved commit {latest_commit_hash} to version.json")
        yield from runInstallation()

    except requests.RequestException as e:
        logging.error(remove_ansi_escape_sequences(f"Error downloading RVC repository from GitHub: {str(e)}"))
        yield 'data: Error downloading RVC repository from GitHub.\n\n'
    except zipfile.BadZipFile:
        logging.error(remove_ansi_escape_sequences("Error: Bad ZIP file"))
        yield 'data: Error: Bad ZIP file.\n\n'
    except OSError as e:
        logging.error(remove_ansi_escape_sequences(f"Error during extraction: {str(e)}"))
        yield 'data: Error during extraction.\n\n'

# run RVC installation
def runInstallation():
    bat_file_path = os.path.join(os.path.abspath(os.path.join(os.getcwd(), '..', 'python', 'rvc')), 'install.bat')

    yield 'data: Downloading requeriments...\n\n'
    logging.info(remove_ansi_escape_sequences("Downloading requeriments..."))

    try:
        process = subprocess.Popen(
            [bat_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            shell=True,
            cwd=os.path.abspath(os.path.join(os.getcwd(), '..', 'python', 'rvc'))
        )

        for line in process.stdout:
            yield f'data: {line}\n\n'
            logging.info(line.strip())

        process.stdout.close()
        process.wait()

        yield 'data: Installation completed successfully.\n\n'
        logging.info(remove_ansi_escape_sequences("Installation completed successfully."))

    except Exception as e:
        yield f'data: Error running installation: {str(e)}\n\n'
        logging.error(remove_ansi_escape_sequences(f"Error running installation: {str(e)}"))

# download model
def downloadModel(modelLink):
    command = [os.path.join("env", "python.exe"), "rvc_cli.py", "download", "--model_link", f'"{modelLink}"']
    command_path = os.path.abspath(os.path.join(os.getcwd(), '..', 'python', 'rvc'))

    logging.info(remove_ansi_escape_sequences(f"command: {' '.join(command)}"))
    logging.info(remove_ansi_escape_sequences(f"command_path: {command_path}"))

    yield 'data: Downloading model...\n\n'
    logging.info(remove_ansi_escape_sequences("Downloading model..."))

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            shell=True,
            cwd=command_path
        )

        for line in process.stdout:
            yield f'data: {line}\n\n'
            logging.info(line.strip())

        process.stdout.close()
        process.wait()

        yield 'data: Model downloaded successfully.\n\n'
        logging.info(remove_ansi_escape_sequences("Model downloaded successfully."))

    except Exception as e:
        yield f'data: Error running download: {str(e)}\n\n'
        logging.error(remove_ansi_escape_sequences(f"Error running download: {str(e)}"))



@app.route('/')
def home():
    client_ip = request.remote_addr
    logging.info(remove_ansi_escape_sequences(f"Request from {client_ip}"))
    return jsonify({'status': 'Hello from server!'}), 200

@app.route('/pre-install', methods=['GET'])
def pre_install():
    return Response(downloadRepo(), content_type='text/event-stream')

@app.route('/check-update', methods=['GET'])
def check_update():
    logging.info(remove_ansi_escape_sequences("Checking for updates..."))
    return Response(checkUpdate(), content_type='text/event-stream')

@app.route('/download', methods=['GET'])
def download_model():
    model_link = request.args.get('link')
    logging.info(remove_ansi_escape_sequences(f"model_link: {model_link}"))
    if not model_link:
        logging.error(remove_ansi_escape_sequences("Error: model link argument is missing."))
        return Response("Error: model link argument is missing.", status=400)
    
    return Response(downloadModel(model_link), content_type='text/event-stream')


if __name__ == "__main__":
    logging.info(remove_ansi_escape_sequences("Server started at: http://127.0.0.1:5123"))
    app.run(port=5123, host='0.0.0.0', debug=False)
    logging.info(remove_ansi_escape_sequences("Server stopped"))
