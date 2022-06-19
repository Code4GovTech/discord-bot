import psycopg2 as pg

conn = pg.connect(
  user="postgres", 
  password="passISstrong123",
  host="db.kowqkxjlhqsevcosjxkr.supabase.co",
  port="5432",
  database="postgres")

cur = conn.cursor()