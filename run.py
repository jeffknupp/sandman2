from sandman2 import get_app

app = get_app('sqlite+pysqlite:///tests/data/db.sqlite3')

def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
