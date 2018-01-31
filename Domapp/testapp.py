from flask import Flask, render_template

app = Flask(__name__)

@app.route("/") #tekst binnen ("") is adres in adresbalk om de pagina weer te geven. Kan alles zijn wat je wilt. dus ook afwijkend van de html naam
def home():
    return render_template("loginpage.html")

@app.route("/user1")
def user1():
    return render_template("home.html")

@app.route("/user2")
def user2():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)
