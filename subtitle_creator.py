import assemblyai as aai
from moviepy import TextClip
import srt

api_key = "YOUR_ASSEMBLYAI_API_KEY"
download_dir = "downloaded_clips/"

# Set API key
aai.settings.api_key = api_key

def get_subtitles(video_file):

    print("[ .. ] Generating subtitles..")

    # Set and pass config to transcriber
    config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.best, language_code="de")
    transcript = aai.Transcriber(config=config).transcribe(video_file)

    # Raise error if neccessary
    if transcript.status == "error":
        print("[ WARNING ] Unable to create subtitles.")
        return []
    
    try:
        # Export transcript as srt format
        srt_output = transcript.export_subtitles_srt(chars_per_caption=18)

    except aai.types.TranscriptError:
        print("[ WARNING ] Unable to export subtitles to srt format.")
        return []

    # Parse srt to python object
    subtitles = list(srt.parse(srt_output))

    # Go through all subtitles and create a TextClip for each of them
    text_clip_subtitles = []
    font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
    for s in subtitles:
        text_clip_subtitles.append(TextClip(text=s.content, method="caption", color="white",
                                            size=(int(0.9*608), 1080), margin=(int(0.05*608), 0), 
                                            text_align="center", vertical_align="center", 
                                            stroke_color="black", stroke_width=5,
                                            duration=(s.end-s.start).total_seconds(), 
                                            font=font_path, font_size=72).with_start(s.start.total_seconds()))

    print("[ OK ] Subtitles generated.")

    return text_clip_subtitles

def subtitle_creator_handler(video_file):

    print("[ .. ] Starting subtitle_creator module..")

    subtitles = get_subtitles(video_file)

    print("[ OK ] subtitle_creator module has finished.")
    print()

    return subtitles

if __name__ == "__main__":
    pass