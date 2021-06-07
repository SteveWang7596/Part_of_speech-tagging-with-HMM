#!/bin/bash

# optimise_interpolation.sh
# Scott Hallauer
# 7 June 2021

# Script to run the HMM tagger with differnt lambda values for linear 
# interpolation smoothing and find the optimal value for the average accuracy
# across development sets. Cross validation is performed by splitting the 
# training data into 10 different combinations of training/development sets.

> data/results/interpolation_result.txt

for lambda in $(seq 0.0 0.05 1.0)
do 
  echo ""
  echo "lambda_0 = ${lambda}"
  echo ""
  k=1
  sum_accuracy=0
  for j in $(seq 0.0 0.1 0.9)
  do
    dev_start=${j}
    dev_end=`python3 -c "print(round(${j}+0.1,1))"`
    accuracy=`python3 tagger_1.py ${dev_start} ${dev_end} ${lambda}`
    sum_accuracy=`python3 -c "print(${sum_accuracy}+${accuracy})"`
    echo "Training Iteration ${k} of 10: ACCURACY = ${accuracy}"
    k=$((k+1))
  done
  average_accuracy=`python3 -c "print(${sum_accuracy}/10)"`
  echo "AVERAGE ACCURACY = ${average_accuracy}"
done