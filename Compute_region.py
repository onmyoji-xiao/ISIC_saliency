import math

class Vex(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y


def color_to12(r_img, height, width):
    for i in range(height):
        for j in range(width):
            ti = int(r_img[i, j] / 22) * 22 + 13
            r_img[i, j] = ti
    return r_img


def changeo1_to_o2(o1, o2, colorlist,colorcount,height,width,b_img,g_img,r_img):
    ch1i, ch2i, ch3i = colorlist[o1]
    ch1j, ch2j, ch3j = colorlist[o2]
    ch_n = colorcount[ch1i][ch2i][ch3i]
    colorcount[ch1j][ch2j][ch3j] += ch_n
    colorcount[ch1i][ch2i][ch3i] = 0
    for chi in range(height):
        for chj in range(width):
            cht1 = int(b_img[chi, chj] / 22)
            cht2 = int(g_img[chi, chj] / 22)
            cht3 = int(r_img[chi, chj] / 22)
            if cht1 == ch1i and cht2 == ch2i and cht3 == ch3i:
                b_img[chi, chj] = ch1j * 22 + 13
                g_img[chi, chj] = ch2j * 22 + 13
                r_img[chi, chj] = ch3j * 22 + 13
    del colorlist[o1]


def computeDr(r1, r2,clist,b_img,g_img,r_img):
    rv1 = clist[r1]
    rv2 = clist[r2]
    rcolor1 = [[[0 for _ in range(12)] for _ in range(12)] for _ in range(12)]
    rcolor2 = [[[0 for _ in range(12)] for _ in range(12)] for _ in range(12)]
    rclist1 = list()
    rclist2 = list()
    for i in range(len(rv1)):
        rx = rv1[i].x
        ry = rv1[i].y
        rt1 = int(b_img[rx, ry] / 22)
        rt2 = int(g_img[rx, ry] / 22)
        rt3 = int(r_img[rx, ry] / 22)
        rcolor1[rt1][rt2][rt3] += 1
        if rcolor1[rt1][rt2][rt3] == 1:
            rclist1.append((rt1, rt2, rt3))

    for i in range(len(rv2)):
        rx = rv2[i].x
        ry = rv2[i].y
        rt1 = int(b_img[rx, ry] / 22)
        rt2 = int(g_img[rx, ry] / 22)
        rt3 = int(r_img[rx, ry] / 22)
        rcolor2[rt1][rt2][rt3] += 1
        if rcolor2[rt1][rt2][rt3] == 1:
            rclist2.append((rt1, rt2, rt3))
    dr = 0.
    # print("rclist1-----------")
    # print(rclist1)
    # print("rclist2-----------")
    # print(rclist2)
    for i1 in range(len(rclist1)):
        ra1, ra2, ra3 = rclist1[i1]
        for i2 in range(len(rclist2)):
            rb1, rb2, rb3 = rclist2[i2]
            fr1 = float(rcolor1[ra1][ra2][ra3] / len(rv1))
            fr2 = float(rcolor2[rb1][rb2][rb3] / len(rv2))
            # print(fr1, fr2)
            dr += float(fr1 * fr2 * 22 * math.sqrt(
                (ra1 - rb1) * (ra1 - rb1) + (ra2 - rb2) * (ra2 - rb2) + (ra3 - rb3) * (ra3 - rb3)))
    # print(dr)
    return dr


def computeSk(ck,clist,width,height,b_img,g_img,r_img):
    sk = 0.
    for k in range(len(clist)):
        if k != ck:
            sk += float(len(clist[k]) / (width * height) * computeDr(ck, k,b_img,g_img,r_img))
    return sk
