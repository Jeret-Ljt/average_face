import cv2
import numpy as np

def warpTriangle(img1, img2, t1, t2, times = 1):

    r1 = cv2.boundingRect(np.float32([t1]))
    r2 = cv2.boundingRect(np.float32([t2]))  #find the bounding rectangle to conver the triangle


    t1_off = [[t1[i][0] - r1[0], t1[i][1] - r1[1]] for i in range(0, 3)]
    t2_off = [[t2[i][0] - r2[0], t2[i][1] - r2[1]] for i in range(0, 3)]   # Offset points by left top corner of the respective rectangles

    img1Rect = img1[r1[1]:r1[1] + r1[3], r1[0]:r1[0] + r1[2]] #cut the piece from img1

    _, img2Rect = applyAffineTransform(img1Rect, t1_off, t2_off, (r2[2], r2[3]))

    mask = np.zeros((r2[3], r2[2], 3), dtype=np.float32)     #create a mask

    cv2.fillConvexPoly(mask, np.int32(t2_off), (1.0, 1.0, 1.0))


    img2Rect = img2Rect * mask

    #img2[r2[1]:r2[1] + r2[3], r2[0]:r2[0] + r2[2]] *= ([1, 1, 1] - mask)  #this step is crucial! avoid to be overpuls in the triangular edges
    img2[r2[1]:r2[1] + r2[3], r2[0]:r2[0] + r2[2]] += img2Rect * times



def calculateDelaunayTriangles(rect, points):
    subdiv = cv2.Subdiv2D(rect) # Create subdiv
    #print(points)
    for p in points:
        subdiv.insert((p[0], p[1]))  # Insert points into subdiv

    triangleList = subdiv.getTriangleList()  #get the information of triangle dividing
    delaunayTri = [] #find which point that the triangle point refers to

    for t in triangleList:
        ind = []
        for j in range(0, 3):
            for k in range(0, len(points)):
                if abs(t[2 * j] - points[k][0]) < 0.5 and abs(t[2 * j + 1] - points[k][1]) < 0.5:
                    ind.append(k)
                    break
        if len(ind) == 3:
            delaunayTri.append(ind)

    return delaunayTri

def applyAffineTransform(src, srcTri, dstTri, size):
    matrix = cv2.getAffineTransform(np.float32(srcTri), np.float32(dstTri))
    dst = cv2.warpAffine(src, matrix, size, borderMode=cv2.BORDER_REPLICATE) #the borderMode need to be set carefully. it is very vital!

    return matrix, dst