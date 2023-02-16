import pandas
from dbo import DBO, TrainingData, IdealFunction
from peewee import FloatField
from functools import reduce

if __name__ == "__main__":
    dbo = DBO()

    dbo.init()

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
        for j, val in enumerate(row):  # go through all entries in a row and update ideal values
            key = list(ideal_cols.keys())[j]
            ideal_cols.update({key: val})
        ideal_function = IdealFunction.create(ideal_cols)
        ideal_function.save()

    """
    Use least square to find ideal functions for training data
    """
    ideal_functions_query = IdealFunction.select()

    ideal_functions = []  # will be of shape (400, 50)

    # first let's bring ideal_functioins into a format we can use
    for id_row in ideal_functions_query:
        ideal_function = []
        for i in range(50):
            ideal_function.append(id_row.__dict__["__data__"][f"y{i+1}"])
        ideal_functions.append(ideal_function)

    def sum_diffs(a, b):
        return [sum(x) for x in zip(a, b)]

    # aggregate sums for y1
    differences_y1 = []
    for indx, td_row in enumerate(TrainingData.select(TrainingData.x, TrainingData.y1)):
        differences = [(td_row.y1 - y_val)**2 for y_val in ideal_functions[indx]]
        differences_y1.append(differences)

    sums_y1 = reduce(sum_diffs, differences_y1)
    minimal_sum_y1 = min(sums_y1)
    print(sums_y1.index(minimal_sum_y1))


    dbo.destroy()
