


import librosa
# pip install librosa

import vamp
"""
1. pip install vamp
2. https://code.soundsoftware.ac.uk/projects/vamp-plugin-pack 에서 운영체제에 맞는 exe파일을 받고 Chordino and NNLS chroma 플러그인만 설치
"""

import glob
import os.path
import youtube_dl
import json

from PIL import Image, ImageDraw, ImageFont
import music_chord_database as mcd
#pip install pillow


JSON_PATH = 'data.json'

class _Chord_Classification_Service:

    _instance = None
    
    # 유튜브 url로부터 시간별 코드리스트, 비트리스트, 유튜브 추출 파일 이름을 반환하는 함수
    def load_audio_data_from_url(self, url):
        ydl_opts = {
            'format': 'best',
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # 확장자 변경
        files = glob.glob("*.mp4")
        audio_file_name = ''

        signal, sr = 0,0
        for x in files:
            if not os.path.isdir(x):
                filename = os.path.splitext(x)
                audio_file_name = filename[0]
                signal, sr = librosa.load(x)
                os.remove(x)


        # load audio file


        predicted_beat_list = vamp.collect(signal, sr, "beatroot-vamp:beatroot")

        predicted_chord_list = vamp.collect(signal, sr, "nnls-chroma:chordino")

        chord_list = []
        for i in predicted_chord_list['list']:
            i['timestamp'] = float(i['timestamp'])
            chord_list.append(i)

        beat_list = []
        for i in predicted_beat_list['list']:
            beat_list.append(float(i['timestamp']))

        return chord_list, beat_list, audio_file_name.split('-')[0]
    
    # load_audio_data_from_url로부터 정보를 받아와 악보를 저장하는 함수
    def make_music_sheet(self, url, title):
        chord_list, beat_list, audio_file_name = self.load_audio_data_from_url(url)
        print(chord_list)
        print(beat_list)
        print(len(beat_list))

        # for문을 돌다가 마지막 element에 도달하기 전에 끊기지 않게 하기 위함
        while((len(beat_list) + 6) % 16 != 0):
            beat_list.append(beat_list[-1])
        print(len(beat_list))
        beat_list.append(beat_list[-1])

        text = ''
        if title == '':
            title = audio_file_name


        text += title
        text += '\n\n\n'


        total_chord_cnt = 0
        beat_flag = 0
        for chord in chord_list:
            if chord['timestamp'] >= 0 and chord['timestamp'] < beat_list[0]:
                if chord['label'] == 'N':
                    continue
                text += chord['label'] + '  '
                total_chord_cnt += 1

        init_flag = True
        for beat_id in range(len(beat_list)):
            if init_flag == False:
                if beat_flag != 16:
                    beat_flag += 1
                    continue
            else:
                if beat_flag != 10:
                    beat_flag += 1
                    continue
                init_flag = False

            for chord in chord_list:
                if chord['timestamp'] >= beat_list[beat_id - beat_flag] and chord['timestamp'] < beat_list[beat_id]:
                    text += chord['label'] + '  '
                    total_chord_cnt += 1
            text += '\n\n'
            beat_flag = 0

        for chord in chord_list:
            if chord['timestamp'] >= 0 and chord['timestamp'] < beat_list[0]:
                if chord['label'] == 'N':
                    continue
                text += chord['label'] + '  '
                total_chord_cnt += 1

        sheet_height = len(text.split('\n\n') )
        sheet_width = int(250 * total_chord_cnt/sheet_height)
        #./ batang.ttc
        print(sheet_height * 90 / sheet_width)
        if  sheet_height * 90 / sheet_width > 8:
            sheet_width += 250
        font = ImageFont.truetype('C:/Windows/Fonts/batang.ttc', 45)
        img = Image.new(mode='RGB', size=(sheet_width, sheet_height * 90), color='#FFF')
        draw = ImageDraw.Draw(img)
        draw.text((50, 50), text, font=font, fill='#000')
        img.save(title + '.png', format='PNG')



    def get_top_three_similar_chord_music(self, url, json_path):

        #1. 연속코드 비교
        chord_list_with_timestramp = self.load_audio_data_from_url(url)[0] #여기서 하나만 받았기 때문에 사실 튜플형태로 반환되므로 [0]을 해준다

        continuous_chord_list = mcd.get_contionuous_chord_list(chord_list_with_timestramp)


        same_chord_progression_cnt_dict = {}

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for key, value in data.items():
            same_chord_progression_cnt = {}
            for cont_chord_data in value:
                for cont_chord in continuous_chord_list:
                    if cont_chord_data == cont_chord:
                        if cont_chord not in same_chord_progression_cnt:
                            same_chord_progression_cnt[cont_chord] = 1
                        else:
                            same_chord_progression_cnt[cont_chord] += 1
            same_chord_progression_cnt_dict[key] = same_chord_progression_cnt

        print(same_chord_progression_cnt_dict)





        #2. 단일코드 비교















def  Chord_Classification_Service():
    
    #singleton 구조인데 그냥 유튭강의 따라한 흔적. 속도 아주 조금더 빠르지 않을까 생각. 없애도 무방

    #ensure that we only have 1 instance of CCS
    if  _Chord_Classification_Service._instance is None:
        _Chord_Classification_Service._instance = _Chord_Classification_Service()
    return  _Chord_Classification_Service._instance


ccs = Chord_Classification_Service()

let_it_be_url = 'https://www.youtube.com/watch?v=QDYfEBY9NM4'
The_visitor_url = 'https://www.youtube.com/watch?v=y5YmTj8KDWM'
brown_url = 'https://www.youtube.com/watch?v=-5duYTCCtqI'
how_you_like_that_url = 'https://www.youtube.com/watch?v=ioNng23DkIM'

title = ''
#ccs.make_music_sheet(let_it_be_url, title)

#
#
json_path = JSON_PATH
ccs.get_top_three_similar_chord_music(The_visitor_url, json_path)


