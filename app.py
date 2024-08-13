from utils.sign_mapping import create_mapping, get_sign_videos
from flask import Flask, request, render_template, jsonify
import os
import requests
from pose_format import Pose
from pose_format.pose_visualizer import PoseVisualizer
from utils.video_to_pose import pose_estimate  # Import hàm từ video_to_pose.py
from moviepy.editor import VideoFileClip, concatenate_videoclips

app = Flask(__name__)

# URL của API trên Google Colab
COLAB_API_URL = 'https://03fd-34-127-36-242.ngrok-free.app/transcribe'

# Paths to the video and script folders
VIDEOS_PATH = 'datasets/videos'
SCRIPTS_PATH = 'datasets/scripts'
POSE_PATH = 'static/pose'

# Create the mapping between videos and scripts
video_to_script, script_to_video = create_mapping(VIDEOS_PATH, SCRIPTS_PATH)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    if 'audio_data' not in request.files:
        return jsonify({'error': 'No audio file uploaded'}), 400
    
    audio_data = request.files['audio_data']
    files = {'audio_data': audio_data}

    try:
        response = requests.post(COLAB_API_URL, files=files)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f'Error occurred: {e}')
        return jsonify({'error': 'Failed to transcribe audio'}), 500
    
    result = response.json()
    transcript = result.get('transcript', '')

    # Get the corresponding sign language videos
    sign_language_videos = get_sign_videos(transcript, script_to_video)
    print(sign_language_videos)
    sign_video_paths = [os.path.join(VIDEOS_PATH, video) for video in sign_language_videos]

    # Combine the sign language videos into one video
    combined_video_path = 'static/videos/combined_video.mp4'
    combine_videos(sign_video_paths, combined_video_path)

    # Chuyển đổi video kết hợp thành dữ liệu tư thế
    pose_file_path = video_to_pose_wrapper(combined_video_path)

    # Đọc dữ liệu từ tệp pose và tạo GIF mới
    try:
        with open(pose_file_path, "rb") as f:
            pose = Pose.read(f.read())
        v = PoseVisualizer(pose)
        gif_path = os.path.join("static/skeletons", 'skeleton.gif')
        v.save_gif(gif_path, v.draw())  # Đảm bảo rằng file GIF được ghi đè
    except FileNotFoundError:
        return jsonify({'error': 'Pose file not found'}), 500
    except Exception as e:
        print(f'Error occurred while processing pose data: {e}')
        return jsonify({'error': 'Failed to process pose data'}), 500

    return jsonify({'transcript': transcript, 'skeleton_file': 'skeleton.gif'})

def video_to_pose_wrapper(video_path):
    pose_output_path = os.path.join(POSE_PATH, os.path.basename(video_path).replace(".mp4", ".pose"))
    try:
        pose_estimate(video_path, pose_output_path, 'mediapipe')
    except Exception as e:
        print(f"Error occurred while running pose_video: {e}")
        raise RuntimeError(f"Command 'pose_video' failed with error: {e}")
    
    return pose_output_path

def combine_videos(video_paths, output_path):
    try:
        clips = [VideoFileClip(video) for video in video_paths]
        combined = concatenate_videoclips(clips)
        combined.write_videofile(output_path, codec='libx264', fps=30)
    except Exception as e:
        print(f"Error occurred while combining videos: {e}")
        raise RuntimeError(f"Failed to combine videos with error: {e}")

if __name__ == '__main__':
    app.run(debug=True)

