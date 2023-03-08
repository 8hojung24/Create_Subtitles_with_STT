# from pytube import YouTube
import ffmpeg
from google.cloud import storage
from google.oauth2 import service_account
from google.cloud import speech
import srt
import os

""""""""" GCLOUD 연동 및 storage에 파일 올리기 """""""""
def upload_gcloud(args):
    KEY_PATH="C:\\Users\\8hoju\\OneDrive\\바탕 화면\\College\\인터루드\\23.01 영상자막\\divine-glazing-373902-f715b80326db.json"
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = KEY_PATH
    credentials = service_account.Credentials.from_service_account_file(KEY_PATH)

    bucket_name1 = 'my-first-bucket0123'
    bucket_name2 = 'my-second-bucket0123'
    source_file_name = '%s'%(args)
    destination_blob_name = '%s'%(args)

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name1)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)


""""""""" GCloud Speech 에서 wav 를 srt,txt로 변환 """""""""
def long_running_recognize(args):
    """
    Transcribe long audio file from Cloud Storage using asynchronous speech
    recognition

    Args:
      storage_uri URI for audio file in GCS, e.g. gs://[BUCKET]/[FILE]
    """

    print("Transcribing {} ...".format(args.storage_uri))
    client = speech.SpeechClient()

    # Encoding of audio data sent.
    operation = client.long_running_recognize(
        config=
        {
            "enable_word_time_offsets": True,
            "enable_automatic_punctuation": True,
            "sample_rate_hertz": args.sample_rate_hertz,
            "language_code": args.language_code,
            "audio_channel_count": args.audio_channel_count,
            "encoding": args.encoding,
        },
        audio={"uri": args.storage_uri},
    )
    response = operation.result()

    subs = []

    for result in response.results:
        # First alternative is the most probable result
        subs = break_sentences(args, subs, result.alternatives[0])

    print("Transcribing finished")
    return subs


def break_sentences(args, subs, alternative):
    firstword = True
    charcount = 0
    idx = len(subs) + 1
    content = ""

    for w in alternative.words:
        if firstword:
            # first word in sentence, record start time
            start = w.start_time

        charcount += len(w.word)
        content += " " + w.word.strip()

        if ("." in w.word or "!" in w.word or "?" in w.word or
                charcount > args.max_chars or
                ("," in w.word and not firstword)):
            # break sentence at: . ! ? or line length exceeded
            # also break if , and not first word
            subs.append(srt.Subtitle(index=idx,
                                     start=start,
                                     end=w.end_time,
                                     content=srt.make_legal_content(content)))
            firstword = True
            idx += 1
            content = ""
            charcount = 0
        else:
            firstword = False
    return subs


def write_srt(args, subs):
    srt_file = args.out_file + ".srt"
    print("Writing {} subtitles to: {}".format(args.language_code, srt_file))
    f = open(srt_file, 'w', encoding = 'utf8')
    f.writelines(srt.compose(subs))
    f.close()
    return


def write_txt(args, subs):
    txt_file = args.out_file + ".txt"
    print("Writing text to: {}".format(txt_file))
    f = open(txt_file, 'w', encoding = 'utf8')
    for s in subs:
        f.write(s.content.strip() + "\n")
    f.close()
    return


def main(wavfile):
    print("main2의 %s"%wavfile)
    upload_gcloud(wavfile)
    import argparse
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--storage_uri",
        type=str,
        default="gs://my-first-bucket0123/%s"%(wavfile),
    )
    parser.add_argument(
        "--language_code",
        type=str,
        default="ko-KR",
    )
    parser.add_argument(
        "--sample_rate_hertz",
        type=int,
        default=16000,
    )
    parser.add_argument(
        "--out_file",
        type=str,
        default="%s"%((wavfile.rstrip('.wav'))),
    )
    parser.add_argument(
        "--max_chars",
        type=int,
        default=40,
    )
    parser.add_argument(
        "--encoding",
        type=str,
        default='LINEAR16'
    )
    parser.add_argument(
        "--audio_channel_count",
        type=int,
        default=1
    )
    args = parser.parse_args()

    subs = long_running_recognize(args)
    write_srt(args, subs)
    write_txt(args, subs)