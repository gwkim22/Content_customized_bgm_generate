import torch
from transformers import pipeline
import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, 'riffusion'))
from _interpolation import Riffusion_interpolation
from utils import *
import argparse
import numpy as np
from riffusion.cli import audio_to_image
import pickle
import pydub

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--code", default="1", help="code used to verify request") 
    parser.add_argument("--output_dir",default=os.path.join(BASE_DIR, 'tmp'))
    parser.add_argument("--sentiment_string",default="80 94 fear")
    args, _ = parser.parse_known_args()
    
    sentiment = list(map(str, args.sentiment_string.split(' ')))
    sentiments = []
    sentiments = [sentiment[i:i+3] for i in range(0, len(sentiment), 3)] # [[6, 12, 'surprise']]

    for i, s in enumerate(sentiments):
        s[0] = int(s[0])
        s[1] = int(s[1])
        prompt, seed_audio = sent2prompt(s[2], 1) # s[2]는 감정(sadness, joy 등)이고, prompt와 seed image(둘다 리스트 4개) 반환
        width = int((s[1]-s[0]) // 5 + 1) # interpolation step으로 1당 5초로 계산
        duration_ms = s[1]-s[0]
        segment = pydub.AudioSegment.from_file(seed_audio[i]) # TODO 추후 수정
        output_dir_path = os.path.join(BASE_DIR, f'riffusion/seed_images/{s[2]}')
        extension = 'wav'
        # print(s, duration_ms)
        segment_duration_ms = int(segment.duration_seconds * 1000)
        clip_start_ms = np.random.randint(0, segment_duration_ms - duration_ms)
        clip = segment[clip_start_ms : clip_start_ms + 5000]
        clip_path = os.path.join(output_dir_path, 'test'+str(i)+'.wav')
        clip.export(clip_path, format=extension)
        audio_to_image(audio=clip_path, image=os.path.join(BASE_DIR, f'riffusion/seed_images/{s[2]}.png'))
        seed_image = os.path.join(BASE_DIR, f'riffusion/seed_images/{s[2]}.png')
        riffusion = Riffusion_interpolation(prompt[i], prompt[i], seed_image,num_inference_steps=50, num_interpolation_steps= width) # prompt와 seed image로 bgm 생성하고, 저장까지 진행
        riffusion.run(i, args.code)
    # TODO 모델팀 최종 output에 따라 파일 이름 규칙 정하기
    print("filepath") # 파일 이름 포함 파일 경로
if __name__ == '__main__':
    main()