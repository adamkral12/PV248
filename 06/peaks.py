#!/usr/bin/python3

import struct
import numpy as np
import sys
import wave

stream = wave.open(sys.argv[1], 'r')

frames = stream.getnframes()
channelsSum = stream.getnchannels()
rate = stream.getframerate()
numOfMeasures = frames * channelsSum
# last window is ignored
winNum = int(frames / rate)
framesRead = stream.readframes(frames)

if stream.getsampwidth() == 1:
    # map to integer range 16
    fmt = "%iB" % numOfMeasures
elif stream.getsampwidth() == 2:
    # map to integer range 8
    fmt = "%ih" % numOfMeasures

stream.close()

unpackedStream = struct.unpack(fmt, framesRead)

# average channels in stereo
if channelsSum == 2:
    channels = [[] for time in range(channelsSum)]
    unpackedStreamAverage = []
    for i, v in enumerate(unpackedStream):
        part = i % channelsSum
        channels[part].append(v)
    for index in range(0, frames):
        unpackedStreamAverage.append(int((channels[0][index] + channels[1][index]) / 2))
    unpackedStream = unpackedStreamAverage

maxBoundary = None
minBoundary = None

for index in range(winNum):
    # start & end based on rate
    currentWindow = unpackedStream[(rate * index):rate + (rate * index)]
    rfft = np.fft.rfft(n=int(rate), a=currentWindow)
    resultFft = np.abs(rfft)

    divisor = (float(len(currentWindow))/rate)
    numerator = np.arange(1 + (len(currentWindow)/2))
    frequencies = numerator/divisor
    for i in range(len(resultFft)):
        # 20 times higher than average
        if 20 * np.mean(resultFft) < resultFft[i]:
            if minBoundary is None:
                minBoundary = frequencies[i]
            else:
                if minBoundary > frequencies[i]:
                    minBoundary = frequencies[i]
            if maxBoundary is None:
                maxBoundary = frequencies[i]
            else:
                if frequencies[i] > maxBoundary:
                    maxBoundary = frequencies[i]

if minBoundary is not None and maxBoundary is not None:
    print('low = {}, high = {}'.format(int(minBoundary), int(maxBoundary)))
else:
    print('no peaks')

