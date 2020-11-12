from flask import request, url_for, make_response, jsonify, Flask
from flask_api import FlaskAPI, status, exceptions
from resources import LinkEvents, CustomException


app = FlaskAPI(__name__)


def get_data(request):
    response = request.get_json()
    date_range = int(request.args.get('rangoFecha', 30))
    order = request.args.get('criterioOrden', 'montoTotal')
    by = request.args.get('vincularPor', 'egresos')
    criteria = request.args.get('criteria', None)

    try:
        data = {
            'date_range' : date_range,
            'order' : order,
            'incomes' : response['Ingresos'],
            'outcomes' : response['Egresos'],
            'by' : by,
            'criteria' : criteria
        }
    except:
        raise CustomException("'Ingresos' and 'Egresos' must be passed")

    return data

@app.route('/example/')
def example_api():
    return {'example': 'This is a browsable API'}

@app.route("/link/", methods=['POST'])
def link():
    try:
        data = get_data(request)
        linker = LinkEvents(data['incomes'], data['outcomes'], data['date_range'], data['order'])
        if data['by'] == 'egresos':
            linked = linker.link_by_outcome()
        elif data['by'] == 'ingresos':
            linked = linker.link_by_income()
        elif data['by'] == 'fecha':
            linker = LinkEvents(data['incomes'], data['outcomes'], data['date_range'], 'fechaDeOperacion')
            linked = linker.link_by_outcome()
        elif data['by'] == 'mix':
            linker = LinkEvents(data['incomes'], data['outcomes'], data['date_range'], data['order'])
            linked = linker.exec_mix(data['criteria'])
        else:
            return jsonify("Check 'by' paramater.")
    except Exception as e:
        print(e)
        return make_response(jsonify({'error': "An error occurs, check your params."}), 300)

    return jsonify(linked), 201


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
    


if __name__ == "__main__":
    app.run(debug=True)
