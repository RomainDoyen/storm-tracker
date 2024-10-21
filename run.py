import threading
from app import app
from app.functions.update import update_cyclones_data

if __name__ == '__main__':
    thread = threading.Thread(target=update_cyclones_data)
    thread.daemon = True
    thread.start()

    # app.run(debug=True, port=7000)
    app.run()
