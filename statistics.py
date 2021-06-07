# calc_dist.py
# Scott Hallauer
# 28 May 2021

# Script to calculate the transition (q) and emission (e) distributions of a dataset

import dataset
import csv

q_dist_filename = "data/processed/q_dist.csv"
e_dist_filename = "data/processed/e_dist.csv"

def get_words(dataset):
  """Return list of all unique words in the provided dataset."""
  words = []
  for sentence in dataset:
    sentence_words = sentence["words"]
    for word in sentence_words:
      if word not in words:
        words.append(word)
  return words

def get_tags(dataset):
  """Return list of all unique tags (including the special tags START and STOP) in the provided dataset."""
  tags = ["START", "STOP"]
  for sentence in dataset:
    sentence_tags = sentence["tags"]
    for tag in sentence_tags:
      if tag not in tags:
        tags.append(tag)
  return tags

def get_counts(dataset):
  """Return unigram and bigram tag counts, and word-tag pair counts in the provided dataset."""
  words = get_words(dataset)
  words.append("UNKNOWN_WORD")
  tags = get_tags(dataset)
  tags.append("UNKNOWN")
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
  # initialise token_count to 0
  token_count = 0
  # count occurrences in dataset
  for sentence in dataset:
    sentence_words = sentence["words"]
    sentence_tags = sentence["tags"]
    tag_0 = "START"
    token_count += 1
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
      token_count += 1
      tag_0 = tag_1
  unigram_tag_counts["UNKNOWN"] = 0
  for tag in tags:
    bigram_tag_counts["UNKNOWN"][tag] = 0
    bigram_tag_counts[tag]["UNKNOWN"] = 0
  return {
    "unigram_tag_counts": unigram_tag_counts,
    "bigram_tag_counts": bigram_tag_counts,
    "word_tag_pair_counts": word_tag_pair_counts,
    "token_count": token_count
  }

def get_trigram_counts(dataset):
  """Return trigram tag counts, and word-tag pair counts in the provided dataset."""
  #initialise trigram_tag_count to 0
  tags = get_tags(dataset)
  tags.append("UNKNOWN")
  trigram_tags_counts = {}
  for tri_tag_0 in tags:
    trigram_tags_counts[tri_tag_0] = {}
    for tri_tag_1 in tags:
      trigram_tags_counts[tri_tag_0][tri_tag_1] = {}
      for tri_tag_2 in tags:
        trigram_tags_counts[tri_tag_0][tri_tag_1][tri_tag_2] = 0
  for sentence in dataset:
    sentence_tags = sentence["tags"]
    tag_0 = "START"
    for i in range(len(sentence_tags)):
      tag_1 = sentence_tags[i]
      if i < (len(sentence_tags)-1):
        tag_2 = sentence_tags[i+1]
      else:
        tag_2 = "STOP"
      trigram_tags_counts[tag_0][tag_1][tag_2] += 1
      tag_0 = tag_1
  return trigram_tags_counts

def get_transition_distribution(dataset, smoothing = "none", lambdas=[0.5,0.5]):
  """Return the transition (q) distribution for the provided dataset."""
  # check parameters
  if sum(lambdas) != 1.0:
    raise ValueError("The provided lambda values for linear interpolation smoothing do not sum to 1.0.")
  # get dataset counts
  tags = get_tags(dataset)
  tags.append("UNKNOWN")
  counts = get_counts(dataset)
  token_count = counts["token_count"]
  q_dist = {}
  for tag_0 in tags:
    q_dist[tag_0] = {}
    unigram_tag_0_count = counts["unigram_tag_counts"][tag_0] # c(tag_0)
    for tag_1 in tags:
      unigram_tag_1_count = counts["unigram_tag_counts"][tag_1] # c(tag_1)
      bigram_tag_count = counts["bigram_tag_counts"][tag_0][tag_1] # c(tag_0, tag_1)
      # Laplace smoothing
      if smoothing == "laplace":
        p = (bigram_tag_count + 1) / (unigram_tag_0_count + len(tags))
      # Linear interpolation smoothing
      elif smoothing == "interpolation":
        p = lambdas[0] * (bigram_tag_count / unigram_tag_0_count) + lambdas[1] * (unigram_tag_1_count / token_count)
      # No smoothing
      else:
        p = bigram_tag_count / unigram_tag_0_count
      q_dist[tag_0][tag_1] = p
  return q_dist

def get_emission_distribution(dataset, smoothing = "none"):
  """Return the emission (e) distribution for the provided dataset."""
  words = get_words(dataset)
  words.append("UNKNOWN_WORD")
  tags = get_tags(dataset)
  tags.append("UNKNOWN")
  counts = get_counts(dataset)
  e_dist = {}
  for word in words:
    e_dist[word] = {}
    for tag in tags:
      unigram_tag_count = counts["unigram_tag_counts"][tag] # c(tag)
      word_tag_pair_count = counts["word_tag_pair_counts"][word][tag] # c(word, tag)
      # Laplace smoothing
      if smoothing == "laplace":
        p = (word_tag_pair_count + 1) / (unigram_tag_count + len(tags))
      # No smoothing
      else:
        p = word_tag_pair_count / unigram_tag_count
      e_dist[word][tag] = p
  return e_dist

def get_trigram_distribution(dataset):
  """"Return the transition (q) distibiton for the provided dataset."""
  tags = get_tags(dataset)
  tags.append("UNKNOWN")
  counts = get_counts(dataset)
  tri_counts = get_trigram_counts(dataset)
  tri_q_dist = {}
  for tag_0 in tags:
    tri_q_dist[tag_0] = {}
    for tag_1 in tags:
      tri_q_dist[tag_0][tag_1] = {}
      bigram_tag_count = counts["bigram_tag_counts"][tag_0][tag_1]
      for tag_2 in tags:
        trigram_count = tri_counts[tag_0][tag_1][tag_2]
        p = (trigram_count + 1) / (bigram_tag_count + len(tags)) # Probability of tag_2 give tag_0,tag_1
        tri_q_dist[tag_0][tag_1][tag_2] = p
  return tri_q_dist


def main():
  """Calculate and output transition and emission distributions for the selected dataset."""
  # get training set
  train_set = dataset.subset(dataset.load("train"), 0.0, 1.0)
  # calculate and output transition distribution
  q_dist = get_transition_distribution(train_set, smoothing="laplace")
  output_file = open(q_dist_filename, mode="w")
  output_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
  output_writer.writerow(["tag_0", "tag_1", "p"])
  for outer_set in q_dist.items():
    tag_0 = outer_set[0]
    for inner_set in outer_set[1].items():
      tag_1 = inner_set[0]
      p = inner_set[1]
      output_writer.writerow([tag_0, tag_1, p])
  # calculate and output emission distribution
  e_dist = get_emission_distribution(train_set, smoothing="laplace")
  output_file = open(e_dist_filename, mode="w")
  output_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
  output_writer.writerow(["word", "tag", "p"])
  for outer_set in e_dist.items():
    word = outer_set[0]
    for inner_set in outer_set[1].items():
      tag = inner_set[0]
      p = inner_set[1]
      output_writer.writerow([word, tag, p])

if __name__ == "__main__":
  main()