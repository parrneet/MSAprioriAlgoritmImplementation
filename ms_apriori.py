import sys
import re
import itertools
import copy

def read_input_data(input_file):
    #read input transaction data
    #store the transactions in a list of lists
    file = open(input_file,"r")
    global transactions
    global transaction_count
    for line in file:
        line =  line.strip()
        line =  line.replace("{"," ")
        line = line.replace("}"," ")
        transactions.append(map(int, line.split(",")))
        transaction_count+=1
    print("\n")
    # print ("transactions",transactions)
    print("\n")
    print ("transaction_count",transaction_count)
    print("\n")
    return transactions, transaction_count


def read_input_parameters(parameter_file):
    #read input prarameters (MIS)
    #store the MIS values in a dictionary
    #store the cannot be together values in a list of lists
    #store must_haves in a list
    file = open(parameter_file,"r")
    global mis
    global max_sup_diff
    global cannot_be_together
    global must_haves
    for line in file:
        if line.startswith('MIS'):
            line = line.replace("(", " ")
            line = line.replace(")", " ")
            item = [int(x) for x in re.findall(r'\d+', line)]
            min_sup = [float(x) for x in re.findall(r'\d*\.\d+', line)]
            mis[item[0]] = min_sup[0]
        if line.startswith('SDC'):
            max_sup_diff_input = re.findall(r'\d*\.\d+', line)
            max_sup_diff = float(max_sup_diff_input[0])
        if line.startswith('cannot_be_together'):
            line = line.replace("cannot_be_together:"," ")
            line = line.replace("{"," ")
            lists = [x for x in line.split("},")]
            cannot_be_together = []
            for i in range(0, len(lists)):
                cannot_be_together.append([int(y) for y in re.findall(r'\d+', lists[i])])

        if line.startswith('must-have'):
            must_haves = [int(x) for x in re.findall(r'\d+', line)]
    print("MIS values", mis)
    print("max_sup_diff", max_sup_diff)
    print("cannot_be_together", cannot_be_together)
    print("must_haves", must_haves)
    # must_haves =[]
    print("\n")


def ms_apriori(transactions, mis, max_sup_diff):
    #get itemset from dictionary
    itemset = list(mis.keys())
    items_count = len(itemset)
    #sort the items according to MIS values
    sorted_itemset = sorted(itemset, key = mis.get)
    print("Sorted Itemset",sorted_itemset)
    print("\n")

    #init-pass
    #generate seeds for candidate generation
    seeds_l = init_pass(sorted_itemset, transactions)

    freq_1_itemset = {}
    unfiltered_frequent_itemsets = {}

    # if support count of each seed > min support add to unfiltered_frequent_itemsets
    # if seed also in has one of must_haves add to Frequent itemsets
    for each in seeds_l:
        if( support_count[each]  >= mis[each]):

            unfiltered_frequent_itemsets[each] = int(support_count[each] * transaction_count)
            if len(must_haves) >0:
                if each in must_haves:
                    freq_1_itemset[each] = int(support_count[each] * transaction_count)
            else:
                print("No must have condition")
                freq_1_itemset[each] = int(support_count[each] * transaction_count)


    print("************* freq_1_itemset ***************\n", freq_1_itemset)
    print("************* unfiltered freq_1_itemset ***************\n", unfiltered_frequent_itemsets)

    output = "Frequent 1 - itemsets:\n"
    for each in freq_1_itemset:
        output += "\n\t"+str(freq_1_itemset[each])+": {"+ str(each)+"}"
    output += "\n\n\tTotal number of Frequent 1 sets: "+ str(len(freq_1_itemset)) +"\n\n"

    k = 2
    candidates_k = []
    unfiltered_frequent_itemsets = freq_1_itemset

    # if there are unfiltered_frequent_itemsets proceed to next level
    while( len(unfiltered_frequent_itemsets) != 0 ):
        print("\nStart of while loop")
        print"************* GENRATE CANDIDATES *************\n"
        if(k==2):
            candidates_k = level2_candidate_generation(seeds_l, max_sup_diff)
        else:
            candidates_k = ms_candidate_generation(unfiltered_frequent_itemsets, max_sup_diff)

        freq_k_itemset = []
        unfiltered_frequent_itemsets = []
        if candidates_k == [] :
            print("no candidates,break")
            break

        print"************* GENRATE COUNTS *************\n"
        candidate_counts = []
        tail_counts = []

        # if a candidate is present in a transaction, increment candidate count
        # if candidate minus 1st element (tail) is present in a transaction, increment tail count
        for each_c in candidates_k:
            tail_count = 0
            candidate_count = 0
            for each_t in transactions:
                if set(each_c).issubset(set(each_t)):
                    candidate_count += 1
                if set(each_c[1:]).issubset(set(each_t)):
                    tail_count += 1

            # if support of candidate >= min support of first item in candidate add to unfiltered_frequent_itemsets
            if float(candidate_count)/transaction_count >= mis[each_c[0]]:
                unfiltered_frequent_itemsets.append(each_c)
                # check conditions and add to output frequent itemset
                if check_conditions(each_c):
                    freq_k_itemset.append(each_c)
                    candidate_counts.append(candidate_count)
                    tail_counts.append(tail_count)

        candidate_count_map = (zip(freq_k_itemset,candidate_counts,tail_counts))

        #generate freq_k_itemset
        # print("************* GENRATE FREQUENT {} ITEMSETS *************\n".format(k))
        # print("frequent {} itemset after condition checks\n {}".format(k, freq_k_itemset))
        # print("unfiltered frequent {} itemset after condition checks\n {}".format(k, unfiltered_frequent_itemsets))

        print("frequent {} itemset size\n {}".format(k, len(freq_k_itemset)))
        print("unfiltered frequent {} itemset size\n {}".format(k, len(unfiltered_frequent_itemsets)))

        if len(freq_k_itemset) > 0 :
            output += "Frequent "+str(k)+"- itemsets:\n"
            count = 0
            for candidate, count, t_count in candidate_count_map:
                output += "\n\t"+str(count)+": {"+ str(candidate)+"}\n "
                output += "Tail count :"+ str(t_count)+"\n\n"
                count+=1
            output += "\n\n\tTotal number of Frequent "+ str(k) + " sets: "+ str(len(freq_k_itemset)) +"\n\n"

        k+=1

    return output

#define function init_pass
def init_pass(sorted_itemset, transactions):
    #Calculate support count for all items
    #store support count in a dictionary
    seeds_l = []
    global support_count
    for each in sorted_itemset:
        support_count[each] = float(sum( x.count(each) for x in transactions ))/transaction_count
    print("Support count for items",support_count)
    print("\n")
    # print("MIS values", mis)

    # generate seeds_l
    # find first item for which support >= min support and add to seeds
    for i in range(0,len(sorted_itemset)):
        if support_count[sorted_itemset[i]] >= mis[sorted_itemset[i]]:
            seeds_l.append(sorted_itemset[i])
            # print("{} added to seeds_l with sup {} compared to MIS(i) {}".format(sorted_itemset[i], support_count[sorted_itemset[i]], mis[sorted_itemset[i]]))
            break
    min_i = mis[sorted_itemset[i]]
    # for all items after the above item I , if support >= min support of I, add to seeds
    for j in range(i+1,len(sorted_itemset)):
        if support_count[sorted_itemset[j]] >= min_i:
            seeds_l.append(sorted_itemset[j])
            # print("{} added to seeds_l with sup {} compared to MIS(i) {}".format(sorted_itemset[j], support_count[sorted_itemset[j]], min_i))

    print("\n")
    print("seeds_l",seeds_l)
    print("\n")
    return seeds_l


def level2_candidate_generation(seeds, max_sup_diff):
    global support_count
    candidates_l2 = []
    # find first item for which support >= min support
    for i in range(0, len(seeds)):
        if support_count[seeds[i]] >= mis[seeds[i]] :

            # for each item J in seeds after above found item I,
            # if support of  J >= min support of I and the difference in support of J and I <= maximum support difference
            # add item to level 2 candidates
            for j in range(i+1, len(seeds)):
                sup_j = support_count[seeds[j]]
                sup_i = support_count[seeds[i]]

                if support_count[seeds[j]] >= mis[seeds[i]] and abs(round(sup_j - sup_i,10)) <= round(max_sup_diff,10)  :
                    # print("abs(sup_j - sup_i)",abs(sup_j - sup_i))
                    candidates_l2.append([seeds[i], seeds[j]])
    # print("**************** level 2 candidates generated ************\n", candidates_l2)
    print("**************** level 2 candidates generated size************\n", len(candidates_l2))
    return candidates_l2


def ms_candidate_generation(freq_k_itemset, max_sup_diff):
    candidates = []
    last_elem = []
    new_can =[]
    # freq_k_itemset_copy = copy.deepcopy(freq_k_itemset)
    for i in range(0, len(freq_k_itemset)):
        for j in range(0, len(freq_k_itemset)):
            # print("freq_k_itemset[i] freq_k_itemset[j]",freq_k_itemset[i][-1],freq_k_itemset[j][-1])
            if freq_k_itemset[i][:-1] == freq_k_itemset[j][:-1] and freq_k_itemset[i][-1] != freq_k_itemset[j][-1] :
                # print("last element check success")
                if freq_k_itemset[i][-1] < freq_k_itemset[j][-1] and  abs( round(support_count[freq_k_itemset[i][-1]] - support_count[freq_k_itemset[j][-1]],10) ) <= round(max_sup_diff,10) :
                    # print("add check success")
                    candidate = copy.deepcopy(freq_k_itemset[i])
                    candidate.append(copy.deepcopy(freq_k_itemset[j][-1]))
                    candidates.append(candidate)
                    # print("********** candidate added **********", candidate)
                    subsets = list(itertools.combinations(candidate, len(candidate)-1 ))
                    for each in subsets:
                        # print(" subset", list(each))
                        if candidate[0] in list(each) or mis[candidate[0]] == mis[candidate[1]]:
                            if list(each) not in freq_k_itemset:
                                # print("********** candidate removed **********", candidate)
                                candidates.remove(candidate)
                                break

    # print("**************** ms candidates generated ************\n", candidates)
    print("**************** ms candidates count ************\n", len(candidates))

    return candidates

def check_conditions(frequent_set):
    # print("*************** Check for conditions ***************\n")
    if len(cannot_be_together) > 0:
        for each_c_b_t in cannot_be_together:
            if set(each_c_b_t) <= set(frequent_set):
                print("cannot_be_together returned False")
                return False
    else:
        print("No cannot_be_together condition")

    if len(must_haves) == 0:
        print("No must_haves condition")
        return True
    for must_have in must_haves:
        if must_have in frequent_set:
            print("must_haves returned True")
            return True
    print("must_haves returned False")
    return False


transactions = []
transaction_count = 0
mis = {}
max_sup_diff = 0
support_count = {}
max_sup_diff = 0
cannot_be_together = []
must_haves = []

def __main__(argv):
    input_data = argv[1]
    parameter_data = argv[2]
    output_patterns = argv[3]
    transactions, transaction_count = read_input_data(input_data)
    read_input_parameters(parameter_data)
    output = ms_apriori(transactions, mis, max_sup_diff)
    output_file = open(output_patterns,"w+")
    output_file.write(output)

if __name__ == "__main__":
	__main__(sys.argv)
