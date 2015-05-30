__author__ = 'gulliver - Radek Simkanic - SIM0094'

import cv2
import numpy as np

def different_pixels(first_img, second_img, mode = 0):
    height, width = first_img.shape[:2]
    result = np.zeros((height, width, 3), np.uint8)
    for r in xrange(0, height):
        for c in xrange(0, width):
            for ch in [0, 1, 2]:
                if (mode == 0):
                    if first_img[r][c][ch] != second_img[r][c][ch]:
                        result [r][c][ch] = 255
                elif (mode == 1):
                    if first_img[r][c][ch] != second_img[r][c][ch]:
                        result [r][c][2] = 255
                        break
    return result

class Differenciator:
    RED = 2
    GREEN = 1
    BLUE = 0

    img_source = None

    def setPicture(self, img):
        if isinstance(img, str):
            self.img_source = cv2.imread(img)
        elif isinstance(img, np.ndarray):
            self.img_source = img
        else:
            raise TypeError, "Type must be str or numpy"
        self.height, self.width = self.img_source.shape[:2]

    def getChanell(self, chanell, img = None, structure = False, type = np.uint8):
        if chanell not in [self.RED, self.GREEN, self.BLUE]:
            return False

        if img == None:
            img = self.img_source

        height, width = img.shape[:2]

        if structure:
            one_color = np.zeros((height, width, 3), type)
        else:
            one_color = np.zeros((height, width, 1), type)

        r = 0
        for row in img:
            c = 0
            for column in row:
                color =  column[chanell]
                if structure:
                    one_color[r][c][chanell] = color
                else:
                    one_color[r][c] = color
                c += 1
            r += 1
        return one_color

    def genVisualisationDiff(self, one_color_diff, zeros = False, discrete = False):
        """
        [CZE] Vizualizace rozdilu
        :param one_color_diff: matice jednoho kanalu m * n
        :param zeros: zda zvyraznovat zvlast nulove rozdily
        :return:
        """
        height, width = one_color_diff.shape[:2]
        visualisation = np.zeros((height, width, 3), np.uint8)
        r = 0
        for row in one_color_diff:
            c = 0
            for column in row:
                if column == 0 and zeros:
                    visualisation[r][c][self.GREEN] = 255
                elif column < 0:
                    visualisation[r][c][self.BLUE] = 255 if discrete else abs(column)
                else:
                    visualisation[r][c][self.RED] = 255 if discrete else column
                c += 1
            r += 1
        return visualisation

    def resizePicture(self, img, multiple):
        height, width = img.shape[:2]
        new_img = np.zeros((height * multiple, width * multiple, 3), img.dtype) #np.uint8
        r = 0
        for row in img:
            c = 0
            for column in row:
                for t in xrange(0, multiple):
                    for tt in xrange(0, multiple):
                        new_img[r * multiple + tt][c * multiple + t] = column
                        new_img[r * multiple + tt][c * multiple + t] = column
                c += 1
            r += 1
        return new_img

    def createTextFile(self, img, name):
        if img == None:
            img = self.img_source
        if img == None:
            return False

        f = open(name, "w")
        for channel in [self.BLUE, self.GREEN, self.RED]:
            f.write("Channel %i\n"%channel)
            for row in img:
                row_txt = ""
                for column in row:
                    row_txt += str(column[channel]) + " "

                f.write(row_txt + "\n")
        f.close()
        return True

    def encodeLDifference(self, img = None):
        if img == None:
            img = self.img_source
        if img == None:
            return False

        height, width = img.shape[:2]

        diff = np.zeros((height, width, 3), np.int8) # !!! int8
        old_pixel = [0, 0, 0]
        r = 0
        for row in img:
            c = 0
            for column in row:
                diff[r][c][self.RED] = int(column[self.RED]) - old_pixel[self.RED]
                diff[r][c][self.GREEN] = int(column[self.GREEN]) - old_pixel[self.GREEN]
                diff[r][c][self.BLUE] = int(column[self.BLUE]) - old_pixel[self.BLUE]

                old_pixel[self.RED] = int(column[self.RED])
                old_pixel[self.GREEN] = int(column[self.GREEN])
                old_pixel[self.BLUE] = int(column[self.BLUE])

                c += 1
            r += 1

        return diff

    def encodeEDifference(self, img = None):
        if img == None:
            img = self.img_source
        if img == None:
            return False

        height, width = img.shape[:2]

        diff = np.zeros((height, width, 3), np.int8) # !!! int8
        old_pixel = [0, 0, 0]
        r = 0
        for row in img:
            c = 0
            for column in row:
                diff[r][c][self.RED] = int(column[self.RED]) - old_pixel[self.RED]
                diff[r][c][self.GREEN] = int(column[self.GREEN]) - old_pixel[self.GREEN]
                diff[r][c][self.BLUE] = int(column[self.BLUE]) - old_pixel[self.BLUE]

                old_pixel[self.RED] = int(column[self.RED])
                old_pixel[self.GREEN] = int(column[self.GREEN])
                old_pixel[self.BLUE] = int(column[self.BLUE])

                c += 1
            old_pixel[self.RED] = int(row[0][self.RED])
            old_pixel[self.GREEN] = int(row[0][self.GREEN])
            old_pixel[self.BLUE] = int(row[0][self.BLUE])
            r += 1

        return diff

    def encodeTDifference(self, img = None):
        if img == None:
            img = self.img_source
        if img == None:
            return False

        height, width = img.shape[:2]

        diff = np.zeros((height, width, 3), np.int8) # !!! int8
        old_pixel = [0, 0, 0]
        r = 0
        for row in img:
            c = 0
            for column in row:
                if r > 0:
                    old_pixel[self.RED] = int(img[r - 1][c][self.RED])
                    old_pixel[self.GREEN] = int(img[r - 1][c][self.GREEN])
                    old_pixel[self.BLUE] = int(img[r - 1][c][self.BLUE])
                diff[r][c][self.RED] = int(column[self.RED]) - old_pixel[self.RED]
                diff[r][c][self.GREEN] = int(column[self.GREEN]) - old_pixel[self.GREEN]
                diff[r][c][self.BLUE] = int(column[self.BLUE]) - old_pixel[self.BLUE]
                if r == 0:
                    old_pixel[self.RED] = int(column[self.RED])
                    old_pixel[self.GREEN] = int(column[self.GREEN])
                    old_pixel[self.BLUE] = int(column[self.BLUE])

                c += 1
            r += 1

        return diff

    def encodeZDifference(self, img = None): #sneak
        if img == None:
            img = self.img_source
        if img == None:
            return False

        height, width = img.shape[:2]

        diff = np.zeros((height, width, 3), np.int8) # !!! int8
        old_pixel = [0, 0, 0]
        r = 0
        for row in img:
            c = 0
            for column in row:
                if r % 2 == 0:
                    diff[r][c][self.RED] = int(column[self.RED]) - old_pixel[self.RED]
                    diff[r][c][self.GREEN] = int(column[self.GREEN]) - old_pixel[self.GREEN]
                    diff[r][c][self.BLUE] = int(column[self.BLUE]) - old_pixel[self.BLUE]

                    old_pixel[self.RED] = int(column[self.RED])
                    old_pixel[self.GREEN] = int(column[self.GREEN])
                    old_pixel[self.BLUE] = int(column[self.BLUE])
                else:
                    diff[r][width - c - 1][self.RED] = int(row[width - c - 1][self.RED]) - old_pixel[self.RED]
                    diff[r][width - c - 1][self.GREEN] = int(row[width - c - 1][self.GREEN]) - old_pixel[self.GREEN]
                    diff[r][width - c - 1][self.BLUE] = int(row[width - c - 1][self.BLUE]) - old_pixel[self.BLUE]

                    old_pixel[self.RED] = int(row[width - c - 1][self.RED])
                    old_pixel[self.GREEN] = int(row[width - c - 1][self.GREEN])
                    old_pixel[self.BLUE] = int(row[width - c - 1][self.BLUE])
                c += 1
            r += 1

        return diff

    def decodeZDifference(self, encode_img = None): #sneak
        if encode_img == None:
            return False

        height, width = encode_img.shape[:2]

        decode_img = np.zeros((height, width, 3), np.int8) # !!! int8

        r = 0
        for row in encode_img:
            c = 0
            for column in row:
                if r % 2 == 0:
                    decode_img[r][c][self.RED] = int(column[self.RED])
                    decode_img[r][c][self.GREEN] = int(column[self.GREEN])
                    decode_img[r][c][self.BLUE] = int(column[self.BLUE])

                    if c > 0:
                        decode_img[r][c][self.RED] += int(decode_img[r][c - 1][self.RED])
                        decode_img[r][c][self.GREEN] += int(decode_img[r][c - 1][self.GREEN])
                        decode_img[r][c][self.BLUE] += int(decode_img[r][c - 1][self.BLUE])
                    elif c == 0 and r > 0:
                        decode_img[r][0][self.RED] += int(decode_img[r - 1][c][self.RED])
                        decode_img[r][0][self.GREEN] += int(decode_img[r - 1][c][self.GREEN])
                        decode_img[r][0][self.BLUE] += int(decode_img[r - 1][c][self.BLUE])

                else:
                    decode_img[r][width - c - 1][self.RED] = int(row[width - c - 1][self.RED])
                    decode_img[r][width - c - 1][self.GREEN] = int(row[width - c - 1][self.GREEN])
                    decode_img[r][width - c - 1][self.BLUE] = int(row[width - c - 1][self.BLUE])

                    if c > 0:
                        decode_img[r][width - c - 1][self.RED] += int(decode_img[r][width - c][self.RED])
                        decode_img[r][width - c - 1][self.GREEN] += int(decode_img[r][width - c][self.GREEN])
                        decode_img[r][width - c - 1][self.BLUE] += int(decode_img[r][width - c][self.BLUE])
                    elif c == 0:
                        decode_img[r][width - 1][self.RED] += int(decode_img[r - 1][width - 1][self.RED])
                        decode_img[r][width - 1][self.GREEN] += int(decode_img[r - 1][width - 1][self.GREEN])
                        decode_img[r][width - 1][self.BLUE] += int(decode_img[r - 1][width - 1][self.BLUE])

                c += 1
            r += 1
        return decode_img

    def encodeNDifference(self, img = None): #sneak
        if img == None:
            img = self.img_source
        if img == None:
            return False

        height, width = img.shape[:2]

        diff = np.zeros((height, width, 3), np.int8) # !!! int8
        old_pixel = [0, 0, 0]
        for c in xrange(width):
            for r in xrange(height):

                if c % 2 == 0:
                    diff[r][c][self.RED] = int(img[r][c][self.RED]) - old_pixel[self.RED]
                    diff[r][c][self.GREEN] = int(img[r][c][self.GREEN]) - old_pixel[self.GREEN]
                    diff[r][c][self.BLUE] = int(img[r][c][self.BLUE]) - old_pixel[self.BLUE]

                    old_pixel[self.RED] = int(img[r][c][self.RED])
                    old_pixel[self.GREEN] = int(img[r][c][self.GREEN])
                    old_pixel[self.BLUE] = int(img[r][c][self.BLUE])
                else:
                    diff[height - r - 1][c][self.RED] = int(img[height - r - 1][c][self.RED]) - old_pixel[self.RED]
                    diff[height - r - 1][c][self.GREEN] = int(img[height - r - 1][c][self.GREEN]) - old_pixel[self.GREEN]
                    diff[height - r - 1][c][self.BLUE] = int(img[height - r - 1][c][self.BLUE]) - old_pixel[self.BLUE]

                    old_pixel[self.RED] = int(img[height - r - 1][c][self.RED])
                    old_pixel[self.GREEN] = int(img[height - r - 1][c][self.GREEN])
                    old_pixel[self.BLUE] = int(img[height - r - 1][c][self.BLUE])

        return diff

    def decodeNDifference(self, encode_img = None): #sneak
        if encode_img == None:
            return False

        height, width = encode_img.shape[:2]

        decode_img = np.zeros((height, width, 3), np.int8) # !!! int8

        for c in xrange(width):
            for r in xrange(height):
                if c % 2 == 0:
                    decode_img[r][c][self.RED] = int(encode_img[r][c][self.RED])
                    decode_img[r][c][self.GREEN] = int(encode_img[r][c][self.GREEN])
                    decode_img[r][c][self.BLUE] = int(encode_img[r][c][self.BLUE])

                    if r > 0:
                        decode_img[r][c][self.RED] += int(decode_img[r - 1][c][self.RED])
                        decode_img[r][c][self.GREEN] += int(decode_img[r - 1][c][self.GREEN])
                        decode_img[r][c][self.BLUE] += int(decode_img[r - 1][c][self.BLUE])
                    elif r == 0 and c > 0:
                        decode_img[r][c][self.RED] += int(decode_img[r][c - 1][self.RED])
                        decode_img[r][c][self.GREEN] += int(decode_img[r][c - 1][self.GREEN])
                        decode_img[r][c][self.BLUE] += int(decode_img[r][c - 1][self.BLUE])

                else:
                    decode_img[height - r - 1][c][self.RED] = int(encode_img[height - r - 1][c][self.RED])
                    decode_img[height - r - 1][c][self.GREEN] = int(encode_img[height - r - 1][c][self.GREEN])
                    decode_img[height - r - 1][c][self.BLUE] = int(encode_img[height - r - 1][c][self.BLUE])

                    if r > 0:
                        decode_img[height - r - 1][c][self.RED] += int(decode_img[height - r][c][self.RED])
                        decode_img[height - r - 1][c][self.GREEN] += int(decode_img[height - r][c][self.GREEN])
                        decode_img[height - r - 1][c][self.BLUE] += int(decode_img[height - r][c][self.BLUE])
                    elif r == 0:
                        decode_img[height - 1][c][self.RED] += int(decode_img[height - 1][c - 1][self.RED])
                        decode_img[height - 1][c][self.GREEN] += int(decode_img[height - 1][c - 1][self.GREEN])
                        decode_img[height - 1][c][self.BLUE] += int(decode_img[height - 1][c - 1][self.BLUE])

        return decode_img

    def encodeZNDifference(self, img = None):
        diff = self.encodeZDifference(img)

        return self.encodeNDifference(diff)

    def decodeLDifference(self, encode_img):#Linear
        if encode_img == None:
           return False

        height, width = encode_img.shape[:2]
        decode_img = np.zeros((height, width, 3), np.int8) # !!! int8

        r = 0
        for row in encode_img:
            c = 0
            for column in row:
                decode_img[r][c][self.RED] += int(column[self.RED])
                decode_img[r][c][self.GREEN] += int(column[self.GREEN])
                decode_img[r][c][self.BLUE] += int(column[self.BLUE])

                if c > 0:
                    decode_img[r][c][self.RED] += int(decode_img[r][c - 1][self.RED])
                    decode_img[r][c][self.GREEN] += int(decode_img[r][c - 1][self.GREEN])
                    decode_img[r][c][self.BLUE] += int(decode_img[r][c - 1][self.BLUE])

                elif c == 0 and r > 0:
                    decode_img[r][c][self.RED] += int(decode_img[r - 1][width - 1][self.RED])
                    decode_img[r][c][self.GREEN] += int(decode_img[r - 1][width - 1][self.GREEN])
                    decode_img[r][c][self.BLUE] += int(decode_img[r - 1][width - 1][self.BLUE])

                c += 1
            r += 1
        return decode_img

    def decodeTDifference(self, encode_img):
        if encode_img == None:
           return False

        height, width = encode_img.shape[:2]
        decode_img = np.zeros((height, width, 3), np.int8) # !!! int8

        r = 0
        for row in encode_img:
            c = 0
            for column in row:
                if r > 0:
                    decode_img[r][c][self.RED] += int(encode_img[r - 1][c][self.RED])
                    decode_img[r][c][self.GREEN] += int(encode_img[r - 1][c][self.GREEN])
                    decode_img[r][c][self.BLUE] += int(encode_img[r - 1][c][self.BLUE])
                decode_img[r][c][self.RED] += int(column[self.RED])
                decode_img[r][c][self.GREEN] += int(column[self.GREEN])
                decode_img[r][c][self.BLUE] += int(column[self.BLUE])
                if r == 0:
                    decode_img[r][c][self.RED] += int(column[self.RED])
                    decode_img[r][c][self.GREEN] += int(column[self.GREEN])
                    decode_img[r][c][self.BLUE] += int(column[self.BLUE])

                c += 1
            r += 1

        return decode_img

    def decodeEDifference(self, encode_img):
        if encode_img == None:
           return False

        height, width = encode_img.shape[:2]
        decode_img = np.zeros((height, width, 3), np.int8) # !!! int8

        r = 0
        for row in encode_img:
            c = 0
            for column in row:
                decode_img[r][c][self.RED] += int(column[self.RED])
                decode_img[r][c][self.GREEN] += int(column[self.GREEN])
                decode_img[r][c][self.BLUE] += int(column[self.BLUE])

                if c > 0:
                    decode_img[r][c][self.RED] += int(decode_img[r][c - 1][self.RED])
                    decode_img[r][c][self.GREEN] += int(decode_img[r][c - 1][self.GREEN])
                    decode_img[r][c][self.BLUE] += int(decode_img[r][c - 1][self.BLUE])

                elif c == 0 and r > 0:
                    decode_img[r][c][self.RED] += int(decode_img[r - 1][0][self.RED])
                    decode_img[r][c][self.GREEN] += int(decode_img[r - 1][0][self.GREEN])
                    decode_img[r][c][self.BLUE] += int(decode_img[r - 1][0][self.BLUE])

                c += 1
            r += 1
        return decode_img


    def decodeZNDifference(self, img):
        diff = self.decodeNDifference(img)
        return self.decodeZDifference(diff)


"""
if __name__ == "__main__":
    img_source = cv2.imread("test.jpg")
    #img_source = cv2.imread("Great_smiles.jpg")
    #img_source = cv2.imread("beer_test.jpg")

    d = Differenciator()
    d.setPicture(img_source)
    img_blue = d.getChanell(Differenciator.BLUE, structure=True)

    # SNEAK

    diff = d.encodeZDifference()  #sneak
    d.createCsvFile(diff, "difference_list.csv")
    #print diff
    diff_b = d.getChanell(Differenciator.BLUE, diff, type=np.int8)
    diff_g = d.getChanell(Differenciator.GREEN, diff, type=np.int8)
    diff_r = d.getChanell(Differenciator.RED, diff, type=np.int8)
    #print diff_b
    visualization_b = d.genVisualisationDiff(diff_b, True)
    discrete_visualization_b = d.genVisualisationDiff(diff_b, True, True)
    #print visualization_b
    cv2.imshow("Obrazek",img_source)
    cv2.imshow("blue",img_blue)

    cv2.imshow("diference - sneak", visualization_b)
    cv2.imshow("discrete diference - sneak", discrete_visualization_b)

    cv2.imshow("diference - sneak BIG", d.resizePicture(visualization_b, 4))
    cv2.imshow("discrete diference - sneak BIG", d.resizePicture(discrete_visualization_b, 4))


    cv.WaitKey(0)
"""
