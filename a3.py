"""
===========================
A3
Naive Bayes bag-of-Word (NB-BOW)

Victor Soledad
===========================
"""
print(__doc__)

import sys
import numpy
from a3_functions import *

# Read Training Data and skip first line
traindata = readData("covid_training.tsv", True)
original_vocabulary, filtered_vocabulary, data_count, factual_count = parseTraining(traindata)

# Read Test Data
testdata = readData("covid_test_public.tsv", False)

# Analyze test data with both vocabs
analyzeData(testdata, original_vocabulary, data_count, factual_count, 0.01, "NB-BOW-OV")
analyzeData(testdata, filtered_vocabulary, data_count, factual_count, 0.01, "NB-BOW-FV")

# print(original_vocabulary)
# print(filtered_vocabulary)