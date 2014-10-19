from sandman2 import get_app, reflect_all

app = get_app('config.settings')

def main():
    with app.app_context():
        reflect_all()
    app.run(debug=True)


if __name__ == '__main__':
    main()
