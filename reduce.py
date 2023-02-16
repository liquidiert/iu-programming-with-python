from functools import reduce

if __name__=="__main__":
    to_reduce= [[8,7,6,4], [4,2,4,2], [9,1,3,3]]

    def sum_diffs(a, b):
        return [sum(x) for x in zip(a, b)]

    print(reduce(sum_diffs, to_reduce))