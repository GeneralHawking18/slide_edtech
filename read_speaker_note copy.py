from flask import Flask, request, jsonify
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Create a Flask app object
app = Flask("Google Slides App")

# Create a service account credentials object
SCOPES = ['https://www.googleapis.com/auth/presentations.readonly']


# Create a Google Slides API service object


class SlidesUtils():
    def __init__(self, flow):
        self.crediential = flow.credentials

    
    def get_speaker_notes(self):
        # Get the presentation id and slide id from the request parameters
        service = build('slides', 'v1', credentials=self.credentials)
        # presentation_id = request.args.get("presentation_id")
        # slide_id = request.args.get("slide_id")

        slide_id = "id.p1"
        presentation_id = "1S3Azmaggy5DS4IjZRIlkUQx_71-lCxsk"

        # Get the presentation object from the Google Slides API service
        presentation = service.presentations().get(presentationId=presentation_id).execute()

        # Find the slide with the given slide id
        slide = None
        for s in presentation.get("slides", []):
            if s.get("objectId") == slide_id:
                slide = s
                break
        
        # If the slide is not found, return an error message
        if slide is None:
            return jsonify({"error": "Slide not found"})

        # Find the speaker notes shape id from the slide properties
        speaker_notes_shape_id = slide.get("slideProperties", {}).get("notesPage", {}).get("notesProperties", {}).get("speakerNotesObjectId")

        # If the speaker notes shape id is not found, return an empty message
        if speaker_notes_shape_id is None:
            return jsonify({"speaker_notes": ""})

        # Find the speaker notes shape from the notes page shapes
        speaker_notes_shape = None
        for shape in slide.get("slideProperties", {}).get("notesPage", {}).get("pageElements", []):
            if shape.get("objectId") == speaker_notes_shape_id:
                speaker_notes_shape = shape
                break
        
        # If the speaker notes shape is not found, return an empty message
        if speaker_notes_shape is None:
            return jsonify({"speaker_notes": ""})

        # Get the speaker notes text from the shape text content
        speaker_notes_text = ""
        for paragraph in speaker_notes_shape.get("shape", {}).get("text", {}).get("textElements", []):
            speaker_notes_text += paragraph.get("textRun", {}).get("content", "")

        # Return the speaker notes text as a json response
        return jsonify({"speaker_notes": speaker_notes_text})

if __name__ == "__main__":
    app.run(debug = True)