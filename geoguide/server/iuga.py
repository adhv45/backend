import pandas as pd
import datetime
from random import randint
from geoguide.server import app, diversity
from geoguide.server.geoguide.helpers import path_to_hdf

CHUNKSIZE = app.config['CHUNKSIZE']


def get_distances_of(elements, k, distance_by_id):
    my_distances = [distance_by_id[elements[i]] for i in range(k)]
    return my_distances


def make_new_records(elements, new_element, k, records):
    output = {}
    for i in range(k):
        output[i] = elements[i]
    replacement = randint(0, k - 1)
    output[replacement] = records[new_element]
    return output


def run_iuga(input_g, k_value, time_limit, lowest_acceptable_similarity, dataset, filtered_points=[]):
    # parameters
    k = k_value

    # indexing file
    # should the algorithm stop if it reaches the end of the index (i.e.,
    # scanning all records once)
    stop_visiting_once = False

    # Note that in case of user group analysis, each group is a record. In
    # case of spatiotemporal data, each geo point is a record.

    # variables
    # the ID of current k records will be recorded in this object.
    current_records = {}

    # ths ID of next potential k records will be recorded in this object.
    new_records = {}

    # total execution time
    total_time = 0.0

    # dimensions
    similarities = {}
    distances = {}

    # read input data frame
    store = pd.HDFStore(path_to_hdf(dataset))
    for df in store.select('relation', chunksize=CHUNKSIZE):
        if filtered_points:
            df = df[(df['id_a'].isin(filtered_points)) & (df['id_b'].isin(filtered_points))]
        for row in df.itertuples():
            if int(row[1]) > input_g:
                break
            to_id = int(row[2])
            if to_id == input_g:
                continue
            similarities[to_id] = float(row[3])
            distances[to_id] = float(row[4])
    store.close()

    # sorting similarities and distances in descending order
    similarities_sorted = sorted(
        similarities.items(), key=lambda x: x[1], reverse=True)
    distances_sorted = sorted(
        distances.items(), key=lambda x: x[1], reverse=True)

    # begin - prepare lists for easy retrieval
    records = {}
    similarity_by_id = {}
    distance_by_id = {}

    cnt = 0
    for value in similarities_sorted:
        records[cnt] = value[0]
        similarity_by_id[value[0]] = value[1]
        cnt += 1

    for value in distances_sorted:
        distance_by_id[value[0]] = value[1]
    # begin - prepare lists for easy retrieval

    # print(len(records), "records retrieved and indexed.")

    # begin - retrieval functions

    # end - retrieval functions

    # initialization by k most similar records
    for i in range(k):
        current_records[i] = records[i]

    # print("begin:", show(current_records, k, similarity_by_id, distance_by_id))

    # greedy algorithm
    pointer = k - 1
    nb_iterations = 0
    pointer_limit = len(records) - 1
    while total_time < time_limit and pointer < pointer_limit:
        nb_iterations += 1
        pointer += 1
        redundancy_flag = False
        for i in range(k):
            if current_records[i] == records[pointer]:
                redundancy_flag = True
                break
        if redundancy_flag:
            continue
        begin_time = datetime.datetime.now()
        current_distances = get_distances_of(current_records, k, distance_by_id)
        current_diversity = diversity.diversity(current_distances)
        new_records = make_new_records(current_records, pointer, k, records)
        new_distances = get_distances_of(new_records, k, distance_by_id)
        new_diversity = diversity.diversity(new_distances)
        if new_diversity > current_diversity:
            current_records = new_records
        end_time = datetime.datetime.now()
        duration = (end_time - begin_time).microseconds / 1000.0
        total_time += duration
        if similarity_by_id[records[pointer]] < lowest_acceptable_similarity:
            if stop_visiting_once:
                break
            else:
                pointer = k

    # print("end:", show(current_records, k, similarity_by_id, distance_by_id))
    # print("execution time (ms)", total_time)
    # print("# iterations", nb_iterations)

    min_similarity = 1
    dicToArray = []
    for i in range(k):
        if similarity_by_id[current_records[i]] < min_similarity:
            min_similarity = similarity_by_id[current_records[i]]
        dicToArray.append(current_records[i])
    my_distances = get_distances_of(current_records, k, distance_by_id)
    my_diversity = diversity.diversity(my_distances)
    return [min_similarity, round(my_diversity, 2), sorted(dicToArray)]
