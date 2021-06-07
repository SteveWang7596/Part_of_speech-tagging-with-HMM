# Part of Speech Tagging with Hidden Markov Models

## Overview

**dataset.py** is used to process the raw data files.

**statistics.py** is used to calculate the transition and emission 
distributions.

**tagger_1.py** is used to run the first-order HMM.

**tagger_2.py** is used to run the second-order HMM.

**optimise_interpolation.sh** is used to test multiple values for lambda 
parameters in linear interpolation smoothing

## Execution

Run `python3 tagger_1.py` to excute first-order HMM. Set parameters in the 
"PRE-PROCESSING" section at the top of the script, such as which datasets to use
for training and evaluation, as well as which smoothing method to and lambda 
values use.

Run `python3 tagger_2.py` to excute second-order HMM. Set parameters in the same
way as described above.

Run `bash optimise_interpolation.sh` to evaluate average accuracy for different
values of lambda parameters for linear interpolation smoothing for the first-
order HMM.

## Output

Output from **tagger_1.py** and **tagger_2.py** are in data/output/.

Output from **optimise_interpolation.sh** is in data/results/.