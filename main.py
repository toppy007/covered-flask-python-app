from website import create_app

app, mail = create_app()

if __name__ == '__main__':
    app.run(debug=True)
