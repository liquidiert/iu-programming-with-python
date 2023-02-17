from peewee import *

class DBO:
    db = SqliteDatabase("training_data.sqlite")

    def init(self):
        self.db.connect()
        self.db.create_tables([TrainingData, Result])

    def destroy(self):
        for row in TrainingData.select():
            row.delete_instance()

        for row in IdealFunction.select():
            row.delete_instance()

        self.db.close()

class TrainingData(Model):
    """
    A model class holding parameters for training data functions
    """

    x = FloatField()
    y1 = FloatField()
    y2 = FloatField()
    y3 = FloatField()
    y4 = FloatField()

    class Meta:
        database = DBO.db

class IdealFunction(Model):
    """
    A model class holding parameters for ideal functions
    """

    @classmethod
    def create(cls, args):
        instance = cls()
        for entry in args:
            setattr(instance, entry, args[entry])
        return instance

    class Meta:
        database = DBO.db

class Result(Model):
    """
    A model class holding the results of an ideal function
    """

    x = FloatField()
    y = FloatField()
    y_delta = FloatField()
    ideal_function = CharField(max_length=3)

    class Meta:
        database = DBO.db
