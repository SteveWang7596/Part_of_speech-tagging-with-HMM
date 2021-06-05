import dataset
import statistics

###########################################################
# PRE-PROCESSING                                          #
###########################################################

train_set = dataset.load("train")
test_set = dataset.load()
q_dist = statistics.get_transition_distribution(train_set, smoothing="laplace")
e_dist = statistics.get_emission_distribution(train_set, smoothing="laplace")

tags = statistics.get_tags(train_set)

for tag_1 in tags:
    for tag_2 in tags:
        print (q_dist[tag_1][tag_2])