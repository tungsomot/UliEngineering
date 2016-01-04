#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from numpy.testing import assert_approx_equal, assert_allclose
from nose.tools import assert_equal, assert_true, raises, assert_less
from UliEngineering.SignalProcessing.FFT import *
from UliEngineering.SignalProcessing.Chunks import *
from nose_parameterized import parameterized
import concurrent.futures
import numpy as np

executor = concurrent.futures.ThreadPoolExecutor(4)

class TestFFT(object):
    def testBasicFFT(self):
        rand = np.random.random(1000) * 5.0 + 1.0 # +1: Artifical DC artifacts
        x, y = computeFFT(rand, 10.0)
        assert_equal(x.shape, (rand.shape[0] / 2, ))
        assert_equal(y.shape, (rand.shape[0] / 2, ))
        assert_equal(x.shape, y.shape)
        # Test if artifacts can be cut
        origLength = x.shape[0]
        x2, y2 = cutFFTDCArtifacts(x, y)
        assert_less(x2.shape[0], origLength)
        # Check if we can also pass a tuple
        x3, y3 = cutFFTDCArtifacts((x, y))
        assert_allclose(x2, x3)
        assert_allclose(y2, y3)

    def testCutDCArtifactsNoMinimum(self):
        # No minimum --> should return original array
        x = np.linspace(100, 1, 100)
        y = np.linspace(500, 5, 100)
        x2, y2 = cutFFTDCArtifacts(x, y)
        assert_allclose(x2, x)
        assert_allclose(y2, y)


    def testDominantFrequency(self):
        x = np.linspace(100, 199, 100) # Must not be equal to array index (so we check the fn doesnt just return indices)
        y = np.random.random(100)
        # Insert artificial peak
        y[32] = 8.0
        assert_equal(dominantFrequency(x, y), 132)
        # Check if we can also pass a tuple
        assert_equal(dominantFrequency((x, y)), 132)
        # Also check by threshold

    def testSelectFrequenciesByThreshold(self):
        x = np.linspace(100, 199, 100)
        y = np.random.random(100)
        y[32] = 8.0
        y[92] = 5.5
        y[98] = 4.5
        assert_allclose(selectFrequenciesByThreshold(x, y, 5.0), [132, 192])

    @parameterized.expand([
        ("With DC", False),
        ("Without DC", True),
    ])
    def testParallelFFTSum(self, name, removeDC):
        d = np.random.random(1000)
        y, nchunks = fixedSizeChunkGenerator(d, 100, 5)
        # Just test if it actually runs
        x, y = parallelFFTSum(executor, y, nchunks, 10.0, 100, removeDC=removeDC)
        if removeDC:
            assert_equal(x.shape[0], y.shape[0])
        else: # With DC
            assert_equal(x.shape[0], 50)
            assert_equal(y.shape[0], 50)
        assert_equal(x.shape, y.shape)