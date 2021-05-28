# calc_dist.py
# Scott Hallauer
# 28 May 2021

# Script to calculate the transition and emission distributions

import csv

train_filename = "GOV-ZA.50000TrainingSet.af.pos.full.csv"
test_filename = "GOV-ZA.5000TestSet.af.pos.full.csv"
t_dist_filename = "t_dist.csv"
e_dist_filename = "e_dist.csv"
train_set_size = 0.9

def get_tags(dataset):
  tags = ["START", "STOP"]
  for sentence in dataset:
    sentence_tags = sentence[1]
    for tag in sentence_tags:
      if tag not in tags:
        tags.append(tag)
  return tags

def get_counts(dataset):
  tags = get_tags(dataset)
  # initialise unigram_counts to 0
  unigram_counts = {}
  for tag in tags:
    unigram_counts[tag] = 0
  # initialise bigram_counts to 0
  bigram_counts = {}
  for tag_0 in tags:
    bigram_counts[tag_0] = {}
    for tag_1 in tags:
      bigram_counts[tag_0][tag_1] = 0
  # count occurrences of unigrams and bigrams in dataset
  for sentence in dataset:
    sentence_tags = sentence[1]
    tag_0 = "START"
    for i in range(len(sentence_tags) + 1):
      if i < len(sentence_tags):
        tag_1 = sentence_tags[i]
      else:
        tag_1 = "STOP"
      unigram_counts[tag_0] += 1
      unigram_counts[tag_1] += 1
      bigram_counts[tag_0][tag_1] += 1
      tag_0 = tag_1
  return (unigram_counts, bigram_counts)

# get corpus
input_file = open(train_filename)
input_reader = csv.reader(input_file, delimiter=',')

line_count = 0

corpus = []
corpus_words = {}
corpus_tags = {"START": 0, "STOP": 0}

sentence_words = []
sentence_tags = []

for row in input_reader:
  word = row[0]
  tag = row[1]
  if word == "" and tag == "":
    corpus.append([sentence_words, sentence_tags])
    corpus_tags["START"] += 1
    corpus_tags["STOP"] += 1
    sentence_words = []
    sentence_tags = []
    continue
  if line_count > 0:
    sentence_words.append(word)
    if word in corpus_words:
      corpus_words[word] += 1
    else:
      corpus_words[word] = 1
    sentence_tags.append(tag)
    if tag in corpus_tags:
      corpus_tags[tag] += 1
    else:
      corpus_tags[tag] = 1
  line_count += 1

cutoff = round(len(corpus) * train_set_size)

# get train_set and dev_set
train_set = corpus[:cutoff]
dev_set = corpus[cutoff:]

# calculate transition distribution
train_set_counts = get_counts(train_set)

output_file = open(t_dist_filename, mode="w")
output_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

output_writer.writerow(["tag_0", "tag_1", "p"])

for outer_tags in train_set_counts[1].items():
  tag_0 = outer_tags[0]
  for inner_tags in outer_tags[1].items():
    tag_1 = inner_tags[0]
    # count(tag_0, tag_1)
    bigram_count = inner_tags[1]
    # count(tag_0)
    unigram_count = train_set_counts[0][tag_0]
    # P(tag_1 | tag_0)
    p = bigram_count / unigram_count
    output_writer.writerow([tag_0, tag_1, p])