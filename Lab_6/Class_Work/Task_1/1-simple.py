from microdot import Microdot

app = Microdot()

@app.route("/")
def index(request):
    return "Microdot is working on ESP32!"

app.run(port=80)