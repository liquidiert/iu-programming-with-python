import pandas
from dbo import DBO, TrainingData, IdealFunction
from peewee import FloatField

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

    for td_row in TrainingData.select(TrainingData.x, TrainingData.y1):
        for i in range(50):
            for id_row in IdealFunction.select(IdealFunction.x, IdealFunction.y1):
                print(id_row.x)



    dbo.destroy()
