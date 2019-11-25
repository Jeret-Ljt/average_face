# -*- coding: utf-8 -*-
import urllib.request
import urllib.error
import time
import os
import json

from config import Config
http_url = r'https://api-cn.faceplusplus.com/facepp/v3/detect'
key = r"os2x76mV8-UjMTVZ5Y2vJsVSX2SGX4YX"
secret = r"jc5huvAfw9-CzgICpy2Hx7iIqNmHPKJH"

class Detect:
    def __init__(self, img_dir):
        self.img_dir = Config['img_dir']
        self.point_dir = img_dir + '_points'
    def run(self):
        if not os.path.exists(self.point_dir):
            os.mkdir(self.point_dir)

        for image in os.listdir(self.img_dir):

            filepath = os.path.join(self.img_dir, image)

            boundary = '----------%s' % hex(int(time.time() * 1000))
            data = []
            data.append('--%s' % boundary)
            data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_key')
            data.append(key)

            data.append('--%s' % boundary)
            data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_secret')
            data.append(secret)

            data.append('--%s' % boundary)
            fr = open(filepath, 'rb')
            data.append('Content-Disposition: form-data; name="%s"; filename=" "' % 'image_file')
            data.append('Content-Type: %s\r\n' % 'application/octet-stream')
            data.append(fr.read())
            fr.close()

            data.append('--%s' % boundary)
            data.append('Content-Disposition: form-data; name="%s"\r\n' % 'return_landmark')
            data.append('2')

            data.append('--%s' % boundary)
            data.append('Content-Disposition: form-data; name="%s"\r\n' % 'return_attributes')
            data.append(
                "gender,age,smiling,headpose,facequality,blur,eyestatus,emotion,ethnicity,beauty,mouthstatus,eyegaze,skinstatus")
            data.append('--%s--\r\n' % boundary)

            for i, d in enumerate(data):
                if isinstance(d, str):
                    data[i] = d.encode('utf-8')
            http_body = b'\r\n'.join(data)
            # build http request
            req = urllib.request.Request(url=http_url, data=http_body)
            # header
            req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)

            try:
                # post data to server
                resp = urllib.request.urlopen(req, timeout=5)
                # get response
                qrcont = resp.read().decode('utf-8')
                qrcont = json.loads(qrcont)

                #print(qrcont)
                # if you want to load as json, you should decode first,
                # for example: json.loads(qrount.decode('utf-8'))
                faceLandmark = qrcont["faces"][0]["landmark"]
                outfile = open(os.path.join(self.point_dir , image.split('.')[0] + '.json'), "w", encoding="utf-8")

                json.dump(faceLandmark, outfile)

            except urllib.error.HTTPError as e:
                print(e.read().decode('utf-8'))


if __name__ == "__main__":
    d = Detect('./test')
    d.run()
