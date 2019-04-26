# Running the example

* Update the `keycloak.json` with proper details
* Register the resources usin the following command
```
pip install -r requirements.txt
export FLASK_APP=app.py
flask register-resources
```
* Run the flask application using the following command
```
flask run
```
* Open `http://localhost:5000/login` within the browser
