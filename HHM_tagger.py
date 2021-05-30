# HHM_tagger.py
# Steve Wang
# 28 May 2021

# Script to tag a given sentence
import copy
import csv

q_dist_filename = "data/processed/q_dist.csv"
e_dist_filename = "data/processed/e_dist.csv"
test_filename = "data/raw/GOV-ZA.5000TestSet.af.pos.full.csv"

POS_tags = []
q = {}
e = {}

###########################################################
# PRE-PROCESSING                                          #
###########################################################

input_tag_name = open(q_dist_filename)
input_tag_reader = csv.reader(input_tag_name, delimiter=',')
next(input_tag_reader)

for line in input_tag_reader:
    tag_0 = line[0]
    tag_1 = line[1]
    if tag_0 not in POS_tags:
        POS_tags.append(tag_0)
    if tag_1 not in POS_tags:
        POS_tags.append(tag_1)

input_file_q = open(q_dist_filename)
input_q_reader = csv.reader(input_file_q, delimiter=',')
next(input_q_reader)

for line in input_q_reader:
    if line[0] not in q:
        q[line[0]] = {}
    q[line[0]][line[1]] = line[2]

input_file_e = open(e_dist_filename)
input_e_reader = csv.reader(input_file_e, delimiter=',')
next(input_e_reader)

for line in input_e_reader:
    if line[0] not in e:
        e[line[0]] = {}
    e[line[0]][line[1]] = line[2]

input_test_file = open(test_filename)
input_test_reader = csv.reader(input_test_file, delimiter=",")
next(input_test_reader)

test_sentences = []

sentence_words = []
sentence_tags = []

for line in input_test_reader:
    word = line[0]
    tag = line[1]
    if word == "" and tag == "":
        test_sentences.append([sentence_words, sentence_tags])
        sentence_words = []
        sentence_tags = []
        continue
    sentence_words.append(word)
    sentence_tags.append(tag)

#############################################
# word_1, {POS_1:[x,y], POS_2:[x,y], ...}   #
# word_2, {POS_1:[x,y], POS_2:[x,y], ...}   #
# word_3, {POS_1:[x,y], POS_2:[x,y], ...}   #
# ......                                    #
#############################################
# Where x is the pi value and y is the back pointer


def populate_lattice(lattice):
    # For each row in the lattice
    for i in range(len(lattice)):
        word = lattice[i][0]
        # For each word and each POS tag
        for pos_tag in lattice[i][1]:
            if i == 0:
                # If it is the first word then pi is the probability of the tag on condition of the word
                lattice[i][1][pos_tag][0] = float(e[word][pos_tag])
            else:
                pi = None
                back_pointer = None
                temp = None
                for prev_values in lattice[i - 1][1]:
                    # Let temp value be pi of previous values * probability of current tag given previous tag *
                    # probablity of tag given word
                    print(word)
                    temp = float(lattice[i - 1][1][prev_values][0]) * float(q[prev_values][pos_tag]) * float(e[word][pos_tag])
                    if pi == None or temp > pi:
                        pi = temp
                        back_pointer = prev_values
                lattice[i][1][pos_tag][0] = pi
                lattice[i][1][pos_tag][1] = back_pointer


def get_pos_tag(lattice):
    tags = []
    tag = None
    for i in range(len(lattice)-1, -1, -1):
        if tag == None:
            max = None
            guess = None
            for k in lattice[i][1]:
                if max == None or lattice[i][1][k][0] > max:
                    max = lattice[i][1][k][0]
                    tag = lattice[i][1][k][1]
                    guess = k
            tags.append(guess)
        else:
            tags.append(tag)
            tag = lattice[i][1][tag][1]
    tags.reverse()
    return tags

accuracies = []

for test_sentence in test_sentences:
    lattice = []
    row = {}
    for POS_tag in POS_tags:
        row[POS_tag] = [0, None]
    for word in test_sentence[0]:
        lattice.append([word, copy.deepcopy(row)])
    populate_lattice(lattice)
    tags = get_pos_tag(lattice)
    correct_tags = 0
    for i in range(len(test_sentence[0])):
        if test_sentence[1][i] == tags[i]:
            correct_tags += 1
    accuracy = correct_tags / len(test_sentence[0])
    accuracies.append(accuracy)

