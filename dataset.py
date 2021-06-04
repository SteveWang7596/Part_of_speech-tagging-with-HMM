# dataset.py
# Scott Hallauer
# 3 June 2021

# Script to read in CSV datasets. Includes functionality to divide dataset into 
# training and development sets.

import csv
import math

train_filename = "data/raw/GOV-ZA.50000TrainingSet.af.pos.full.csv"
test_filename = "data/raw/GOV-ZA.5000TestSet.af.pos.full.csv"

def load(name = "train"):
  """Return the requested dataset as a list of word-tag paired sentences."""
  if name == "train":
    selected_filename = train_filename
  else:
    selected_filename = test_filename
  with open(selected_filename) as input_file:
    input_reader = csv.reader(input_file, delimiter=',')
    dataset = []
    sentence_words = []
    sentence_tags = []
    line_count = 0
    for row in input_reader:
      word = row[0]
      tag = row[1]
      if word == "" and tag == "":
        dataset.append({"words": sentence_words, "tags": sentence_tags})
        sentence_words = []
        sentence_tags = []
        continue
      if line_count > 0:
        sentence_words.append(word)
        sentence_tags.append(tag)
      line_count += 1
    return dataset

def subset(dataset, start_proportion = 0.0, end_proportion = 1.0):
  """Return a proportionate subset of the provided dataset."""
  start_idx = math.floor(len(dataset) * start_proportion)
  end_idx = math.floor(len(dataset) * end_proportion)
  return dataset[start_idx:end_idx]