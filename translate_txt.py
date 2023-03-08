# -*- coding: utf-8 -*-
#
# Copyright 2019 Google LLC
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
from google.cloud import translate
from google.cloud import storage
from google.oauth2 import service_account
import os

""""""""" GCLOUD 연동 및 storage에 파일 올리기 """""""""
def upload_gcloud(args):
    KEY_PATH="C:/Users/8hoju/OneDrive/바탕 화면/College/인터루드/23.01 영상자막/divine-glazing-373902-f715b80326db.json"
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = KEY_PATH
    credentials = service_account.Credentials.from_service_account_file(KEY_PATH)

    bucket_name1 = 'my-first-bucket0123'
    bucket_name2 = 'my-second-bucket0123'
    source_file_name = '%s'%(args)
    destination_blob_name = '%s'%(args)

    """client = storage.Client.from_service_account_json(KEY_PATH)
    
    blobs = client.list_blobs(bucket_name2)
    for blob in blobs:
        blob.delete()"""
    
    storage_client = storage.Client()

    #버킷2 비우기
    bucket = storage_client.bucket(bucket_name2)
    blobs = bucket.list_blobs()
    for blob in blobs:
        blob.delete()
    print("bucket2를 비웠습니다.")

    #버킷1에 파일 업로드하기
    bucket = storage_client.bucket(bucket_name1)
    global txtname
    txtname=os.path.basename(args)
    blob = bucket.blob(txtname)

    blob.upload_from_filename(destination_blob_name)

def get_supported_languages(project_id):
    """Getting a list of supported language codes"""

    client = translate.TranslationServiceClient()
    parent = client.location_path(project_id, "global")
    response = client.get_supported_languages(parent=parent)

    # List language codes of supported languages
    print('Supported Languages: ', end='')
    for language in response.languages:
        print(u"{} ".format(language.language_code), end='')
    print("\n")

def batch_translate_text(input_uri, output_uri, project_id, location, source_lang, target_lang):
    from time import sleep
    # call batch translate against orig.txt

    client = translate.TranslationServiceClient()

    target_language_codes = target_lang.split(",")
    gcs_source = {"input_uri": input_uri}
    mime_type = "text/plain"
    input_configs_element = {"gcs_source": gcs_source, "mime_type": mime_type}
    input_configs = [input_configs_element]
    gcs_destination = {"output_uri_prefix": output_uri}
    output_config = {"gcs_destination": gcs_destination}
    parent = f"projects/{project_id}/locations/{location}"

    operation = client.batch_translate_text(
        request={
            "parent": parent,
            "source_language_code": source_lang,
            "target_language_codes": target_language_codes,
            "input_configs": input_configs,
            "output_config": output_config,
        })

    # Initial delay
    total_wait_secs = 90
    print(f"Waiting for operation to complete... {total_wait_secs:.0f} secs")

    delay_secs = 10
    sleep(90)
    while not operation.done():
        # Exponential backoff
        delay_secs *= 1.1
        total_wait_secs += delay_secs
        print(f"Checking again in: {delay_secs:.0f} seconds | total wait: {total_wait_secs:.0f} secs")
        sleep(delay_secs)

    response = operation.result()
    print(u"Total Characters: {}".format(response.total_characters))
    print(u"Translated Characters: {}".format(response.translated_characters))

def download_gcloud(args,lang):
    from pathlib import Path
    """"""""" GCLOUD 연동 및 storage에 파일 다운받기"""""""""
    KEY_PATH="C:/Users/8hoju/OneDrive/바탕 화면/College/인터루드/23.01 영상자막/divine-glazing-373902-f715b80326db.json"
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = KEY_PATH
    credentials = service_account.Credentials.from_service_account_file(KEY_PATH)

    bucket_name1 = 'my-first-bucket0123'
    bucket_name2 = 'my-second-bucket0123'
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name2)
    path_dir=os.path.dirname(args) 
    txt=(txtname).replace(".txt","")
    list_files_to_download = [bucket_name1+"_"+txt+"_"+lang+"_translations.txt", 'index.csv'] 

    for file_to_download in list_files_to_download:
        blob = bucket.blob(file_to_download) #다운로드할 파일명이 들어가야함 
        blob.download_to_filename(f'{path_dir}/{blob.name}') #다운로드할 경로명

def main(srt,lang):
    import srt2txt
    srt2txt.main(srt) 
    upload_gcloud(srt2txt.txt_file)
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project_id",
        type=str,
        default="divine-glazing-373902", #자기 프로젝트 id로 바꿔주기
    )
    parser.add_argument(
        "--location",
        type=str,
        default='us-central1',
    )
    parser.add_argument(
        "--source_lang",
        type=str,
        default="ko-KR",#firstlang ..
    )
    parser.add_argument(
        "--target_lang",
        type=str,
        default=lang,
    )
    parser.add_argument(
        "--input_uri",
        type=str,
        default="gs://my-first-bucket0123/%s"%(txtname),
    )
    parser.add_argument(
        "--output_uri",
        type=str,
        default="gs://my-second-bucket0123/" 
    )
    args = parser.parse_args()

    batch_translate_text(args.input_uri, args.output_uri, args.project_id,
                         args.location, args.source_lang, args.target_lang)

    download_gcloud(srt2txt.txt_file,args.target_lang) #여기 수정함 
    print("번역 작업이 완료되었습니다.")

if __name__ == "__main__":
    main("C:/Users/8hoju/OneDrive/바탕 화면/College/인터루드/23.01 영상자막/영상example/1분 동안 세계에서 일어나는 일들!!.srt", "zh-CN")