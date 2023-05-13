import yaml
from yacs.config import CfgNode
import json
from pathlib import Path
import soundfile as sf
import os
import client
import server
import threading
import socket

from paddlespeech.t2s.exps.syn_utils import am_to_static
from paddlespeech.t2s.exps.syn_utils import get_am_inference
from paddlespeech.t2s.exps.syn_utils import get_am_output
from paddlespeech.t2s.exps.syn_utils import get_frontend
from paddlespeech.t2s.exps.syn_utils import get_predictor
from paddlespeech.t2s.exps.syn_utils import get_voc_output


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    # print(s.getsockname()[0])
    return s.getsockname()[0]


class texttovoice:

    def __init__(self):
        # 在其他环境中，记得修改下面这两个变量的路径
        self.am_inference_dir = "./model/spka"
        #am_inference_dir = os.path.join("E:/诸葛大韦的大三/语音识别/spka")
        #am_inference_dir = os.path.join("E:/诸葛大韦的大三/语音识别", spka)
        self.voc_inference_dir = "./vcoder/pwgan_aishell3_static_1.1.0"
        # voc_inference_dir = "F:\DIGITAL\pwgan_aishell3_static_1.1.0"  # 这里以 pwgan_aishell3 为例子

        # 音频生成的路径，修改成你音频想要保存的路径
        self.wav_output_dir = "./audio"

        # 选择设备[gpu / cpu]，这里以GPU为例子，
        self.device = "gpu"

        # 想要生成的文本和对应文件名

        # frontend
        self.frontend = get_frontend(
            lang="mix",
            phones_dict=os.path.join(
                self.am_inference_dir, "phone_id_map.txt"),
            tones_dict=None
        )

        # am_predictor
        self.am_predictor = get_predictor(
            model_dir=self.am_inference_dir,
            model_file="fastspeech2_mix" + ".pdmodel",
            params_file="fastspeech2_mix" + ".pdiparams",
            device=self.device)

        # voc_predictor
        self.voc_predictor = get_predictor(
            model_dir=self.voc_inference_dir,
            model_file="pwgan_aishell3" + ".pdmodel",
            params_file="pwgan_aishell3" + ".pdiparams",
            # model_file="pwgan_aishell3" + ".pdmodel",    # 这里以 pwgan_aishell3 为例子，其它模型记得修改此处模型名称
            #params_file="pwgan_aishell3" + ".pdiparams",
            device=self.device)

        self.output_dir = Path(self.wav_output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.c = client.client("192.168.167.179", 8080)
        print(
            "------------------------------------------------------------------------------")

    def process(self, text_dict):
        sentences = list(text_dict.items())

        merge_sentences = True
        fs = 24000
        for utt_id, sentence in sentences:
            am_output_data = get_am_output(
                input=sentence,
                am_predictor=self.am_predictor,
                am="fastspeech2_mix",
                frontend=self.frontend,
                lang="mix",
                merge_sentences=merge_sentences,
                speaker_dict=os.path.join(
                    self.am_inference_dir, "phone_id_map.txt"),
                spk_id=0, )
            wav = get_voc_output(
                voc_predictor=self.voc_predictor, input=am_output_data)
            # print(type(wav))
            # print(wav.shape)
            # print(wav.ndim)
            stream_list = wav.tolist()
            stream_list_second = []

            for i in stream_list:
                # print(i)
                stream_list_second.append(i[0])
            # print(stream_list_second)
            # 保存文件
            # while True:
            #     self.c.send_data(data[1:-1])
            data = str(stream_list_second)
            print(len(data))
            # print(data)
            self.c.send_data(data[1:-1])
            Note = open('test.txt', mode='w+')
            Note.write(str(stream_list_second))
            sf.write(self.output_dir / (utt_id + ".wav"), wav, samplerate=fs)

    def start(self):
        print("Success")
        while True:
            # os.system("cls")
            i = input()
            dict = {}
            dict["1"] = i
            self.process(dict)

    def s(self):
        ip = get_ip()
        host = 8080
        self.server = server.server(ip, host)


if __name__ == "__main__":

    # text_dict = {
    #     "1": "今天天气真不错，欢迎和我一起玩。",
    #     "2": "我认为跑步给我的身体带来了健康。"
    # }
    obj = texttovoice()
    print("ok")

    # obj.process(text_dict)
    obj.start()
