# Second_order_HHM_tagger.py
# Steve Wang
# 28 May 2021

# Script to tag a given sentence
import copy
import dataset
import statistics

###########################################################
# PRE-PROCESSING                                          #
###########################################################

train_set = dataset.load("train")
test_set = dataset.load("test")
q_dist = statistics.get_transition_distribution(train_set, smoothing="laplace")
e_dist = statistics.get_emission_distribution(train_set, smoothing="laplace")
trained_POS_tags = statistics.get_tags(train_set)
trained_words = statistics.get_words(train_set)
pos_tags = statistics.get_tags(test_set)
trigram_dist = statistics.get_trigram_distribution(train_set)

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
        if word not in trained_words:
            find_word = "UNKNOWN_WORD"
        else:
            find_word = word
        # For each word and each POS tag
        for pos_tag in lattice[i][1]:
            if pos_tag not in trained_POS_tags:
                find_pos_tag = "UNKNOWN"
            else:
                find_pos_tag = pos_tag
            if i == 0:
                # If it is the first word then pi is the probability of the tag on condition of the word
                lattice[i][1][pos_tag][0] = float(q_dist["START"][find_pos_tag]) * float(e_dist[find_word][find_pos_tag])
            elif i == 1:
                # If i is at the 2nd word then pi is the probability of the tag on condition of the previous word and "START"
                pi = None
                back_pointer = None
                temp = None
                for prev_values in lattice[i-1][1]:
                    if prev_values not in trained_POS_tags:
                        find_prev_values = "UNKNOWN"
                    else:
                        find_prev_values = prev_values
                    temp = float(lattice[i-1][1][prev_values][0]) * float(trigram_dist["START"][find_prev_values][find_pos_tag]) * float(e_dist[find_word][find_pos_tag])
                    if pi == None or temp > pi:
                        pi = temp
                        back_pointer = prev_values
                lattice[i][1][pos_tag][0] = pi
                lattice[i][1][pos_tag][1] = back_pointer
            else:
                pi = None
                back_pointer = None
                temp = None
                for prev_values in lattice[i - 1][1]:
                    if prev_values not in trained_POS_tags:
                        find_prev_values = "UNKNOWN"
                    else:
                        find_prev_values = prev_values
                    for pre_prev_value in lattice[i - 2][1]:
                        if pre_prev_value not in trained_POS_tags:
                            find_pre_prev_value = "UNKNOWN"
                        else:
                            find_pre_prev_value = pre_prev_value
                        temp = float(lattice[i-1][1][prev_values][0]) * float(trigram_dist[find_pre_prev_value][find_prev_values][find_pos_tag]) * float(e_dist[find_word][find_pos_tag])
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

for test_sentence_set in test_set:
    test_sentence_words = test_sentence_set.get('words')
    test_sentence_tags = test_sentence_set.get('tags')
    lattice = []
    row = {}
    for POS_tag in statistics.get_tags(test_set):
        row[POS_tag] = [0, None]
    for word in test_sentence_words:
        lattice.append([word, copy.deepcopy(row)])
    populate_lattice(lattice)
    tags = get_pos_tag(lattice)
    print(test_sentence_words)
    print(test_sentence_tags)
    print(tags)
    correct_tags = 0
    for i in range(len(test_sentence_words)):
        if test_sentence_tags[i] == tags[i]:
            correct_tags += 1
    accuracy = correct_tags / len(test_sentence_words)
    print(accuracy)
    accuracies.append(accuracy)

total_accuracy = sum(accuracies)/len(accuracies)
print(total_accuracy)