# calc_dist.py
# Scott Hallauer
# 28 May 2021

# Script to calculate the transition (q) and emission (e) distributions

import dataset
import csv

q_dist_filename = "data/processed/q_dist.csv"
e_dist_filename = "data/processed/e_dist.csv"

def get_words(dataset):
  words = []
  for sentence in dataset:
    sentence_words = sentence["words"]
    for word in sentence_words:
      if word not in words:
        words.append(word)
  return words

def get_tags(dataset):
  tags = ["START", "STOP"]
  for sentence in dataset:
    sentence_tags = sentence["tags"]
    for tag in sentence_tags:
      if tag not in tags:
        tags.append(tag)
  return tags

def get_counts(dataset):
  words = get_words(dataset)
  tags = get_tags(dataset)
  # initialise unigram_tag_counts to 0
  unigram_tag_counts = {}
  for tag in tags:
    unigram_tag_counts[tag] = 0
  # initialise bigram_tag_counts to 0
  bigram_tag_counts = {}
  for tag_0 in tags:
    bigram_tag_counts[tag_0] = {}
    for tag_1 in tags:
      bigram_tag_counts[tag_0][tag_1] = 0
  # initialise word_tag_pair_counts to 0
  word_tag_pair_counts = {}
  for word in words:
    word_tag_pair_counts[word] = {}
    for tag in tags:
      word_tag_pair_counts[word][tag] = 0
  # calculate size of vocabulary (number of unique words)
  vocabulary_size = len(words)
  # calculate size of tagset (number of unique POS tags)
  tagset_size = len(tags)
  # count occurrences in dataset
  for sentence in dataset:
    sentence_words = sentence["words"]
    sentence_tags = sentence["tags"]
    tag_0 = "START"
    for i in range(len(sentence_tags) + 1):
      if i < len(sentence_tags):
        tag_1 = sentence_tags[i]
        word_1 = sentence_words[i]
        word_tag_pair_counts[word_1][tag_1] += 1
      else:
        tag_1 = "STOP"
      unigram_tag_counts[tag_0] += 1
      unigram_tag_counts[tag_1] += 1
      bigram_tag_counts[tag_0][tag_1] += 1
      tag_0 = tag_1
  return {
    "unigram_tag_counts": unigram_tag_counts, 
    "bigram_tag_counts": bigram_tag_counts, 
    "word_tag_pair_counts": word_tag_pair_counts, 
    "vocabulary_size": vocabulary_size, 
    "tagset_size": tagset_size
  }

# get training set
corpus = dataset.load("train")
train_set = dataset.subset(corpus, 0.0, 1.0)
train_set_counts = get_counts(train_set)

# calculate and output transition distribution
output_file = open(q_dist_filename, mode="w")
output_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

output_writer.writerow(["tag_0", "tag_1", "p"])

for outer_set in train_set_counts["bigram_tag_counts"].items():
  tag_0 = outer_set[0]
  for inner_set in outer_set[1].items():
    tag_1 = inner_set[0]
    bigram_tag_count = inner_set[1] + 1 # c(tag_0, tag_1) + 1 (Laplace smoothing)
    unigram_tag_count = train_set_counts["unigram_tag_counts"][tag_0] + train_set_counts["tagset_size"] # c(tag_0) + T (Laplace smoothing)
    p = bigram_tag_count / unigram_tag_count # P(tag_1 | tag_0) (Laplace smoothing)
    output_writer.writerow([tag_0, tag_1, p])

# calculate and output emission distribution
output_file = open(e_dist_filename, mode="w")
output_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

output_writer.writerow(["word", "tag", "p"])

for outer_set in train_set_counts["word_tag_pair_counts"].items():
  word = outer_set[0]
  for inner_set in outer_set[1].items():
    tag = inner_set[0]
    word_tag_pair_count = inner_set[1] + 1 # c(word, tag) + 1 (Laplace smoothing)
    unigram_tag_count = train_set_counts["unigram_tag_counts"][tag] + train_set_counts["tagset_size"] # c(tag) + T (Laplace smoothing)
    p = word_tag_pair_count / unigram_tag_count # P(word | tag) (Laplace smoothing)
    output_writer.writerow([word, tag, p])