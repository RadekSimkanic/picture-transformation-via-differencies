__author__ = 'gulliver - Radek Simkanic - SIM0094'

import numpy as np
import messages as msg
import sys
import os
import struct

from helper_functions import readBlocks
from BinnaryCode import *
import LZW as lzw
import RLE as rle
import BWT as bwt

"""
TODO
Checker of memory for large data
"""


class CompressDecompress:
    RED = 2
    GREEN = 1
    BLUE = 0

    METHOD_CODE = {"Z":0, "N":1, "L":2, "E":3, "ZN":4, "T":5}
    def __init__(self):

        self.positive_data = {
            self.RED : [],
            self.GREEN : [],
            self.BLUE : [],
        }

        self.negative_data = {
            self.RED : [],
            self.GREEN : [],
            self.BLUE : []
        }

        self.use_rle = False
        self.use_bwt = False
        self.use_lzw = False
        self.use_interleaving = False
        self.use_short_rle_separator = False
        self.output_file = "compress.bin"

    def useRle(self, enable = True):
        self.use_rle = enable
        return self

    def useBwt(self, enable = True):
        self.use_bwt = enable
        return self

    def useLzw(self, enable = True):
        self.use_lzw = enable
        return  self

    def useInterleaving(self, enable = True):
        self.use_interleaving = enable

    def useShortRleSeparator(self, enable = True):
        self.use_short_rle_separator = enable

    def outputFile(self, file):
        self.output_file = file
        return self

    def compress(self, numpy_data, diff_method):
        if not isinstance(numpy_data, np.ndarray):
            msg.message(
                msg.SYSTEM_ERROR,
                "numpy_data must be ndarry (numpy)",
                TypeError
            )

        print numpy_data.shape

        width = numpy_data.shape[0]
        height = numpy_data.shape[1]
        chanels = numpy_data.shape[2]
        self.__separateData(numpy_data)
        del(numpy_data)

        # join
        if self.use_interleaving:
            pd = []
            for i in xrange(len(self.positive_data[0])):
                pd.append(self.positive_data[self.RED][i])
                pd.append(self.positive_data[self.GREEN][i])
                pd.append(self.positive_data[self.BLUE][i])
            del(self.positive_data[self.RED], self.positive_data[self.GREEN], self.positive_data[self.BLUE])
        else:
            pd = self.positive_data[self.RED]
            del(self.positive_data[self.RED])
            pd += self.positive_data[self.GREEN]
            del(self.positive_data[self.GREEN])
            pd += self.positive_data[self.BLUE]
            del(self.positive_data[self.BLUE])

        nd = self.negative_data[self.RED] + self.negative_data[self.GREEN] + self.negative_data[self.BLUE]

        # remove of zeros at the end
        while True:
            if nd[-1] == 0:
                nd.pop()
            else:
                break

        nd_codes = self.__genSignedCodes(nd)


        # BWT
        bwt_index = 0
        if self.use_bwt:
            msg.message(
                msg.INFORMATION,
                "Burrows Wheller Transformation data..."
            )

            alphabets = map(lambda x: x, xrange(0, 256))
            bwt_positive = bwt.BWTOwnAlphabet(pd, alphabets)
            pd_bwt = bwt_positive.encode()

            bwt_index = pd_bwt[0]
            pd = pd_bwt[1]

            msg.message(
                msg.DONE,
                "Encoded. Transformation done"
            )

        if self.use_rle:

            if self.use_short_rle_separator:
                rle_separator = 3
                plus = 2
            else:
                rle_separator = encodeFibonacci(max(pd)+2) # +1 next number +1 coding of numbers (0 = 0b11)
                plus = 1

            diff_data = self.__fibonacciTransform(pd, plus)

            #rle_separator = encodeFibonacci(max(pd)+2) # +1 next number +1 coding of numbers (0 = 0b11)
            print "RLE SEPARATOR %s  %i"%(bin(rle_separator),max(pd)+2 )
            del(pd)

            diff_data = self.__rleCompression(diff_data, rle_separator)

            diff_data.append(3)# for synchronization
            diff_data = resplitBinaryCodes(diff_data, 8)

        elif self.use_lzw:
            msg.message(
                msg.INFORMATION,
                "LZW Compression..."
            )
            chr_data = map(lambda x: chr(x), pd)
            del(pd)
            diff_data = lzw.compress(chr_data)

            msg.message(
                msg.DONE,
                "Compression done"
            )

            diff_data = self.__fibonacciTransform(diff_data)

            diff_data.append(3)# for synchronization
            diff_data = resplitBinaryCodes(diff_data, 8)


        else:
            diff_data = self.__fibonacciTransform(pd)
            del(pd)
            diff_data.append(3)# for synchronization
            diff_data = resplitBinaryCodes(diff_data, 8)

        msg.message(
            msg.DONE,
            " Writing data to file..."
        )
        """
        BB - OPTION in format: xzzzzilg rwbetttt
            x - reserved for expand next options
            z - reserved
            i - interleaving
            l - LZW
            g - gray (only one channel 0-255)
            r - RLE
            w - width (1) or height (0)
            b - BWT
            e - expand sizes
            t - transformation method
        [B] - next option not used now (good for the future feature)
        I - Width or height
        I/II - Size of virtual numbers - for simpler programming :D
        [I] - BWT index
        [I] - RLE separator (I is very big (9bits needed - changed?)
        BBBB... inline diff data
        [BBBB...] signature data
        """

        fw = open(self.output_file, "wb")

        # picture reconstruct information
        only_gray_chanel = 1 if chanels == 1 else 0
        lzw_enable = 1<<1 if self.use_lzw and not self.use_rle else 0
        interleaving_enable = 1<<2 if self.use_interleaving else 0
        option1 = only_gray_chanel | lzw_enable | interleaving_enable

        width_enable = (1<<6) if width < height else 0
        bwt_enable = (1<<5) if self.use_bwt else 0
        expand_sizes = (1<<4) if len(diff_data) > (1<<32) - 1 else 0
        rle_enable = (1<<7) if self.use_rle else 0 # and not self.use_lzw
        option2 = diff_method | width_enable | bwt_enable | expand_sizes | rle_enable

        fw.write(struct.pack("BB", option1, option2))

        # next option
        #TODO

        # width / height
        fw.write(struct.pack("I", width if width_enable else height))

        # size of virtual numbers
        if expand_sizes:
            fw.write(struct.pack("II", len(diff_data)))
        else:
            fw.write(struct.pack("I", len(diff_data)))

        # BWT index of diff_data
        if bwt_enable and expand_sizes:
            fw.write(struct.pack("II", bwt_index))
        elif bwt_enable:
            fw.write(struct.pack("I", bwt_index))

        # RLE separator
        if rle_enable:
            fw.write(struct.pack("I", rle_separator))

        # diff data
        mask = "%iB"%len(diff_data)
        fw.write(struct.pack(mask, *diff_data))

        # signed data
        mask = "%iB"%len(nd_codes)

        fw.write(struct.pack(mask, *nd_codes))
        fw.close()

        msg.message(
            msg.INFORMATION,
            " File is generated"
        )

    def decompress(self, file_path):
        if not os.path.isfile(file_path):
            msg.message(
                msg.SYSTEM_ERROR,
                "%s is not file"%file_path,
                IOError
            )

        msg.message(
            msg.INFORMATION,
            "Decompressing file..."
        )

        fr = open(file_path, "rb")

        # translate head
        option1, option2 = struct.unpack("BB", fr.read(1 + 1) )

        if option1 & (1<<7):
            # TODO next options
            raise NotImplemented, "Future features (next options)"

        if option1 & 1:
            # TODO gray scale (only one chanel)
            raise NotImplemented, "Gray scale"



        use_lzw = True if option1 & (1<<1) else False
        use_interleaving = True if option1 & (1<<2) else False
        use_rle = True if option2 & (1<<7) else False
        use_width = True if option2 & (1<<6) else False
        use_bwt = True if option2 & (1<<5) else False
        is_expanded = True if option2 & (1<<4) else False
        method = option2 & 0b1111

        width_height = struct.unpack("I", fr.read(4) )[0]
        width = width_height if use_width else 0
        height = width_height if use_width == 0 else 0

        if is_expanded:
            size, size2 = struct.unpack("II", fr.read(4 + 4) )
            size <<= 4 * 8
            size += size2
        else:
            size = struct.unpack("I", fr.read(4) )[0]

        # BWT index
        if use_bwt: #enable bigger size? (+I)
            bwt_index = struct.unpack("I", fr.read(4) )[0]

        # RLE
        if use_rle:
            rle_separator = struct.unpack("I", fr.read(4) )[0]
            print "RLE SEPARATOR %s"%bin(rle_separator)

        # check
        if width_height <= 0 or size <= 0 or method not in self.METHOD_CODE.values() or (use_lzw and use_rle):
            msg.message(
                msg.ERROR,
                "Basic information for decompress image are bad or not possible loaded. Bad file or file is crashed! %i %i %i"%(width_height, size, method)
            )

        # Data
        # ??? check size or partly load
        all_numbers = []
        i = 0
        for stream in readBlocks(fr, 1):
            all_numbers.append(struct.unpack("B", stream)[0])

        numbers_for_regenerate_fibonacci = all_numbers[:size]
        signed_numbers = all_numbers[size:]
        del(all_numbers)

        fib_numbers = self.__regenerateFibonacci(numbers_for_regenerate_fibonacci, True)

        # RLE
        if use_rle:
            fib_numbers = self.__rleExpander(fib_numbers, rle_separator)

        # decode fibonacci to differentiation number
        numbers = map(lambda x: decodeFibonacci(x)-1, fib_numbers)

        del(fib_numbers)

        if use_bwt:
            numbers = self.__decodeBwt(numbers, bwt_index)

        if use_lzw:
            numbers = self.__lzwDecompress(numbers)

        signed = self.__genListBitSigned(signed_numbers)

        del(signed_numbers)

        if width > height:
            height = (len(numbers) / width) / 3
        else:
            width = (len(numbers) / height) / 3

        if use_interleaving:
            numbers = self.__interleavingDecode(numbers)

        self.__categorizeData(numbers, signed, width, height)

        del(numbers, signed)

        img = []
        i = 0
        for row in xrange(width):
            r = []
            for column in xrange(height):
                c = [int(self.positive_data[0][i]), int(self.positive_data[1][i]), int(self.positive_data[2][i])]
                i += 1
                r.append(c)
            img.append(r)

        img = np.array(img, dtype=np.int)

        msg.message(
            msg.DONE,
            "DONE"
        )

        # Get key by value
        method = self.METHOD_CODE.keys()[self.METHOD_CODE.values().index(method)]

        return (img, method)

    def __interleavingDecode(self, inline_data):
        msg.message(
                msg.INFORMATION,
            "Interleaving decode..."
        )

        new_numbers_r = []
        new_numbers_g = []
        new_numbers_b = []

        for i in xrange(len(inline_data)):
            if i % 3 == 0:
                new_numbers_r.append(inline_data[i])
            elif i % 3 == 1:
                new_numbers_g.append(inline_data[i])
            else:
                new_numbers_b.append(inline_data[i])

        msg.message(
                msg.DONE,
            "Interleaving decode done"
        )
        return new_numbers_r + new_numbers_g + new_numbers_b

    def __lzwDecompress(self, inline_data):
        msg.message(
                msg.INFORMATION,
            "LZW decompression..."
        )

        numbers = lzw.decompress(inline_data)
        numbers = map(lambda x: ord(x), numbers)

        msg.message(
            msg.DONE,
            "Decompression done"
        )
        return numbers

    def __decodeBwt(self, inline_data, bwt_index):
        msg.message(
            msg.INFORMATION,
            "BWT decoding..."
        )

        b = bwt.BWTOwnAlphabet(inline_data, map(lambda x: x, xrange(0, 255) ) )
        numbers = b.decode(bwt_index)
        msg.message(
            msg.DONE,
            "BWT decoding done"
        )
        return numbers

    def __fibonacciTransform(self, inline_data, plus = 1):
        msg.message(
            msg.INFORMATION,
            "Fibonacci encode"
        )

        fib = map(lambda x: encodeFibonacci(x+plus), inline_data)

        msg.message(
            msg.DONE,
            "Fibonacci done"
        )

        return fib

    def __rleCompression(self, inline_data, separator):
        msg.message(
            msg.INFORMATION,
            "Simple RLE compression..."
        )

        length_separator = length(separator)

        r = rle.RLE(inline_data)
        rle_positive = r.compress()

        new_fib = []
        for number, count in rle_positive:
            if count == 1:
                new_fib.append(number)
                continue

            number_length = length(number)
            if length_separator + number_length + length(encodeFibonacci(count)) > number_length * count:
                for i in xrange(count):
                    new_fib.append(number)
            else:
                new_fib.append(separator)
                new_fib.append(encodeFibonacci(count)) # !!! count: 11 = 1
                new_fib.append(number)

        msg.message(
            msg.DONE,
            "Compression done"
        )

        return  new_fib




    def __rleExpander(self, data_list, separator):
        msg.message(
            msg.INFORMATION,
            "RLE Expand..."
        )

        new_list = []
        count = 0
        for number in data_list:
            if count > 1:
                for i in xrange(count):
                    new_list.append(number)
                count = 0
                continue
            if count == 1:
                count = decodeFibonacci(number)
                continue
            if number == separator:
                count = 1
                continue
            new_list.append(number)

        msg.message(
            msg.DONE,
            "RLE expand done"
        )

        return new_list


    def __regenerateFibonacci(self, data_list, status = False):
        msg.message(
            msg.INFORMATION,
            "Fibonacci regenerate..."
        )

        decode_fib = []
        data = data_list.pop(0)
        """
        Started:
        Data: 11010010 10011000 ...
        Mask:   110000 ->
        """
        mask = 3 << 4
        mask_length = 6
        candidate = 0
        is_candidate = False
        load_data = 0
        i = 0
        for number in data_list:#TODO Time optimalize for long sequence 11111111...
            i += 1

            #print("STATUS %.2f %%"%((float(i)/float(len(data_list)))*100.0, end="\r") #python 3
            if i % 1000 == 0 % status: print "STATUS %.2f %%"%((float(i)/float(len(data_list)))*100.0)

            data <<= 8
            data += number

            mask <<= 8
            mask_length += 8

            if load_data < 10 and i < len(data_list):
                load_data += 1
                continue
            load_data = 0

            skip = False

            while mask_length > 4 and load_data == 0:
                if not is_candidate:
                    ones = 0
                if not is_candidate and data & mask == mask:
                    l = length(data) - mask_length
                    candidate = getFirstBits(data, l)
                    data = cutFirst(data, l)

                    if data & (mask>>1) != mask>>1:
                        decode_fib.append(candidate)
                        skip = True
                    else:
                        is_candidate = True

                if not is_candidate:
                    mask >>= 1
                    mask_length -= 1

                while is_candidate:
                    if length(data) < ones + 1:
                        # NEED NEXT DATA
                        load_data -= 1
                        break

                    if getValueInPosition(data, ones + 1, True):
                        ones += 1
                    else:
                        if ones % 2 == 0:
                            mask >>= 2
                            mask_length -= 2
                            decode_fib.append(candidate)
                        else:
                            candidate <<= 1
                            candidate += 1
                            decode_fib.append(candidate)
                            mask_length -= 3
                            mask >>= 3
                            data = cutFirst(data)
                        is_candidate = False
                        break

                if skip and mask_length > 4:
                    mask >>= 1
                    mask_length -= 1
                    skip = False

        if length(data) > 3:
            # remove filling zeros
            while getLastBits(data) == 0:
                data = cutLast(data)
            # remove synchronization 11
            data = cutLast(data, 2)
        # add last number
        decode_fib.append(data)

        #print("STATUS 100 %", end="\r")  # python 3
        if status: print "STATUS 100 %"

        msg.message(
            msg.DONE,
            "Fibonacci is now regenerated"
        )


        return decode_fib



    def __categorizeData(self, lst, signed, width, height):
        limit = width * height
        i = 0
        j = 0
        chanel = self.RED
        for number in lst:
            # reset for new channel
            if i == limit:
                chanel -= 1
                i = 0
                if chanel < 0:
                    break

            if number != 0 and j < len(signed):
                if signed[j]:
                    number *= -1
                j += 1

            self.positive_data[chanel].append(number)
            i += 1

    def __genSignedCodes(self, lst):
        result = []
        c = 1
        i = 1
        for number in lst:
            if i == 8:
                result.append(c)
                c = 0
                i = 0

            c <<= 1
            c += number
            i += 1
        c <<= 8 - i
        result.append(c)
        return result

    def __genListBitSigned(self, lst):
        signed_list = []
        pocet = 0
        for number in lst:
            pocet+=1
            #gen zeros
            for i in xrange(8 - length(number) if number > 0 else 8):
                signed_list.append(0)

            if number > 0:
                mask = 1 << (length(number) - 1 )
                while mask:
                    signed_list.append(1 if number & mask else 0)
                    mask >>= 1
        return signed_list[1:]


    def __separateData(self, data):
        msg.message(
            msg.INFORMATION,
            "Separation data..."
        )

        for r in data:
            for c in r:
                chanel = 0
                for ch in c:
                    value = int(ch)
                    sign = 0

                    if value < 0:
                        value = abs(value)
                        sign = 1

                    if value != 0:
                        self.negative_data[chanel].append(sign)
                    self.positive_data[chanel].append(value)

                    chanel += 1


        msg.message(
            msg.DONE,
            "Separation data done"
        )
