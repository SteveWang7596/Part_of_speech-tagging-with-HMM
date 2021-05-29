# HHM_tagger.py
# Steve Wang
# 28 May 2021

# Script to tag a given sentence
import copy
import csv

q_dist_filename = "data/processed/q_dist.csv"
e_dist_filename = "data/processed/e_dist.csv"

POS_tags = []
q = {}
e = {}

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

#############################################
# word_1, {POS_1:[x,y], POS_2:[x,y], ...}   #
# word_2, {POS_1:[x,y], POS_2:[x,y], ...}   #
# word_3, {POS_1:[x,y], POS_2:[x,y], ...}   #
# ......                                    #
#############################################
# Where x is the pi value and y is the back pointer

lattice = []


def populate_lattice():
    # For each row in the lattice
    for i in range(lattice):
        word = lattice[i][0]
        # For each word and each POS tag
        for pos_tag in lattice[i][1]:
            if i == 0:
                # If it is the first word then pi is the probability of the tag on condition of the word
                lattice[i][1][pos_tag][0] = e[word][pos_tag]
            else:
                pi = None
                back_pointer = None
                temp = None
                for prev_values in lattice[i - 1][1]:
                    # Let temp value be pi of previous values * probability of current tag given previous tag *
                    # probablity of tag given word
                    temp = lattice[i - 1][1][prev_values][0] * q[prev_values][pos_tag] * e[word][pos_tag]
                    if pi == None or temp > pi:
                        pi = temp
                        back_pointer = prev_values
                lattice[i][1][pos_tag][0] = pi
                lattice[i][1][pos_tag][1] = prev_values


def get_pos_tag():
    tags = []
    tag = None
    for i in range(len(lattice), -1, -1):
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


def __init__(self, words):
    self.lattice = []
    row = {}
    for POS_tag in POS_tags:
        row[POS_tag] = [0, None]
    for word in words:
        self.lattice.append([word, copy.deepcopy(row)])
    populate_lattice()
    get_pos_tag()
