import pandas
from dbo import DBO, TrainingData, IdealFunction, Result
from peewee import FloatField
from functools import reduce
import math
import plotly.express as px

def read_data():
    """
    Read training data and other data into dataframe and save in DB
    """
    training_data = pandas.read_csv("train.csv")

    for row in training_data.values:
        training_dto = TrainingData(
            x=row[0], y1=row[1], y2=row[2], y3=row[3], y4=row[4]
        )
        training_dto.save()

    ideal_functions = pandas.read_csv("ideal.csv")

    ideal_cols = {}
    for col in ideal_functions.columns:
        IdealFunction._meta.add_field(col, FloatField())
        ideal_cols.update({col: 0})

    dbo.db.create_tables([IdealFunction])  # call table create after fields added!

    for row in ideal_functions.values:
        for j, val in enumerate(
            row
        ):  # go through all entries in a row and update ideal values
            key = list(ideal_cols.keys())[j]
            ideal_cols.update({key: val})
        ideal_function = IdealFunction.create(ideal_cols)
        ideal_function.save()


if __name__ == "__main__":
    dbo = DBO()

    dbo.init()

    read_data()

    """
    Use least square to find ideal functions for training data
    """
    ideal_functions_query = IdealFunction.select()

    ideal_functions = []  # will be of shape (50, 400)

    # first let's bring ideal_functions into a format we can use
    for id_row in ideal_functions_query:
        ideal_function = []
        for i in range(50):
            ideal_function.append(id_row.__dict__["__data__"][f"y{i+1}"])
        ideal_functions.append(ideal_function)

    def sum_diffs(a, b):
        return [sum(x) for x in zip(a, b)]

    # aggregate sums for y1
    differences = []
    for indx, td_row in enumerate(TrainingData.select(TrainingData.x, TrainingData.y1)):
        diffs = [(td_row.y1 - y_val) ** 2 for y_val in ideal_functions[indx]]
        differences.append(diffs)

    sums = reduce(sum_diffs, differences)
    minimal_sum = min(sums)
    ideal_function_index_y1 = sums.index(minimal_sum)

    # aggregate sums for y2
    differences = []
    for indx, td_row in enumerate(TrainingData.select(TrainingData.x, TrainingData.y2)):
        diffs = [(td_row.y2 - y_val) ** 2 for y_val in ideal_functions[indx]]
        differences.append(diffs)

    sums = reduce(sum_diffs, differences)
    minimal_sum = min(sums)
    ideal_function_index_y2 = sums.index(minimal_sum)

    # aggregate sums for y3
    differences = []
    for indx, td_row in enumerate(TrainingData.select(TrainingData.x, TrainingData.y3)):
        diffs = [(td_row.y3 - y_val) ** 2 for y_val in ideal_functions[indx]]
        differences.append(diffs)

    sums = reduce(sum_diffs, differences)
    minimal_sum = min(sums)
    ideal_function_index_y3 = sums.index(minimal_sum)

    # aggregate sums for y4
    differences = []
    for indx, td_row in enumerate(TrainingData.select(TrainingData.x, TrainingData.y4)):
        diffs = [(td_row.y4 - y_val) ** 2 for y_val in ideal_functions[indx]]
        differences.append(diffs)

    sums = reduce(sum_diffs, differences)
    minimal_sum = min(sums)
    ideal_function_index_y4 = sums.index(minimal_sum)

    """
    Now compare test data to ideal functions and save ideal function with y delta
    """
    test_data = pandas.read_csv("test.csv")

    def find_ideal_match(point, function_indx):
        y_ideal = IdealFunction.get(IdealFunction.x == point[0])
        distance = (point[0] - y_ideal.x) ** 2 + (
            point[1] - y_ideal.__dict__["__data__"][f"y{function_indx+1}"]
        ) ** 2

        if distance < math.sqrt(2):
            result = Result(
                x=point[0],
                y=point[1],
                y_delta=distance,
                ideal_function=f"y{function_indx + 1}",
            )
            result.save()

    for point in test_data.values:
        find_ideal_match(point, ideal_function_index_y1)
        find_ideal_match(point, ideal_function_index_y2)
        find_ideal_match(point, ideal_function_index_y3)
        find_ideal_match(point, ideal_function_index_y4)

    p = px.scatter(test_data, x="x", y="y")

    p.show()

    for row in Result.select():
        print(
            f"x: {row.x}, y: {row.y}, y_delta: {row.y_delta} function: {row.ideal_function}"
        )

    dbo.destroy()
