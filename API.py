import datetime
from base64 import b64encode
from io import BytesIO
import matplotlib.pyplot as plt
import pyrebase
from flask import Flask, jsonify
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

app = Flask(__name__)
config = {
    "apiKey": "",
    "authDomain": "",
    "databaseURL": "",
    "projectId": "",
    "storageBucket": ""
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

@app.route("/", methods=['GET'])
def home():
    return "Hello World!"

@app.route("/users/<user_id>/is-admin", methods=['GET'])
def user(user_id):
    All_user = db.child('data/users').get().val()
    if user_id in All_user:
        user_data = db.child('data/users/' + user_id).get().val()
        user_admin = db.child('data/users/' + user_id + '/' + 'Admin').get().val()
        if user_admin == 'True':
            return jsonify(
                {'UserID': user_id,
                 'is-admin': 'True'}), 200
        else:
            return jsonify(
                {'UserID': user_id,
                 'is-admin': 'False'}), 200
    else:
        return jsonify({'message': 'Not found a user!'}), 403


@app.route("/gendata/<user_id>/<images_id>", methods=['GET'])
def order_gen_data(user_id, images_id):
    global data_object
    X_plot = []
    Y_plot = []
    datetime_object = datetime.datetime.now()
    user_labled = db.child('Labeled_Images').get().val()
    user_name = db.child('data/users/' + user_id + '/' + 'name').get().val()
    user_images_data = db.child('Labeled_Images/' + user_id).get().val()
    if user_id in user_labled:
        if images_id in user_images_data:
            images_data = db.child('Labeled_Images/' + user_id + '/' + images_id).get().val()
            for set_of_points in images_data:
                position = set_of_points['points']
                for pos in position:
                    x_data = pos['x']
                    X_plot.append(x_data)
                    y_data = pos['y']
                    Y_plot.append(y_data)
                fig = Figure()
                ax = fig.add_subplot(1, 1, 1)
                plt.style.use('dark_background')
                ax.scatter(X_plot, Y_plot, color='white', s=10)
                x0, x1 = ax.get_xlim()
                y0, y1 = ax.get_ylim()
                ax.set_aspect(abs(x1 - x0) / abs(y1 - y0))
                fig.gca().invert_yaxis()
                ax.set_facecolor('xkcd:black')
                ax.axis('off')
                canvas = FigureCanvas(fig)
                png_output = BytesIO()
                canvas.print_png(png_output)
                data = b64encode(png_output.getvalue()).decode('ascii')
                datetime_object = str(datetime_object)
                data_url = data
                data_object = {
                    'TimeStamped': datetime_object,
                    'Images_data': data_url,
                    'Labeled By': user_name,
                    'DataType': 'image/png;base64'
                }
                db.child('Generated_Labeled_Images/' + user_id + '/' + images_id).set(data_object)
                return jsonify({'Data_generated': data_object}), 201
        else:
            return jsonify({'message': 'Not found your data!'}), 404
    else:
        return jsonify({'message': 'Not found a user!'}), 403

if __name__ == '__main__':
    app.run()
