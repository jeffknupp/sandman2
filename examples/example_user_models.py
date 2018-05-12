from user_models import User, Blog, Post
from sandman2 import get_app

app = get_app('sqlite+pysqlite:///blog.sqlite3', user_models=[User, Blog, Post])

if __name__ == '__main__':
    app.run(debug=True)
