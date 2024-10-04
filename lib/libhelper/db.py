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
   trainings_str = trainings.copy()
   cursor.execute('''SELECT DISTINCT "TrainingOrder" FROM "TrainingLog" WHERE "Name" = %s AND "Date" = (SELECT MAX("Date") FROM "TrainingLog" WHERE "Name" = %s)''', (user, user))
   last_training = cursor.fetchall()[0][0]

   if last_training != 3:
      cursor.execute('''SELECT DISTINCT "Training" FROM "TrainingLog" WHERE "TrainingOrder" = %s AND "Name" = %s''', (last_training + 1, user))
      next_training = cursor.fetchall()[0][0]
   else:
      cursor.execute('''SELECT DISTINCT "Training" FROM "TrainingLog" WHERE "TrainingOrder" = %s AND "Name" = %s''', (1, user))
      next_training = cursor.fetchall()[0][0]
   
   for idx, item in enumerate(trainings):
      if next_training in item:
         trainings_str[idx] = '▸ ' + next_training
   
   return trainings, trainings_str

def get_next_training(user):
   cursor.execute('''SELECT DISTINCT "TrainingOrder" FROM "TrainingLog" WHERE "Name" = %s AND "Date" = (SELECT MAX("Date") FROM "TrainingLog" WHERE "Name" = %s); ''', (user, user))
   next_training = cursor.fetchall()

   return next_training

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


