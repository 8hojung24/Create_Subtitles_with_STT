# -*- coding: utf-8 -*-
#
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import srt

def load_srt(filename):
    # 원본 srt파일 읽어들임
    # srt 파일을 자막 list로 
    print("Loading {}".format(filename))
    with open(filename,encoding='utf8') as f:
        text = f.read()
    return list(srt.parse(text))

def process_translations(subs, indexfile):
    # index.csv에서 올려준 파일명, 번역한 언어, 다운받은 파일명 확인 

    print("Updating subtitles for each translated language")
    with open(indexfile,encoding='utf8') as f:
        lines = f.readlines()
    # copy orig subs list and replace content for each line
    for line in lines:
        index_list = line.split(",")
        lang = index_list[1]
        langfile = index_list[2].split("/")[-1]
        lang_subs = update_srt(lang, langfile, subs)
        filename=write_srt(lang, lang_subs)
    return filename 


def update_srt(lang, langfile, subs):
    # change subtitles' content to translated lines
    langfile=path_dir+'/'+langfile 
    
    with open(langfile,encoding='utf8') as f:
        lines = f.readlines()
    i = 0
    for line in lines:
        subs[i].content = line
        i += 1
    return subs


def write_srt(lang, lang_subs):
    filename = path_dir+'/'+srtname +"_"+lang+ ".srt"  

    f = open(filename, "w",encoding='utf8')
    f.write(srt.compose(lang_subs, strict=True))
    f.close()
    print("Wrote SRT file {}".format(filename))
    return filename


def main(firstsrt):
    import argparse
    import os
    global path_dir
    path_dir=os.path.dirname(firstsrt) 

    global srtname
    srtname=os.path.basename(firstsrt)
    srtname=srtname.replace(".srt","")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--srt",
        type=str,
        default=firstsrt, #번역 전 srt파일 
    )
    parser.add_argument(
        "--index",
        type=str,
        default=path_dir+"/index.csv", 
    )
    args = parser.parse_args()

    subs = load_srt(args.srt)

    global newsrtname
    newsrtname=process_translations(subs, args.index)


if __name__ == "__main__":
    main()