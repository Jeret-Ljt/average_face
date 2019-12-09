
import cv2
import numpy as np
from faceplusplus_sdk import Detect
from config import Config
import sys
import json
import os
import utils


def readPoints(path):
    pointsArray = []
    json_array = []
    eliminated_index = []

    listdir = os.listdir(path)
    listdir.sort()
    for txtFile in listdir:
        #print(txtFile)
        points = []
        with open(path + txtFile) as json_file:
            data = json.load(json_file)


        for key, item in data.items():
            points.append([item['x'], item['y']]) #load the json from the file
            if key in Config['eliminated']:
                eliminated_index.append(len(points) - 1)
        pointsArray.append(points)  #put the [x,y] into the points array
        json_array.append(data)

    return eliminated_index + [len(pointsArray[0]) + i for i in range(8)], pointsArray, json_array  #return two formats of the points

def readImages(path):
    imagesArray = []
    listdir = os.listdir(path)
    listdir.sort()

    BG = 0
    for imageFile in listdir:
        #print(imageFile)

        if imageFile == '.DS_Store':
            continue
        if imageFile == Config['background']:
            BG = len(imagesArray)
        img = cv2.imread(os.path.join(path, imageFile))
        img = np.float32(img) / 255.0
        imagesArray.append(img)
    return BG, imagesArray


def Normalization(w, h, allPoints, allPoints_json, images):
    imagesNorm = []
    pointsNorm = []  #the normalized points and images

    boundaryPts = np.array([
        (0, 0),
        (w / 2, 0),
        (w - 1, 0),
        (w - 1, h / 2),
        (w - 1, h - 1),
        (w / 2, h - 1),
        (0, h - 1),
        (0, h / 2)
    ]
    )

    pointsAvg = np.array([[0, 0]] * len(allPoints[0]))  #an array representing the final average landmarks

    eyecorner_chin_Dst = [
        [0.3 * w, h / 2],
        [0.7 * w, h / 2],
        [0.5 * w, h * 0.9]
    ] #the final locations of eye conners and chin


    for i, image in enumerate(images):

        points = allPoints[i]
        #the two eye corners from the original image
        eyecorner_chin_Src = [allPoints_json[i]['left_eye_left_corner'], allPoints_json[i]['right_eye_right_corner'], allPoints_json[i]['contour_chin']]
        eyecorner_chin_Src = [[p['x'], p['y']] for p in eyecorner_chin_Src]



        tform, img = utils.applyAffineTransform(image, eyecorner_chin_Src, eyecorner_chin_Dst, (w, h))  # transform the original image


        points = np.reshape(cv2.transform(np.reshape(np.array(points), (-1, 1, 2)), tform), (-1, 2))  # transform the points
        points = np.maximum(points, 0)
        points = np.minimum(points, [w - 1, h - 1])


        pointsAvg += points  # contribute to the average points
        pointsNorm.append(np.append(points, boundaryPts, axis = 0))

        imagesNorm.append(img)

    pointsAvg = pointsAvg / len(images)


    return np.append(pointsAvg, boundaryPts, axis = 0), pointsNorm, imagesNorm

def Trianglar_affine(BG, w, h, pointsAvg, pointsNorm, imagesNorm, eliminated_index):
    rect = (0, 0, w, h)
    dt = utils.calculateDelaunayTriangles(rect, np.array(pointsAvg))  # the Delaunay Triangles dividing

    # the final output image
    output_bg = np.zeros((h, w, 3), np.float32())


    for j in range(0, len(dt)):
        if dt[j][0] in eliminated_index or dt[j][1] in eliminated_index or dt[j][2] in eliminated_index:
            tri_in = [pointsNorm[BG][dt[j][k]] for k in range(0, 3)]
            tri_out = [pointsAvg[dt[j][k]] for k in range(0, 3)]
            utils.warpTriangle(imagesNorm[BG], output_bg, tri_in, tri_out)

    output = np.zeros((h, w, 3), np.float32())
    for i in range(0, len(imagesNorm)):
        img = output_bg
        for j in range(0, len(dt)):
            if dt[j][0] in eliminated_index or dt[j][1] in eliminated_index or dt[j][2] in eliminated_index:
                continue
            tri_in = [pointsNorm[i][dt[j][k]] for k in range(0, 3)]
            tri_out = [pointsAvg[dt[j][k]] for k in range(0, 3)]
            utils.warpTriangle(imagesNorm[i], img, tri_in, tri_out)
        output = output + img / len(imagesNorm)

    return output
def main():
    img_dir = Config['img_dir']
    point_dir = img_dir + '_points'
    result_dir = img_dir + '_result'

    Detect(img_dir).run()

    w = Config['w'] # the width of the final picture
    h = Config['h'] # the height of the final picture
    eliminated_index, allPoints, allPoints_json = readPoints(point_dir + '/')
    BG, images = readImages(img_dir + '/')
    #print(len(allPoints[0]))

    pointsAvg, pointsNorm, imagesNorm = Normalization(w, h, allPoints, allPoints_json, images)

    output = Trianglar_affine(BG, w, h, pointsAvg, pointsNorm, imagesNorm, eliminated_index)

    #cv2.imshow('image', output)
    #cv2.waitKey(0)


    final_output = np.zeros((h, (len(images) + 1) * (w + 5), 3), dtype = np.float32())

    for i, image in enumerate(imagesNorm):
        final_output[:, i * (w + 5) : i * (w + 5) + w, :] = image
        #cv2.imshow('image', final_output[:, i * (w + 5) : i * (w + 5) + w, :])
        #cv2.waitKey(0)
    final_output[:, len(images) * (w + 5) : len(images) * (w + 5) + w, :] = output

    if not os.path.exists(result_dir):
        os.mkdir(result_dir)

    cv2.imwrite(os.path.join(result_dir, 'result.jpg'), final_output * 255)

    cv2.imshow('image', final_output)
    cv2.waitKey(0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('interrupt')
        sys.exit(1)
