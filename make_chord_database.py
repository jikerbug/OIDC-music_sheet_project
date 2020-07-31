#-*- coding:utf-8 -*-
import youtube_dl
import librosa
import glob
import os.path
import vamp
import json


JSON_PATH = 'data.json'

def get_double_chord_list(chord_list_with_timestamp): # 한글 파일명은 librosa에서 로딩이 안되기 때문에 filename_id로 wav파일을 저장
    # 확장자 변경
    chord_list = []
    for i in chord_list_with_timestamp:
        chord_list.append(i['label'])
    double_chord_list = []

    for idx in range(len(chord_list) - 1):
        if chord_list[idx] != 'N' and chord_list[idx+1] != 'N':

            double_chord = chord_list[idx] + '-' + chord_list[idx+1]
            double_chord_list.append(double_chord)


    return double_chord_list

def playlist_to_audio_data(playlist_url, json_path):


    ydl = youtube_dl.YoutubeDL({
        'format': 'best'
    })

    with ydl:
        result = ydl.download([playlist_url])

    # 확장자 변경
    files = glob.glob("*.mp4")

    chord_list_dict = {}
    with open(json_path, 'r', encoding='utf-8') as f:
        chord_list_dict = json.load(f)

    for x in files:
        filename = os.path.splitext(x)
        new_name_by_id = filename[0].split('-')[-1] + '.wav' # librosa가 한글 파일을 읽을수 없어서 파일명 변경
        os.rename(x, new_name_by_id)
        signal, sr = librosa.load(new_name_by_id) # (signal, sr) 형태로 저장
        os.remove(new_name_by_id)
        chord_list_with_timestamp = vamp.collect(signal, sr, "nnls-chroma:chordino")


        double_chord_list = get_double_chord_list(chord_list_with_timestamp['list'])

        dict_key_music_name = ''
        for idx in range(len(filename[0].split('-')) - 1):
            dict_key_music_name += filename[0].split('-')[idx]

        chord_list_dict[dict_key_music_name] = double_chord_list

    with open(json_path, "w", encoding='utf-8') as fp:
        json.dump(chord_list_dict, fp, indent=4, ensure_ascii=False)



def multiple_playlist_to_audio_data(playlist_url_list, json_path):


    data = {}
    with open(json_path, "w", encoding='utf-8') as fp:
        json.dump(data, fp, indent=4)

    for playlist_url in playlist_url_list:
        playlist_to_audio_data(playlist_url, json_path)





if __name__ == "__main__":
    playlist_url_list = []
    #playlist_url_list.append('https://www.youtube.com/playlist?list=OLAK5uy_kfRVORKFdFjpkjalascOpqWbNawtinMmI')
    playlist_url_list.append('https://www.youtube.com/playlist?list=OLAK5uy_mviJVGP6F4FJgDITAPdwAJlsErxQCpkK8')

    json_path = JSON_PATH
    multiple_playlist_to_audio_data(playlist_url_list, json_path)








