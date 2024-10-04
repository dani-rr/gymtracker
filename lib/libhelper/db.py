import psycopg2
import config
from pandas import DataFrame

def db_connect():
   global conn
   conn = psycopg2.connect(
      database=config.database, user=config.user, password=config.password, host=config.host, port=config.port
   )
   conn.autocommit = True
   global cursor 
   cursor = conn.cursor()

def get_names():
   cursor.execute('''SELECT DISTINCT "Name" FROM "TrainingLog"''')
   names = [name[0] for name in cursor.fetchall()]
   return names

def get_trainings(user):
    cursor.execute('''SELECT DISTINCT "Training" FROM "TrainingLog" WHERE "Name" = %s''', (user,))
    trainings = [training[0] for training in cursor.fetchall()]
    return trainings

def get_last_training(user, training):
   cursor.execute('''SELECT * FROM "TrainingLog" WHERE "Name" = %s AND "Training" = %s AND "Date" = (SELECT MAX("Date") FROM "TrainingLog" WHERE "Name" = %s AND "Training" = %s); ''', (user, training, user, training))
   training = cursor.fetchall()
   training_columns = get_columns_names()
   df_training = DataFrame(training)
   df_training.columns = training_columns
   return df_training

def get_columns_names():
   cursor.execute('''SELECT column_name FROM information_schema.columns WHERE table_name = 'TrainingLog' ORDER BY ordinal_position''')
   columns = [names[0] for names in cursor.fetchall()]
   return columns

# db_connect()
# df = get_last_training('User 1', 'Legs')


# # #Commit your changes in the database
# conn.commit()

# #Closing the connection
# conn.close()


