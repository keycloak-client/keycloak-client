Resource Management
===================

Keycloak client provides the following methods to perform resource management

* `create_resource`
* `list_resource`
* `read_resource`
* `update_resource`
* `delete_resource`

The following snippet is an example written in `Flask <http://flask.pocoo.org/>`_ framework

.. code-block:: python
   :linenos:
   :emphasize-lines: 12

   @app.cli.command()
   def create_resources():
       """ command to register resources with keycloak """

       # read resources from json
       with open('resources.json', 'r') as f:
           resources = f.read()

       # create resources in the keycloak server
       resources = json.loads(resources)
       for item in resources:
           keycloak_client.create_resource(item)
