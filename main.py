import base64
import json
import requests
import re
import os
from bs4 import BeautifulSoup as soup


def read_name_list(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        r = soup(f.read(), features='html.parser')

    name_list = []
    for li in r.find_all('li'):
        name_list.append(li.find('p').text)

    return name_list


def read_audio_list(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        r = soup(f.read(), features='html.parser')

    audio_list = []
    for li in r.find_all('li'):
        # 获取每一个角色的国语和日语配音
        char_audio = {
            "ch": [],
            "jp": []
        }
        for div in li.find_all('div', resursive=False):
            if 'id' in div.attrs and re.match(r'audio-group[0-9]*', div.attrs['id']):
                # 国语
                if div.attrs['id'][-1] == '0':
                    for au in div.find_all('audio'):
                        char_audio['ch'].append(au.attrs['src'])
                # 日语
                elif div.attrs['id'][-1] == '1':
                    for au in div.find_all('audio'):
                        char_audio['jp'].append(au.attrs['src'])
        audio_list.append(char_audio)

    return audio_list


def download_audio(url, save_path):
    print(save_path, end='')
    if os.path.exists(save_path):
        print(' - 已存在')
        return
    else:
        print('download: {:s}'.format(url))
        r = requests.get(url)
        print(r.status_code)

        with open(save_path, 'wb') as f:
            f.write(r.content)
        print(' - 保存成功！')


def encode_audio(audio):
    audio_content = audio.read()
    return base64.b64encode(audio_content)


def download_all_audio(name_list_html='name-list-liyue.html', char_list_html='char-list-liyue.html'):
    name_list = read_name_list(name_list_html)
    audio_list = read_audio_list(char_list_html)

    audios_dir = './audios'
    if not os.path.exists(audios_dir):
        os.makedirs(audios_dir)

    for i in range(0, len(name_list)):
        char_name = name_list[i]

        count = 0
        for ch_au in audio_list[i]['ch']:
            audio_save_path = '{:s}/{:s}-中-{:d}.mp3'.format(
                audios_dir, char_name, count)
            download_audio(ch_au, audio_save_path)
            count += 1

        count = 0
        for jp_au in audio_list[i]['jp']:
            audio_save_path = '{:s}/{:s}-日-{:d}.mp3'.format(
                audios_dir, char_name, count)
            download_audio(jp_au, audio_save_path)
            count += 1


def encode_all_audio(audio_dir='./audios', output_dir='./encoded'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(audio_dir):
        print('Encoding {:s}/{:s}'.format(audio_dir, filename), end='')
        with open('{:s}/{:s}'.format(audio_dir, filename), 'rb') as audio:
            with open('{:s}/{:s}.txt'.format(output_dir, filename.split('.')[0]), 'wb') as f:
                f.write(encode_audio(audio))
        print(' - Done!')


def parse_data_to_json():
    data = {}

    name_list = read_name_list('name-list-mond.html')
    audio_list = read_audio_list('char-list-mond.html')
    for i in range(0, len(name_list)):
        data[name_list[i]] = audio_list[i]

    name_list = read_name_list('name-list-liyue.html')
    audio_list = read_audio_list('char-list-liyue.html')
    for i in range(0, len(name_list)):
        data[name_list[i]] = audio_list[i]

    with open('./data.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False))


if __name__ == '__main__':
    download_all_audio('name-list-mond.html', 'char-list-mond.html')
    download_all_audio('name-list-liyue.html', 'char-list-liyue.html')

    encode_all_audio(audio_dir='./audios', output_dir='./encoded')
