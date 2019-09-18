from user_models import User, Blog, Post
from flask_sandman import create_app

app = create_app('sqlite+pysqlite:///blog.sqlite3', include_models=[User, Blog, Post])

if __name__ == '__main__':
    app.run(debug=True)
