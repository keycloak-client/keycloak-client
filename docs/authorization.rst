Authorization
=============

Keycloak client provides a method called `validate_rpt`, using which you can
introspect and validate the incoming request. This method can be employed as a
authorization middleware within your application.

The following snippet is an example written in `Flask <http://flask.pocoo.org/>`_ framework

.. code-block:: python
   :linenos:
   :emphasize-lines: 4

   @app.route('/introspect-rpt', methods=['POST'])
   def introspect_rpt():
       """ Endpoint to introspect/validate authorization tokens """
       rpt = request.json.get('rpt')
       result = keycloak_client.validate_rpt(rpt)
       return jsonify(result)
