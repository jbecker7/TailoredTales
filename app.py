from flask import Flask, request, render_template

app = Flask(__name__)
if __name__ == '__main__':
    app.run(debug=False)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Your POST handling logic here
        pass
    return render_template("index.html")
