from googleapiclient.discovery import build


class SlidesUtils():
    def __init__(self, flow):
        credentials = flow.credentials
        self.service = build('slides', 'v1', credentials=credentials)

    def get_slides_url(self, presentation_id):
        # Get the presentation object from the service
        # presentation = self.service.presentations().get(presentationId=presentation_id, fields="webViewLink").execute()
        # print(presentation.keys())
        # # Get the base URL of the presentation from the web view link
        # presentation_url = presentation.get("webViewLink").split("?")[0]

        presentation_url = "https://docs.google.com/presentation/d/{}/edit".format(
            presentation_id)
        print(presentation_url)
        # Get the first slide id from the slides list
        # presentation.get("slides", [])[0].get("objectId")
        first_slide_id = "1"
        # Get the URL of the first slide by appending "#slide=id.p" + first_slide_id to the base URL
        slide_url = presentation_url + "#slide=id.{}".format(first_slide_id)

        return presentation_url, slide_url
        # return render_template("play_slides.html", url=url, slide_url=slide_url)

    def get_speaker_note(self, presentation_id, slide_id):
        # Get the presentation object from the service
        presentation = self.service.presentations().get(
            presentationId=presentation_id).execute()

        # Find the slide with the given slide id
        slide = None
        print(presentation.get("slides", []))
        for s in presentation.get("slides", []):
            print(s.get('objectId'))
            if s.get("objectId") == slide_id:
                slide = s
                break
        # If the slide is not found, return an error message
        if slide is None:
            return "Slide not found"
        # Find the speaker notes shape id from the slide properties
        speaker_notes_shape_id = slide.get("slideProperties", {}).get(
            "notesPage", {}).get("notesProperties", {}).get("speakerNotesObjectId")
        # If the speaker notes shape id is not found, return an empty message
        if speaker_notes_shape_id is None:
            return ""
        # Find the speaker notes shape from the notes page shapes
        speaker_notes_shape = None
        for shape in slide.get("slideProperties", {}).get("notesPage", {}).get("pageElements", []):
            if shape.get("objectId") == speaker_notes_shape_id:
                speaker_notes_shape = shape
                break
        # If the speaker notes shape is not found, return an empty message
        if speaker_notes_shape is None:
            return ""
        # Get the speaker notes text from the shape text content
        speaker_notes_text = ""
        for paragraph in speaker_notes_shape.get("shape", {}).get("text", {}).get("textElements", []):
            speaker_notes_text += paragraph.get("textRun",
                                                {}).get("content", "")
        # Return the speaker notes text as a string
        return speaker_notes_text

    def import_audio(self, audio_id, presentation_id, slide_id):

        # The size of the audio in EMU (1 cm = 360000 EMU).
        audio_size = {
            "width": {
                "magnitude": 3000000,
                "unit": "EMU"
            },
            "height": {
                "magnitude": 3000000,
                "unit": "EMU"
            }
        }

        # The transform of the audio in EMU (1 cm = 360000 EMU).
        audio_transform = {
            "scaleX": 1,
            "scaleY": 1,
            "translateX": 311708,
            "translateY": 744575,
            "unit": "EMU"
        }

        # Create a batchUpdate request with a createVideo request.
        requests = [
            {
                "createVideo": {
                    "source": "DRIVE",
                    "id": audio_id,
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": audio_size,
                        "transform": audio_transform
                    }
                }
            }
        ]

        # Execute the request.
        response = self.service.presentations().batchUpdate(
            presentationId=presentation_id, body={"requests": requests}).execute()

        return response