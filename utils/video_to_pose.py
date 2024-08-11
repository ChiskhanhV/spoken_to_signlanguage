import cv2
from pose_format.utils.holistic import load_holistic
import mediapipe as mp

mp_holistic = mp.solutions.holistic
FACEMESH_CONTOURS_POINTS = [str(p) for p in sorted(set([p for p_tup in list(mp_holistic.FACEMESH_CONTOURS) for p in p_tup]))]

def load_video_frames(cap: cv2.VideoCapture):
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        yield cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    cap.release()

def pose_estimate(video_path, output_path, format):
    print('Load video ...')
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = round(cap.get(cv2.CAP_PROP_FPS))
    frames = load_video_frames(cap)
    print('Estimating pose ...')
    
    if format == 'mediapipe':
        pose = load_holistic(frames, fps=fps, width=width, height=height, progress=True, 
            additional_holistic_config={'model_complexity': 2, 'refine_face_landmarks': True})

        pose = pose.get_components(["POSE_LANDMARKS", "FACE_LANDMARKS", "LEFT_HAND_LANDMARKS", "RIGHT_HAND_LANDMARKS"], {"FACE_LANDMARKS": FACEMESH_CONTOURS_POINTS})
    else:
        raise NotImplementedError('Pose format not supported')
    print('Writing ...')
    with open(output_path, "wb") as f:
        pose.write(f)
