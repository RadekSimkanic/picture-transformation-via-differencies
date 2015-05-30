#!/usr/bin/python
#UTF-8
__author__ = 'gulliver - Radek Simkanic - SIM0094'

import os
import Image # PIL

from core.application_arguments import *
from core.differentiation import *
from core.statistics import *
from core.compress_decompress import *
import cProfile
import pstats
import cv2
import cv


class ImageArgument(Argument):
    def _check(self, value):
        if not os.path.isfile(value):
            return (False, "%s is not file"%value)
        """
        try:
            #img = Image.open(value)
            cv2.imread(value)
        except:
            return (False, "%s is not correct image"%value)
        """
        return True

class OutputArgument(Argument):
    def _check(self, value):
        if os.path.isfile(value):
            if os.path.isdir(value):
                return (False, "%s is folder!"%value)

            # rewrite it?
            q = raw_input("File (%s) is exist, rewrite it? (y/n): "%value)

            if q.lower() not in ("y", "yes"):
                return (False, "The file (%s) is not allowed to rewrite!"%value)
        return True

class MethodArgument(Argument):
    methods = [
        "sneak", "zigzag", "Z", "N", "L", "simple", "E", "ZN", "T"
    ]
    def _check(self, value):
        if value not in self.methods:
            return (False, "%s is not applicable method"%value)

        return True

    def getMethods(self):
        self.methods

class ShowDifferencesArgument(Argument):
    values = [
        "yes", "no", "true", "false", "0", "1"
    ]
    def _check(self, value):
        if value not in self.values:
            return (False, "%s is not applicable"%value)

        return True

class AlgorithmArgument(Argument):
    values = [
        "rle", "rle+bwt", "lzw", "nothing"
    ]

    def _check(self, value):
        if value not in self.values:
            return (False, "%s is not applicable"%value)
        return True

class ExpandPixelsArgument(Argument):
    def _check(self, value):
        try:
            value = int(value)
            if value <= 0:
                return (False, "%i is not applicable. Value must be unsigned integer and greater than 0"%value)

        except ValueError:
            return (False, "%s is not applicable. Value must be unsigned integer and greater than 0"%value)

        return True

class StatisticsArgument(Argument):
    values = [
        "pareto", "pie", "histogram", "simply"
    ]

    def _check(self, value):
        values = value.split(",")
        for v in values:
            if v.lower() not in self.values:
                return (False, "%s (%s) is not applicable. Value must be: pareto, pie, histogram, simply"%(value, v))
        return True

def main():
    # Application arguments
    arg_img = ImageArgument("i", "input", "The source picture")
    arg_output = OutputArgument("o", "output", "The destination for save (compressed/decompressed) file. When is not set than name is 'compress.bin' (rewritable)")
    arg_method = MethodArgument("m", "method", "The differences method")
    arg_compress = Argument("c", "compress", "Compress image", False)
    arg_decompress = Argument("d", "decompress", "Decompress image", False)
    arg_show_diff = ShowDifferencesArgument("v", "visible", "Visualisation of differences (value: true => discrete visualisation")
    arg_interleaving = Argument("n", "interleaving", "How to save channels of pixels. With this parameter: Each channel separately for each pixel. Without this parameter: Each channel for all pixels.", False)
    arg_algorithm = AlgorithmArgument("a", "algorithm", "Compression algorithm: nothing (default), rle (recommended), rle+bwe, lzw")
    arg_expand = ExpandPixelsArgument("e", "expand", "Create bigger pixel in visualisation of differences")
    arg_statistics = StatisticsArgument("s", "statistics", "Statistics graphs. Values: pie, chart, pareto, simply (separated by a comma)")

    # Arguments dependencies
    arg_img.setDependencies([
        [arg_decompress, arg_method]
    ])

    arg_output.setDependencies([
        [arg_compress, arg_decompress]
    ])

    arg_method.setDependencies([
        arg_img
    ])

    arg_compress.setDependencies([
        arg_method, arg_img
    ])

    arg_decompress.setDependencies([
        arg_img
    ])

    arg_show_diff.setDependencies([
        arg_method
    ])

    arg_interleaving.setDependencies([
        arg_compress
    ])

    arg_algorithm.setDependencies([
        arg_compress
    ])

    arg_expand.setDependencies([
        arg_show_diff
    ])

    arg_statistics.setDependencies([
        arg_method
    ])

    # Incompatible arguments
    arg_compress.setIncompatibleArguments([
        arg_decompress
    ])

    arg_decompress.setIncompatibleArguments([
        arg_compress
    ])

    arg_method.setIncompatibleArguments([
        arg_decompress
    ])

    arg_show_diff.setIncompatibleArguments([
        arg_decompress
    ])


    # Check arguments
    arg = Arguments()
    arg.setHeadInformation("Last params without commands is source picture.")\
    .addArgument(
        arg_img, True
    )\
    .addArgument(
        arg_output
    )\
    .addArgument(
        arg_method
    )\
    .addArgument(
        arg_compress
    )\
    .addArgument(
        arg_decompress
    )\
    .addArgument(
        arg_show_diff
    )\
    .addArgument(
        arg_interleaving
    )\
    .addArgument(
        arg_algorithm
    )\
    .addArgument(
        arg_expand
    )\
    .addArgument(
        arg_statistics
    )\
    .check()

    # Compress
    if arg_img.isCorrect() and arg_method.isCorrect():
        diff = Differenciator()
        diff.setPicture(arg_img.getValue())


        # rewrite
        method = arg_method.getValue()
        if method in ["sneak", "zigzag"]:
            method = "Z"
        elif method in ["simple"]:
            method = "E"

        # switch case
        diff_img = {
            "Z"         : diff.encodeZDifference,
            "N"         : diff.encodeNDifference,
            "L"         : diff.encodeLDifference,
            "E"         : diff.encodeEDifference,
            "ZN"        : diff.encodeZNDifference,
            "T"         : diff.encodeTDifference,
        }.get(method)()

        method_code = CompressDecompress.METHOD_CODE.get(method)

        msg.message(
            msg.DONE,
            "Differences done"
        )

    if arg_statistics.isCorrect():
        data = diff_img
        img_original = diff.img_source
        methods = arg_statistics.getValue().split(",")
        methods = map(lambda x: x.lower(), methods)

        minimum = min(toInlineList(data) )
        maximum = max(toInlineList(data) )
        p = np.histogram(data, xrange(minimum, maximum))

        # Pareto
        if "pareto" in methods:
            paretoChart(p[0], p[1])

        # Pie Chart
        if "pie" in methods:
            pieChart(p[0], p[1])

        # Histogram
        if "histogram" in methods:
            plt.hist(toInlineList(data), xrange(minimum, maximum), label="All channels", color="yellow")
            #"""
            diff_b = diff.getChanell(Differenciator.BLUE, diff_img, type=np.int8)
            diff_g = diff.getChanell(Differenciator.GREEN, diff_img, type=np.int8)
            diff_r = diff.getChanell(Differenciator.RED, diff_img, type=np.int8)
            plt.hist(toInlineList(diff_b), xrange(-255, 255), label="Blue channel", color="b", alpha=0.5, histtype='step')
            plt.hist(toInlineList(diff_g), xrange(-255, 255), label="Green channel", color="g", alpha=0.5, histtype='step')
            plt.hist(toInlineList(diff_r), xrange(-255, 255), label="Red channel", color="r", alpha=0.5, histtype='step')
            plt.hist(toInlineList(img_original), xrange(0, 255), label="original", color="black", alpha=0.5)
            #"""
            #plt.xlim([-255, 255])
            plt.legend()
            plt.title("Histogram")
            plt.xlabel("Differences value")
            plt.ylabel("Count")
            plt.show()

        # simply
        if "simply" in methods:
            # Modus
            sh = shorth(toInlineList(data))
            print sh
            print "mode with short: %f"%mode(sh)
            print "classical mode: %i"%mode(toInlineList(data))
            print "median: %i"%mode(toInlineList(data))
            print "avg: %f"%arithmeticMean(toInlineList(data))

    if arg_show_diff.isCorrect():
        msg.message(
            msg.INFORMATION,
            "Show differences (pause)"
        )
        diff_b = diff.getChanell(Differenciator.BLUE, diff_img, type=np.int8)
        diff_g = diff.getChanell(Differenciator.GREEN, diff_img, type=np.int8)
        diff_r = diff.getChanell(Differenciator.RED, diff_img, type=np.int8)
        if arg_show_diff.getValue() in ("yes", "true", "1"):
            visualisation_b = diff.genVisualisationDiff(diff_b, True, True)
            visualisation_g = diff.genVisualisationDiff(diff_g, True, True)
            visualisation_r = diff.genVisualisationDiff(diff_r, True, True)
        else:
            visualisation_b = diff.genVisualisationDiff(diff_b, True, False)
            visualisation_g = diff.genVisualisationDiff(diff_g, True, False)
            visualisation_r = diff.genVisualisationDiff(diff_r, True, False)
        if arg_expand.isCorrect():
            expand = int(arg_expand.getValue())
            visualisation_b = diff.resizePicture(visualisation_b, expand)
            visualisation_g = diff.resizePicture(visualisation_g, expand)
            visualisation_r = diff.resizePicture(visualisation_r, expand)
            visualisation_all = diff.resizePicture(diff_img, expand)
        else:
            visualisation_all = diff_img
        cv2.imshow("DIFF visualisation - blue", visualisation_b)
        cv2.imshow("DIFF visualisation - green", visualisation_g)
        cv2.imshow("DIFF visualisation - red", visualisation_r)
        cv2.imshow("DIFF visualisation - ALL int8", visualisation_all)
        cv2.waitKey(0)
        msg.message(
            msg.DONE,
            "Showing close"
        )

    if arg_compress.isCorrect():
        compress = CompressDecompress()

        if arg_interleaving.isCorrect():
            compress.useInterleaving()

        if arg_algorithm.isCorrect():
            if arg_algorithm.getValue() == "rle+bwe":
                compress.useRle()
                compress.useBwt()
            elif arg_algorithm.getValue() == "rle":
                compress.useRle()
            elif arg_algorithm.getValue() == "lzw":
                compress.useLzw()

        if arg_output.isCorrect():
            compress.outputFile(arg_output.getValue())

        compress.compress(diff_img, method_code)


    # Decompress
    if arg_decompress.isCorrect() and arg_img.isCorrect():
        decompres = CompressDecompress().decompress(arg_img.getValue())
        img = decompres[0]
        method = decompres[1]

        diff = Differenciator()
        # switch case
        img_done = {
            "Z"         : diff.decodeZDifference,
            "N"         : diff.decodeNDifference,
            "L"         : diff.decodeLDifference,
            "E"         : diff.decodeEDifference,
            "ZN"        : diff.decodeZNDifference,
            "T"         : diff.decodeTDifference,
        }.get(method)(img)
        cv2.imshow("Picture",img_done.astype(np.uint8))
        cv.WaitKey(0)

        if arg_output:

            msg.message(
                msg.INFORMATION,
                "Saving to %s" % arg_output.getValue()
            )

            cv2.imwrite(arg_output.getValue(), img_done.astype(np.uint8))

            msg.message(
                msg.DONE,
                "Saved"
            )


if __name__ == "__main__":
    #main()
    # cprofile
    cProfile.run('main()', 'profile')
    p = pstats.Stats('profile')
    p.sort_stats('time').print_stats(10)
