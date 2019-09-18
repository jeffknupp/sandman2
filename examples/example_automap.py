from flask_sandman import create_app

app = create_app('sqlite+pysqlite:///db.sqlite3')

if __name__ == '__main__':
    app.run(debug=True)
