from flask_sandman import create_app

app = create_app('sqlite+pysqlite:///tests/data/db.sqlite3')

def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
