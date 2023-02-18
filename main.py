import pandas
from dbo import DBO, TrainingData, IdealFunction, Result
from peewee import FloatField
from functools import reduce
import math
from plotly.subplots import make_subplots
import plotly.graph_objects as go


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

    """
    Create plots to visualize data
    """

    fig = make_subplots(rows=2, cols=2, start_cell="top-left", subplot_titles=[
        "Test data",
        "Training data",
        "Ideal functions",
        "Matched test data and ideal functions"
    ])

    # test data
    fig.add_trace(go.Scatter(x=test_data["x"], y=test_data["y"], mode="markers", name="test_data"), row=1, col=1)

    # training data
    x_training = []
    y1_training = []
    y2_training = []
    y3_training = []
    y4_training = []

    for row in TrainingData.select():
        x_training.append(row.x)
        y1_training.append(row.y1)
        y2_training.append(row.y2)
        y3_training.append(row.y3)
        y4_training.append(row.y4)

    fig.add_trace(go.Scatter(x=x_training, y=y1_training, name="training_data_y1"), row=1, col=2)
    fig.add_trace(go.Scatter(x=x_training, y=y2_training, name="training_data_y2"), row=1, col=2)
    fig.add_trace(go.Scatter(x=x_training, y=y3_training, name="training_data_y3"), row=1, col=2)
    fig.add_trace(go.Scatter(x=x_training, y=y4_training, name="training_data_y4"), row=1, col=2)

    # ideal functions
    ideal_y1 = []
    ideal_y2 = []
    ideal_y3 = []
    ideal_y4 = []

    for row in IdealFunction.select():
        ideal_y1.append(row.__dict__["__data__"][f"y{ideal_function_index_y1+1}"])
        ideal_y2.append(row.__dict__["__data__"][f"y{ideal_function_index_y2+1}"])
        ideal_y3.append(row.__dict__["__data__"][f"y{ideal_function_index_y3+1}"])
        ideal_y4.append(row.__dict__["__data__"][f"y{ideal_function_index_y4+1}"])

    fig.add_trace(go.Scatter(x=x_training, y=ideal_y1, name="ideal_y1"), row=2, col=1)
    fig.add_trace(go.Scatter(x=x_training, y=ideal_y2, name="ideal_y2"), row=2, col=1)
    fig.add_trace(go.Scatter(x=x_training, y=ideal_y3, name="ideal_y3"), row=2, col=1)
    fig.add_trace(go.Scatter(x=x_training, y=ideal_y4, name="ideal_y4"), row=2, col=1)

    # matched test data and ideal functions
    matched_x = []
    matched_y = []
    for row in Result.select():
        matched_x.append(row.x)
        matched_y.append(row.y)

    fig.add_trace(go.Scatter(x=matched_x, y=matched_y, mode="markers", name="test_data"), row=2, col=2)
    fig.add_trace(go.Scatter(x=x_training, y=ideal_y1, name="ideal_y1"), row=2, col=2)
    fig.add_trace(go.Scatter(x=x_training, y=ideal_y2, name="ideal_y2"), row=2, col=2)
    fig.add_trace(go.Scatter(x=x_training, y=ideal_y3, name="ideal_y3"), row=2, col=2)
    fig.add_trace(go.Scatter(x=x_training, y=ideal_y4, name="ideal_y4"), row=2, col=2)

    fig.show()

    dbo.destroy()
