from io import BytesIO
import os
import uuid
from flask import request, flash, redirect
from werkzeug.utils import secure_filename
from datetime import datetime
from googleapiclient.http import MediaIoBaseUpload, MediaFileUpload
from googleapiclient.discovery import build


# Create a class to encapsulate the file uploading functions and attributes
class GG_DriveFileUploader:
    def __init__(self, flow):
        # Initialize the upload folder and the GoogleAPI object
        credentials = flow.credentials
        self.service = build('drive', 'v3', credentials=credentials)

    def upload_audio(self, audio_file):

        file_metadata = {
            "name": "data",
            "mimeType": "video/mp4"  # Change the MIME type to video/mp4
        }
        # media = MediaFileUpload(audio_file.stream)

        with open(audio_file, "rb") as fh:
            buf = BytesIO(fh.read())

 
        media_body = MediaIoBaseUpload(buf, "video/mp4", resumable=True)
        response = self.service.files().create(
            body=file_metadata, media_body=media_body).execute()
        # Get the id of the audio file on Google Drive
        audio_id = response.get("id")
        return audio_id

    def upload(self, file):
        """Upload a file using the drive service and the credentials

        Args:
        file: A file from flask app.
        """

        buffer_memory = BytesIO()
        file.save(buffer_memory)

        media_body = MediaIoBaseUpload(file, file.mimetype, resumable=True)

        created_at = datetime.now().strftime("%Y%m%d%H%M%S")
        file_metadata = {
            "name": f"{file.filename} ({created_at})"
        }

        returned_fields = "id, name, mimeType, webViewLink, exportLinks"

        upload_response = self.service.files().create(
            body=file_metadata,
            media_body=media_body,
            fields=returned_fields
        ).execute()

        return upload_response
