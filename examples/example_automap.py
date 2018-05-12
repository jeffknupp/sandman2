from sandman2 import get_app

app = get_app('sqlite+pysqlite:///db.sqlite3')

if __name__ == '__main__':
    app.run(debug=True)
