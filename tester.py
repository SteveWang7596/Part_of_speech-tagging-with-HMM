import csv

import dataset
import statistics

###########################################################
# PRE-PROCESSING                                          #
###########################################################

test_filename = "data/raw/tester.csv"

train_set = dataset.load("train")
test_set = dataset.load()
q_dist = statistics.get_transition_distribution(train_set, smoothing="laplace")
e_dist = statistics.get_emission_distribution(train_set, smoothing="laplace")

def load():
  """Return the requested dataset as a list of word-tag paired sentences."""
  with open(test_filename) as input_file:
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

data = load()
#tri_gram_counts = statistics.get_trigram_counts(data)
tri_gram_distrbution = statistics.get_trigram_distribution(data)
print(tri_gram_distrbution)
