import psycopg2

conn = psycopg2.connect(
    host="192.168.1.212",      # change if you used another host
    port=5432,
    user="gymtracker",       # or whatever admin user you used for the seed script
    password="gymtracker",
    dbname="gymtracker"  # or the --target-db you passed
)
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM "TrainingLog";')
count = cur.fetchone()[0]
print(f"rows in TrainingLog: {count}")

cur.execute('SELECT "Name", "Training", "Date", "Reps" FROM "TrainingLog" ORDER BY "Name", "Date" LIMIT 5;')
for row in cur.fetchall():
    print(row)

cur.close()
conn.close()