__author__ = 'gulliver - Radek Simkanic - SIM0094'

import numpy as np
import csv
from core.helper_functions import *

import matplotlib.pyplot as plt


def createCsvFile(data, head = None, name = "data.csv"):
    print "CSV"
    if data == None:
        print "FALSE"
        return False

    with open(name, "wb") as csvfile:
        print "Open"
        writer = csv.writer(csvfile, delimiter = ";")

        # head of csv file
        if type(head) == type([0,0]) or type(head) == type((0,0)):
            print "Write head"
            writer.writerow(head)

        print "Write data"
        for row in data:
            print "Write row"
            writer.writerow(row)
        print "TRUE"
        return True

def paretoChart(frequency, labels, bar_color = "b", pareto_color = "r", x_label = "", y_label = ""):
    # sorted by frequency
    both = sorted(zip(frequency, labels), reverse = True)
    frequency, labels = zip(*both)
    summary = sum(frequency)
    pareto = []
    actual = 0.0
    for i in frequency:
        actual += float(i) / float(summary) * 100.0
        #actual += i
        pareto.append(actual)


    fig = plt.figure()

    ind = np.arange(len(frequency))  # the x locations for the groups
    width = .98 # with do of the bars, where a width of 1 indidcates no space between bars
    x = ind + .5 * width # find the middle of the bar

    # first graph - bar
    ax1 = fig.add_subplot(111)
    ax1.bar(xrange(0, len(frequency)), frequency, color = bar_color, width=width)#, align="center"
    ax1.set_xlabel(x_label)
    ax1.set_ylabel(y_label)
    ax1.set_ylim(ymax=summary)
    ax1.set_xticks(x) # set ticks for middle of bars
    ax1.set_xticklabels(labels)

    # second graph - plot
    ax2 = ax1.twinx()

    ax2.plot(xrange(0, len(frequency)), pareto, color = pareto_color, marker='o')
    ax2.set_ylabel("%")
    ax2.set_ylim(0, 100)

    plt.show()


def pieChart(frequency, labels, visible_items = 13):
    # http://stackoverflow.com/questions/6170246/how-do-i-use-matplotlib-autopct
    # http://www.secnetix.de/olli/Python/lambda_functions.hawk
    # http://matplotlib.org/examples/pie_and_polar_charts/pie_demo_features.html

    # seradit obe pole dle frequency
    both = sorted(zip(frequency, labels), reverse = True)
    sizes, labels = zip(*both)
    summary = sum(frequency)

    first_sizes = list(sizes[0:visible_items])
    first_labels = list(labels[0:visible_items])

    first_sizes.append(sum(sizes[visible_items:]))
    first_labels.append("others")

    explode = [0]*(visible_items+1)
    explode[0] = 0.05
    explode[visible_items] = 0.05

    colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral']

    lambda_autopct = lambda pct:  '{p:.2f}%  \n({v:d})'.format(p=pct,v=(int(pct*summary/100.0)))

    plt.pie(first_sizes, explode=explode, labels=first_labels, colors = colors,
            autopct=lambda_autopct, shadow=True, pctdistance=0.9) #autopct="%1.1f%" , startangle=90

    plt.show()

#avg
def arithmeticMean(data):
    return float(sum(data))/len(data) if len(data) > 0 else float('nan')

def shorth(data):
    middle = int(round(len(data)/2.0, 0)) -  1
    sorted_data = sorted(data)
    end = middle - 1
    shorted_length = 0
    shorted_range = 0
    for start in xrange(0, len(data) - middle + 1):
        #print "start %i end %i size %i"%(start, end, len(data))
        if start == 0 or shorted_length > int(sorted_data[end]) - int(sorted_data[start]):
            #print "start %i end %i size %i"%(start, end, len(data))
            shorted_length = int(sorted_data[end]) - int(sorted_data[start])
            shorted_range = (sorted_data[start], sorted_data[end])
        end += 1
    return shorted_range

def mode(data_or_shorth):
    """
    Function for calculating modus
    :param data_or_shorth: when (number1, number2) number1 <= number2 and tuple of data type: shorth else classical
    :return: modus value
    """
    if type(data_or_shorth) == type((1,1)) and len(data_or_shorth) == 2 and data_or_shorth[0] <= data_or_shorth[1]:
        return float(sum(data_or_shorth)) / 2.0

    histogram = np.histogram(data_or_shorth, xrange(-255, 255))
    maximum = histogram[0][0]
    item = histogram[1][0]

    if len(histogram[0]) <= 1:
        return item

    for i in xrange(1, len(histogram[0])):
        if (maximum < histogram[0][i]):
            maximum = histogram[0][i]
            item = histogram[1][i]

    return item

def median(data):
    return sorted(data, reverse=True)[ (len(data)-1)/2 ]


def negativePositive(data):
    negpos = []

    for channel in [0, 1, 2]:
        for row in data:
            for column in row:
                if column[channel] >= 0:
                    negpos.append(1)
                else:
                    negpos.append(-1)
    section_switch = []
    section_length = 0
    last_value = 1
    for item in negpos:
        if item == last_value:
            section_length += 1
        else:
            section_switch.append(section_length)
            section_length = 1
            last_value *= 1
    section_switch.append(section_length)

    return section_switch


def exploratoryStatisticsIndividual(diff, diff_b, diff_g, diff_r, img_source):
    p = np.histogram(diff, xrange(-255, 256))
    paretoChart(p[0], p[1])

    #paretoChart(sorted([0, 100, 25, 300, 80, 200], reverse=True), [1, 2, 3, 4, 5, 6])
    #pareto_data = []


    # Pie Chart
    pieChart(p[0], p[1])

    #histogram = np.histogram(diff, xrange(-255, 255))
    #paretoChart(sorted(histogram[0], reverse=True), [])

    # https://bespokeblog.wordpress.com/2011/07/11/basic-data-plotting-with-matplotlib-part-3-histograms/

    #histogram = np.histogram(diff, xrange(-255, 255))
    #print histogram[0]
    #print histogram[1]
    #plt.hist(histogram[0], histogram[1])
    #print toInlineList(diff)

    # Histogram
    #print np.histogram(diff, xrange(-255, 255))
    plt.hist(toInlineList(diff), xrange(-255, 255), label="All channels", color="yellow")
    plt.hist(toInlineList(diff_b), xrange(-255, 255), label="Blue channel", color="b", alpha=0.5, histtype='step')
    plt.hist(toInlineList(diff_g), xrange(-255, 255), label="Green channel", color="g", alpha=0.5, histtype='step')
    plt.hist(toInlineList(diff_r), xrange(-255, 255), label="Red channel", color="r", alpha=0.5, histtype='step')
    plt.hist(toInlineList(img_source), xrange(0, 255), label="original", color="black", alpha=0.5)
    #plt.xlim([-255, 255])
    plt.legend()
    plt.title("Histogram")
    plt.xlabel("Differences value")
    plt.ylabel("Count")
    plt.show()




    # Modus and others
    # All channels
    print "all: "
    sh = shorth(toInlineList(diff))
    print sh
    print "modus se short: %f"%mode(sh)
    print "modus klasicky: %i"%mode(toInlineList(diff))
    print "median: %i"%mode(toInlineList(diff))
    print "prumer: %f"%arithmeticMean(toInlineList(diff))
    # Blue channel
    print "Blue: "
    sh = shorth(toInlineList(diff_b))
    print sh
    print "modus se short: %f"%mode(sh)
    print "modus klasicky: %i"%mode(toInlineList(diff_b))
    print "median: %i"%mode(toInlineList(diff_b))
    print "prumer: %f"%arithmeticMean(toInlineList(diff_b))
    # Green channel
    print "Green: "
    sh = shorth(toInlineList(diff_g))
    print sh
    print "modus se short: %f"%mode(sh)
    print "modus klasicky: %i"%mode(toInlineList(diff_g))
    print "median: %i"%mode(toInlineList(diff_g))
    print "prumer: %f"%arithmeticMean(toInlineList(diff_g))
    # Red channel
    print "Red: "
    sh = shorth(toInlineList(diff_r))
    print sh
    print "modus se short: %f"%mode(sh)
    print "modus klasicky: %i"%mode(toInlineList(diff_r))
    print "median: %i"%mode(toInlineList(diff_r))
    print "prumer: %f"%arithmeticMean(toInlineList(diff_r))


    # Kladne a zaporne cisla #############################
    negpos = negativePositive(diff)#sneak
    print negpos
    # csv
    #createCsvFile(negpos, ["delka bloku jeden za druhym - zacina se v kladnych cislech"], "negpos.csv")
    # csv
    createCsvFile([negpos], None, "negpos.csv")

    # pareto
    p = np.histogram(negpos, xrange(min(negpos), max(negpos)))
    paretoChart(p[0], p[1])

    # Pie Chart
    pieChart(p[0], p[1], 5)


    # Histogram
    #print np.histogram(diff, xrange(-255, 255))
    plt.hist(negpos, xrange(min(negpos), max(negpos)), label="", color="yellow")
    plt.legend()
    plt.title("Histogram")
    plt.xlabel("Block sizes")
    plt.ylabel("Count")
    plt.show()


    # Modus
    sh = shorth(negpos)
    print sh
    print "modus se short: %f"%mode(sh)
    print "modus klasicky: %i"%mode(negpos)
    print "median: %i"%mode(negpos)
    print "prumer: %f"%arithmeticMean(negpos)

def exploratoryStatistics(data, labels, more_data_for_compare = False):
    minimum = min(toInlineList(data) )
    maximum = max(toInlineList(data) )
    p = np.histogram(data, xrange(minimum, maximum))

    # Pareto
    paretoChart(p[0], p[1])

    # Pie Chart
    pieChart(p[0], p[1])

    # Histogram
    plt.hist(toInlineList(data), xrange(minimum, maximum), label="All channels", color="yellow")
    """
    plt.hist(toInlineList(diff_b), xrange(-255, 255), label="Blue channel", color="b", alpha=0.5, histtype='step')
    plt.hist(toInlineList(diff_g), xrange(-255, 255), label="Green channel", color="g", alpha=0.5, histtype='step')
    plt.hist(toInlineList(diff_r), xrange(-255, 255), label="Red channel", color="r", alpha=0.5, histtype='step')
    plt.hist(toInlineList(img_source), xrange(0, 255), label="original", color="black", alpha=0.5)
    """
    #plt.xlim([-255, 255])
    plt.legend()
    plt.title("Histogram")
    plt.xlabel("Differences value")
    plt.ylabel("Count")
    plt.show()


    # Modus
    sh = shorth(toInlineList(data))
    print sh
    print "mode with short: %f"%mode(sh)
    print "classical mode: %i"%mode(toInlineList(data))
    print "median: %i"%mode(toInlineList(data))
    print "avg: %f"%arithmeticMean(toInlineList(data))



