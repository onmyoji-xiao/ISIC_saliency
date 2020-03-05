from skimage.segmentation import slic
from skimage import io, transform
import cv2
import csv
from Compute_region import Vex, color_to12, changeo1_to_o2, computeSk

csvFile = open("X:/ISIC-data2017/train.csv", "r")
reader = csv.reader(csvFile)
for item in reader:
    """
    1.read image
    """
    img_path = "X:/ISIC-data2017/train/" + item[0] + ".jpg"
    origin_img = cv2.imread(img_path)  # BGR
    ih = origin_img.shape[0]
    iw = origin_img.shape[1]

    ratei = float(ih / iw)
    if iw > 200:
        nw = 200
        nh = int(nw * ratei)
    else:
        nw = iw
        nh = ih
    origin_img = cv2.resize(origin_img, (nw, nh), interpolation=cv2.INTER_AREA)

    img = io.imread(img_path)
    img = transform.resize(img, (nh, nw), mode="constant")
    segments = slic(img, n_segments=50, compactness=10)
    # print(segments)
    width = segments.shape[1]
    height = segments.shape[0]

    """
    Put the segmented areas into clist
    """
    clist = list()
    for k in range(58):
        temp_list = []
        clist.append(temp_list)
    for i in range(height):
        for j in range(width):
            v = Vex(i, j)  # i行j列
            a = segments[i, j]
            clist[a].append(v)

    """
    Split channel
    """
    (b_img, g_img, r_img) = cv2.split(origin_img)
    # 高斯模糊
    b_img = cv2.GaussianBlur(b_img, (5, 5), 0.8)
    g_img = cv2.GaussianBlur(g_img, (5, 5), 0.8)
    r_img = cv2.GaussianBlur(r_img, (5, 5), 0.8)

    """
    Gray pixels to border color
    """

    temp_b = 255
    temp_g = 255
    temp_r = 255

    for i in range(20, height):
        for j in range(20, width):
            if b_img[i, j] > 100 and g_img[i, j] > 100 and r_img[i, j] > 100:
                temp_b = b_img[i, j]
                temp_g = g_img[i, j]
                temp_r = r_img[i, j]
                print(temp_b, temp_g, temp_r)
                break
        if temp_b != 255:
            break

    if temp_b != 255:
        for i in range(nh):
            for j in range(nw):
                if abs(int(b_img[i, j]) - int(g_img[i, j])) < 10 and abs(int(b_img[i, j]) - int(r_img[i, j])) < 10 \
                        or (b_img[i, j] < 60 and g_img[i, j] < 60 and r_img[i, j] < 90):
                    if j < 40 or j > nw - 40 or i < 40 or i > nh - 40:
                        b_img[i, j] = temp_b
                        g_img[i, j] = temp_g
                        r_img[i, j] = temp_r

    img2 = cv2.merge([b_img, g_img, r_img])

    "extract salient areas"

    "Reduce the color to 12*12*12"
    b_img = color_to12(b_img, width, height)
    g_img = color_to12(g_img, width, height)
    r_img = color_to12(r_img, width, height)

    """
   Count the number of colors
    """
    colorcount = [[[0 for _ in range(12)] for _ in range(12)] for _ in range(12)]
    colorlist = list()
    for i in range(height):
        for j in range(width):
            t1 = int(b_img[i, j] / 22)
            t2 = int(g_img[i, j] / 22)
            t3 = int(r_img[i, j] / 22)
            colorcount[t1][t2][t3] += 1
            if colorcount[t1][t2][t3] == 1:
                colorlist.append((t1, t2, t3))
    """
    Remove the color less than 0.005, and change to the nearest color
    """
    o = 0
    while o < len(colorlist):
        t1, t2, t3 = colorlist[o]
        cn = colorcount[t1][t2][t3]
        if float(cn) / (height * width) < 0.005:
            if o > 0:
                changeo1_to_o2(o, o - 1, colorlist, colorcount, height, width, b_img, g_img, r_img)
            else:
                changeo1_to_o2(o, o + 1, colorlist, colorcount, height, width, b_img, g_img, r_img)
            o = o - 1
        o = o + 1

    """
    Compute the region saliency S(rk)=∑w(ri)Dr(rk,ri) 
    """
    skl = list()
    skmin = 255
    skmax = 0
    for ri in range(len(clist)):
        a = 1
        sri = computeSk(ri, clist, width, height, b_img, g_img, r_img)
        rv1 = clist[ri]
        for i in range(len(rv1)):
            rx = rv1[i].x
            ry = rv1[i].y
            if abs(int(b_img[rx, ry]) - int(g_img[rx, ry])) < 10 and abs(
                    int(b_img[rx, ry]) - int(r_img[rx, ry])) < 10 and \
                    b_img[rx, ry] > 200:
                a = 0.3
            if rx < 30 or rx > height - 10 or ry < 40 or ry > width - 40:
                a = 0.3
            if rx < 1 and ry < 1:
                a = 0.3
            if rx < 1 and ry > width - 2:
                a = 0.3
            if rx > height - 2 and ry < 1:
                a = 0.3
            if rx > height - 2 and ry > width - 2:
                a = 0.3

        sri = float(sri * a)
        if sri > skmax:
            skmax = sri
        if sri < skmin and sri != 0:
            skmin = sri
        skl.append(sri)

    result_img = b_img
    sk_img = g_img
    ratek = float(255 / (skmax - skmin))

    for ri in range(len(clist)):
        sri = skl[ri]
        sk_vlist = clist[ri]
        if sri > skmin:
            relsri = (sri - skmin) * ratek
        else:
            relsri = 0
        rv1 = clist[ri]
        for i in range(len(rv1)):
            rx, ry = rv1[i].x, rv1[i].y
            if rx < 10 or rx > height - 10 or ry < 10 or ry > width - 10:
                relsri = relsri

        for i in range(len(sk_vlist)):
            sk_img[sk_vlist[i].x, sk_vlist[i].y] = relsri
            if relsri > 160:
                result_img[sk_vlist[i].x, sk_vlist[i].y] = 255
            else:
                result_img[sk_vlist[i].x, sk_vlist[i].y] = 0
        # print(ri, sri)

    result_img = cv2.resize(result_img, (iw, ih), interpolation=cv2.INTER_AREA)
    cv2.imwrite("X:/ISIC-data2017/newsal/train/" + item[0] + ".jpg", result_img)
    # cv2.imshow('_img', img2)
    # cv2.imshow('sk_img', sk_img)
    # cv2.imshow('rel_img', result_img)
    # cv2.waitKey()
    # cv2.destroyAllWindows()
