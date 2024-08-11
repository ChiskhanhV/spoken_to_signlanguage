import os
import string
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

def read_scripts_and_create_mapping(scripts_path):
    script_to_content = {}
    for script in os.listdir(scripts_path):
        script_name = os.path.splitext(script)[0]
        script_file_path = os.path.join(scripts_path, script)
        with open(script_file_path, 'r', encoding='UTF-8') as file:
            content = file.read().strip()
            script_to_content[script_name] = content
    return script_to_content

def create_mapping(videos_path, scripts_path):
    video_files = sorted(os.listdir(videos_path))
    script_to_content = read_scripts_and_create_mapping(scripts_path)

    video_to_script = {}
    script_to_video = {}

    for video in video_files:
        video_name = os.path.splitext(video)[0]
        script_name = video_name.replace('video', 'script')
        if script_name in script_to_content:
            script_content = script_to_content[script_name]
            phrases = [phrase.strip() for phrase in script_content.split(",")]
            video_to_script[video_name] = phrases
            for phrase in phrases:
                script_to_video[phrase] = video_name + '.mp4'

    #Kiểm tra ánh xạ script_to_video
    for phrase, video in script_to_video.items():
        print(f"Script: '{phrase}' -> Video: {video}")

    return video_to_script, script_to_video

def clean_transcript(transcript):
    translator = str.maketrans('', '', string.punctuation)
    cleaned_transcript = transcript.translate(translator)
    return cleaned_transcript

# def get_sign_videos(transcript, script_to_video, min_bleu_score=0.2):
#     cleaned_transcript = clean_transcript(transcript)
#     words = cleaned_transcript.split(" ")
#     matched_videos = []
#     used_phrases = set()
#     used_videos = set()
#     smoothing_function = SmoothingFunction().method4

#     for length in range(len(words), 0, -1):
#         for i in range(len(words) - length + 1):
#             phrase = ' '.join(words[i:i+length])
#             highest_bleu_score = 0
#             best_video = 'default.mp4'
            
#             for ref_phrase, video in script_to_video.items():
#                 ref_words = ref_phrase.split()
#                 candidate_words = phrase.split()
                
#                 #Thang đo BLEU-4
#                 bleu_score = sentence_bleu([ref_words], candidate_words, weights=(0.25, 0.25, 0.25, 0.25), smoothing_function=smoothing_function)
#                 if bleu_score > highest_bleu_score and phrase not in used_phrases and video not in used_videos:
#                     highest_bleu_score = bleu_score
#                     best_video = video

#             if highest_bleu_score >= min_bleu_score:
#                 matched_videos.append(best_video)
#                 used_phrases.update(phrase.split())
#                 used_videos.add(best_video)
#                 print(f"Cụm từ: '{phrase}' - Điểm BLEU cao nhất: {highest_bleu_score}")

#     if not matched_videos:
#         matched_videos.append('default.mp4')
    
#     return matched_videos

# def get_sign_videos(transcript, script_to_video, min_bleu_score=0.2):
#     cleaned_transcript = clean_transcript(transcript)
#     words = cleaned_transcript.split(" ")
#     matched_videos = []
#     used_phrases = set()
#     used_videos = set()
#     smoothing_function = SmoothingFunction().method4

#     i = 0
#     while i < len(words):
#         highest_bleu_score = 0
#         best_video = 'default.mp4'
#         best_phrase_length = 0
#         selected_phrase = ""
        
#         # Tìm cụm từ dài nhất có điểm BLEU cao nhất
#         for length in range(len(words) - i, 0, -1):
#             phrase = ' '.join(words[i:i+length])
#             if phrase in used_phrases:  # Kiểm tra xem cụm từ đã được sử dụng chưa
#                 continue
#             for ref_phrase, video in script_to_video.items():
#                 ref_words = ref_phrase.split()
#                 candidate_words = phrase.split()
                
#                 # Tính điểm BLEU-4
#                 bleu_score = sentence_bleu([ref_words], candidate_words, weights=(0.25, 0.25, 0.25, 0.25), smoothing_function=smoothing_function)
#                 if bleu_score > highest_bleu_score and bleu_score >= min_bleu_score:
#                     highest_bleu_score = bleu_score
#                     best_video = video
#                     best_phrase_length = length
#                     selected_phrase = phrase

#         # Nếu tìm thấy một cụm từ phù hợp, thêm video và cập nhật vị trí
#         if best_phrase_length > 0 and best_video not in used_videos:
#             matched_videos.append(best_video)
#             used_phrases.add(selected_phrase)  # Thêm cụm từ vào danh sách đã sử dụng
#             used_videos.add(best_video)  # Thêm video vào danh sách đã sử dụng
#             print(f"Cụm từ: '{selected_phrase}' - Điểm BLEU cao nhất: {highest_bleu_score}")
#             i += best_phrase_length
#         else:
#             # Nếu không tìm thấy cụm từ phù hợp, tiếp tục với từ tiếp theo
#             i += 1

#     # Trường hợp không tìm thấy video nào
#     if not matched_videos:
#         matched_videos.append('default.mp4')
    
#     return matched_videos

def get_sign_videos(transcript, script_to_video, min_bleu_score=0.2):
    cleaned_transcript = clean_transcript(transcript)
    words = cleaned_transcript.split(" ")
    matched_videos = []
    used_phrases = set()
    used_videos = set()
    smoothing_function = SmoothingFunction().method4

    i = 0
    while i < len(words):
        highest_bleu_score = 0
        best_video = 'default.mp4'
        best_phrase_length = 0
        selected_phrase = ""
        
        # Tìm cụm từ dài nhất có điểm BLEU cao nhất
        for length in range(len(words) - i, 0, -1):
            phrase = ' '.join(words[i:i+length])
            if phrase in used_phrases:  # Kiểm tra xem cụm từ đã được sử dụng chưa
                continue
            for ref_phrase, video in script_to_video.items():
                ref_words = ref_phrase.split()
                candidate_words = phrase.split()
                
                # Tính điểm BLEU-4
                bleu_score = sentence_bleu([ref_words], candidate_words, weights=(1, 0, 0, 0), smoothing_function=smoothing_function)
                
                # In ra điểm BLEU cho từng cụm từ và video tương ứng
                print(f"Phrase: '{phrase}', Ref phrase: '{ref_phrase}', BLEU score: {bleu_score}")
                
                if bleu_score > highest_bleu_score and bleu_score >= min_bleu_score:
                    highest_bleu_score = bleu_score
                    best_video = video
                    best_phrase_length = length
                    selected_phrase = phrase

        # Nếu tìm thấy một cụm từ phù hợp, thêm video và cập nhật vị trí
        if highest_bleu_score >= min_bleu_score and best_video not in used_videos:
            matched_videos.append(best_video)
            used_phrases.add(selected_phrase)  # Thêm cụm từ vào danh sách đã sử dụng
            used_videos.add(best_video)  # Thêm video vào danh sách đã sử dụng
            print(f"Cụm từ: '{selected_phrase}' - Điểm BLEU cao nhất: {highest_bleu_score}")
            i += best_phrase_length if best_phrase_length > 0 else 1
        else:
            # Nếu không tìm thấy cụm từ phù hợp, tiếp tục với từ tiếp theo
            i += 1

    # Trường hợp không tìm thấy video nào
    if not matched_videos:
        matched_videos.append('default.mp4')
    
    return matched_videos







