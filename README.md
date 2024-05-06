# Python Google Drive Uploader

## Requirements

You will need to create a Google Cloud project and enable the Google Drive API service.

After enabling the Google Drive API service, you will also be required to create an `OAuth client ID`. Select `Desktop app` for the `Application type` field.

For local testing or usage, you will also need to add your Google account to the list of allowed users, which can be found under the `OAuth consent screen` page.

Run `pip install -r requirements.txt` for essential dependencies. It is recommended to use a Python environment management tool like `Conda` or `pyenv`.

```bash
conda create -n py-gdrive-uploader python=3.10
```

## Usage

```bash
python main.py -s /path/to/source/dir -a /path/to/credentials.json
```
