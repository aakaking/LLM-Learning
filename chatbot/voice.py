from openai import OpenAI
import re
import uuid
from pydub import AudioSegment
import shutil
import os
from IPython.display import clear_output
from IPython.display import Audio
import uuid

Language = "Chinese" # @param ['English']
voice_name = "zh-CN-XiaoxiaoNeural"# @param["en-US-AriaNeural",'zh-CN-XiaoxiaoNeural','zh-CN-XiaoyiNeural']
speed = 1  # @param {type: "number"}

if not os.path.exists("./content/audio"):
    os.mkdir("./content/audio")


#@title Edge TTS
def calculate_rate_string(input_value):
    rate = (input_value - 1) * 100
    sign = '+' if input_value >= 1 else '-'
    return f"{sign}{abs(int(rate))}"

def make_chunks(input_text, language):
    language="Chinese"
    if language == "Chinese":
      temp_list = input_text.strip().split(".")
      filtered_list = [element.strip() + '.' for element in temp_list[:-1] if element.strip() and element.strip() != "'" and element.strip() != '"']
      if temp_list[-1].strip():
          filtered_list.append(temp_list[-1].strip())
      return filtered_list

def tts_file_name(text):
    if text.endswith("."):
        text = text[:-1]
    text = text.lower()
    text = text.strip()
    text = text.replace(" ","_")
    truncated_text = text[:25] if len(text) > 25 else text if len(text) > 0 else "empty"
    random_string = uuid.uuid4().hex[:8].upper()
    file_name = f"./content/edge_tts_voice/{truncated_text}_{random_string}.mp3"
    return file_name

def merge_audio_files(audio_paths, output_path):
    # Initialize an empty AudioSegment
    merged_audio = AudioSegment.silent(duration=0)

    # Iterate through each audio file path
    for audio_path in audio_paths:
        # Load the audio file using Pydub
        audio = AudioSegment.from_file(audio_path)

        # Append the current audio file to the merged_audio
        merged_audio += audio

    # Export the merged audio to the specified output path
    merged_audio.export(output_path, format="mp3")

def edge_free_tts(chunks_list,speed,voice_name,save_path):
  # print(chunks_list)
  if len(chunks_list)>1:
    chunk_audio_list=[]
    if os.path.exists("./content/edge_tts_voice"):
      shutil.rmtree("./content/edge_tts_voice")
    os.mkdir("./content/edge_tts_voice")
    k=1
    for i in chunks_list:
      print(i)
      edge_command=f'edge-tts  --rate={calculate_rate_string(speed)}% --voice {voice_name} --text "{i}" --write-media ./content/edge_tts_voice/{k}.mp3'
      print(edge_command)
      var1=os.system(edge_command)
      if var1==0:
        pass
      else:
        print(f"Failed: {i}")
      chunk_audio_list.append(f"./content/edge_tts_voice/{k}.mp3")
      k+=1
    # print(chunk_audio_list)
    merge_audio_files(chunk_audio_list, save_path)
  else:
    edge_command=f'edge-tts  --rate={calculate_rate_string(speed)}% --voice {voice_name} --text "{chunks_list[0]}" --write-media {save_path}'
    print(edge_command)
    var2=os.system(edge_command)
    if var2==0:
      pass
    else:
      print(f"Failed: {chunks_list[0]}")
  return save_path

def random_audio_name_generate():
  random_uuid = uuid.uuid4()
  audio_extension = ".mp3"
  random_audio_name = str(random_uuid)[:8] + audio_extension
  return random_audio_name

def talk(input_text):
  global translate_text_flag,Language,speed,voice_name
  if len(input_text)>=600:
    long_sentence = True
  else:
    long_sentence = False

  if long_sentence==True and translate_text_flag==True:
    chunks_list=make_chunks(input_text,Language)
  elif long_sentence==True and translate_text_flag==False:
    chunks_list=make_chunks(input_text,"Chinese")
  else:
    chunks_list=[input_text]
  save_path="./content/audio/"+random_audio_name_generate()
  edge_save_path=edge_free_tts(chunks_list,speed,voice_name,save_path)
  return edge_save_path

def convert_to_text(audio_path):
    import whisper
    select_model ="base" # ['tiny', 'base']
    whisper_model = whisper.load_model(select_model)
    result = whisper_model.transcribe(audio_path,word_timestamps=True,fp16=False,language='Chinese')
    with open('scan.txt', 'w') as file:
        file.write(str(result))
    return result["text"]


if __name__ == "__main__":
    text = '这是一个演示'  # @param {type: "string"}
    Language = "Chinese" # @param ['English']
    voice_name ="zh-CN-XiaoxiaoNeural"# @param["en-US-AriaNeural",'zh-CN-XiaoxiaoNeural','zh-CN-XiaoyiNeural']
    speed = 1  # @param {type: "number"}
    edge_save_path=talk(text)
    Audio(edge_save_path, autoplay=True)
    