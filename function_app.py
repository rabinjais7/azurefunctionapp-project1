import azure.functions as func
import logging
import requests
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="func_testingFunc")
def func_testingFunc(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
    except ValueError:
        req_body = None

    rows = req.params.get("data") or (req_body.get("data") if req_body else None)

    if rows is None:
        return func.HttpResponse("Error: 'data' parameter is missing", status_code=400)

    if not isinstance(rows, list):
        return func.HttpResponse("Error: 'data' parameter must be a list", status_code=400)

    if not rows:
        return func.HttpResponse("Error: 'data' list is empty", status_code=400)

    status_code = 200
    array_of_rows_to_return = [ ]

    try:
   
        for row in rows:
            row_number = row[0]
            from_currency = row[1]
            to_currency = row[2]

            api_url = 'https://open.er-api.com/v6/latest/'+from_currency
            response = requests.get(url=api_url)
            data = response.json()

            exchange_rate_value = data['rates'][to_currency]
            output_value = [exchange_rate_value]
            row_to_return = [row_number, output_value]
            array_of_rows_to_return.append(row_to_return)

        json_compatible_string_to_return = json.dumps({"data" : array_of_rows_to_return})
        return func.HttpResponse(json_compatible_string_to_return, status_code=200)

    except requests.exceptions.RequestException as err:
        return func.HttpResponse(f"Error: {err}", status_code=400)
    except KeyError as err:
        return func.HttpResponse(f"Error: Invalid key {err}", status_code=400)
    except Exception as err:
        return func.HttpResponse(f"Error: {err}", status_code=400)
