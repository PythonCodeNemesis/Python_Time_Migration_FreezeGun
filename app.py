from flask import Flask, jsonify, request
from freezegun import freeze_time
import datetime
import sqlite3

app = Flask(__name__)

# Connect to the database
conn = sqlite3.connect('example.db')
c = conn.cursor()

# Create a table to store the posts
c.execute('''CREATE TABLE IF NOT EXISTS posts
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              payload TEXT,
              created_at TIMESTAMP)''')
conn.commit()

# Define a function to insert a post into the database
def insert_post(payload):
    now = datetime.datetime.now()
    c.execute("INSERT INTO posts (payload, created_at) VALUES (?, ?)", (payload, now))
    conn.commit()

# Define a route to accept POST requests and insert the payload into the database
@app.route('/post', methods=['POST'])
def post():
    payload = request.json['payload']
    insert_post(payload)
    return jsonify({'message': 'Post created successfully'})

# Define a route to query the posts from the database
@app.route('/posts', methods=['GET'])
def get_posts():
    with app.app_context():
        c.execute("SELECT * FROM posts")
        rows = c.fetchall()
        result = [{'id': row[0], 'payload': row[1], 'created_at': row[2]} for row in rows]
        return jsonify(result)

# Schedule three posts to be sent at different times
@freeze_time('2022-01-01')
def schedule_post_1():
    payload = {'payload': 'January payload'}
    with app.test_client() as client:
        client.post('/post', json=payload)

@freeze_time('2022-02-01')
def schedule_post_2():
    payload = {'payload': 'February payload'}
    with app.test_client() as client:
        client.post('/post', json=payload)

@freeze_time('2022-03-01')
def schedule_post_3():
    payload = {'payload': 'March payload'}
    with app.test_client() as client:
        client.post('/post', json=payload)

# Run the scheduled posts
schedule_post_1()
schedule_post_2()
schedule_post_3()

# Query the posts at different times
with freeze_time('2022-01-01'):
    with app.app_context():
        print(get_posts().get_json())
with freeze_time('2022-02-15'):
    with app.app_context():
        print(get_posts().get_json())
with freeze_time('2022-03-30'):
    with app.app_context():
        print(get_posts().get_json())

if __name__ == '__main__':
    app.run()
