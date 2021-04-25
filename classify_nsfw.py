#!/usr/bin/env python
import sys
import argparse
import tensorflow as tf
from model import OpenNsfwModel, InputType
from image_utils import create_tensorflow_image_loader
from image_utils import create_yahoo_image_loader
import numpy as np
from get_urls import get_urls
import pandas as pd
import requests
import prestodb
import time
import datetime
import pymysql



IMAGE_LOADER_TENSORFLOW = "tensorflow"
IMAGE_LOADER_YAHOO = "yahoo"



class NSFW:

    def __init__(self):
        self.fn_load_image = None
        self.sess = None
        self.model = OpenNsfwModel()
        self.data_path = None

    def session_run(self, source_type):
        with tf.compat.v1.Session() as self.sess:
            input_type = InputType[InputType.TENSOR.name.lower().upper()]
            self.model.build(
                weights_path='data/open_nsfw-weights.npy', input_type=input_type)

            if input_type == InputType.TENSOR:
                if IMAGE_LOADER_YAHOO == IMAGE_LOADER_TENSORFLOW:
                    self.fn_load_image = create_tensorflow_image_loader(
                        tf.Session(graph=tf.Graph()))
                else:
                    self.fn_load_image = create_yahoo_image_loader()
            elif input_type == InputType.BASE64_JPEG:
                import base64
                self.fn_load_image = lambda filename: np.array(
                    [base64.urlsafe_b64encode(open(filename, "rb").read())])

            self.sess.run(tf.compat.v1.global_variables_initializer())

            # ======
            data_txt = pd.read_table(
                self.data_path, sep='\t', header=None).values.tolist()
            data_result = []

            for d in data_txt:
                urls = get_urls(str(d[0]))
                # print('网站 = ', str(d[0]), '图片数量:', len(urls))
                if len(urls) > 0:
                    treu_sum = 0
                    for url in urls:
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'}
                        try:
                            res = requests.get(
                                url, headers=headers, timeout=20)
                        except:
                            continue
                        with open('img/text.jpg', 'wb') as f:
                            f.write(res.content)
                        f.close()

                        try:
                            image = self.fn_load_image('img/text.jpg')
                        except:
                            continue
                        predictions = self.sess.run(self.model.predictions, feed_dict={
                                                    self.model.input: image})
                        # print(float(predictions[0][1]), type(float(predictions[0][1])))
                        if float(predictions[0][1]) >= 0.8:
                            treu_sum += 1

                    if treu_sum / len(urls) >= 0.2:
                        data_result.append(str(d[0]))
                        sday = time.strftime(
                            '%Y-%m-%d', time.localtime(time.time()))
                        # print("INSERT INTO `pornographic_website_detection_zsf` (`sday`, `type`, `url`) VALUES ('" + sday + "', '"+source_type+"', '" + str(d[0]) + "' ,'" + str(d[1]) + "')")
                        # mysql_insert("INSERT INTO `pornographic_website_detection_zsf` (`sday`, `type`, `url`, `sum`) VALUES ('" +
                                        sday + "', '"+source_type+"', '" + str(d[0]) + "' ,'" + str(d[1]) + "')")
            
                    print('网站 = ', str(d[0]), '图片数量:', len(urls), '色情图片情况', treu_sum, len(urls) - treu_sum, '占比:', treu_sum / len(urls))

        return data_result

    def predict(self, input_file):
        image = self.fn_load_image(input_file)
        predictions = self.sess.run(self.model.predictions, feed_dict={
                                    self.model.input: image})

        #print("Results for '{}'".format(input_file))
        #print("\tSFW score:\t{}\n\tNSFW score:\t{}".format(*predictions[0]))
        print(float(predictions[0][1]), type(float(predictions[0][1])))
        if float(predictions[0][1]) >= 0.8:
            print("-------------")


if __name__ == "__main__":
    data = []

    print('===================文本长度：', len(data), '; ', len(data[0]), data[0])
    with open('测试网站.txt', 'w') as result:
        for i in data:
            result.write(str(i[0]) + '\t' + str(i[1]) + '\n')
    result.close()

    nsfw = NSFW()
    nsfw.data_path = '测试网站.txt'
    data_result = nsfw.session_run('测试网站')
