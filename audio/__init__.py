

import os

import moviepy.editor as mp
from moviepy.video.io import ffmpeg_tools


def converts_to_mp4(file):
    # Đọc file mp3 từ bộ nhớ vào một đối tượng BytesIO
    file_name = 'data'
    temp_dir = "temp"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    mp3_dir = os.path.join(temp_dir, "{}.mp3".format(file_name))
    file.save(os.path.join(mp3_dir))

    wav_dir =  os.path.join(temp_dir, "{}.wav".format(file_name))
    ffmpeg_tools.ffmpeg_extract_audio(mp3_dir, wav_dir)

    # Tạo đối tượng AudioFileClip từ file mp3
    audio = mp.AudioFileClip(wav_dir)
    

    # Tạo đối tượng ImageClip từ ảnh tĩnh (bạn có thể thay đổi ảnh tùy ý)
    image = mp.ImageClip('image.jpg')
    # Thiết lập thời lượng của ImageClip bằng với thời lượng của AudioFileClip
    image.duration = audio.duration

    # Kết hợp ImageClip và AudioFileClip để tạo đối tượng VideoFileClip
    video = image.set_audio(audio)

    # Tạo một đối tượng BytesIO để lưu video mp4 vào bộ nhớ

    # Xuất video mp4 vào đối tượng BytesIO

    mp4_dir = "{}/{}.mp4".format(temp_dir, file_name)
    video.write_videofile(mp4_dir, codec="libx264", fps=1)
    # video_file.save()
     # Xóa file mp3 khỏi thư mục tạm
    
    os.remove(mp3_dir)
    os.remove(wav_dir)
    return mp4_dir
    # os.remove(os.path.join('./audio', "data.mp4"))

    # Tạo một đối tượng MediaIoBaseUpload từ đối tượng BytesIO
    # media_body = MediaIoBaseUpload(video_file, "video/mp4", resumable=True)

   

    """
    # Tạo một đối tượng MediaIoBaseUpload từ đối tượng BytesIO
    media_body = MediaIoBaseUpload(video_file, "video/mp4", resumable=True)"""