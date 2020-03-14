Authorization
=============

Authorization is performed with the help of `UMA (User Managed Access)`


**************
Generating PAT
**************

PAT (Protection API Token) is a special token with scope `uma_protection`.
Keycloak provides a method called `pat` using with you can retrieve the PAT token.

.. code-block:: python
   :linenos:

   #! -*- coding: utf-8 -*-
   from keycloak import Client

   kc = Client()
   kc.pat()

****************************
Generating Permission Ticket
****************************

A permission ticket is a special type of token defined by the User-Managed Access (UMA)
specification that provides an opaque structure whose form is determined by the
authorization server. This structure represents the resources and/or scopes being
requested by a client, the access context, as well as the policies that must be
applied to a request for authorization data.
See `this <https://www.keycloak.org/docs/4.8/authorization_services/#_overview_terminology_permission_ticket>`_ for more details.

.. code-block:: python
   :linenos:

   #! -*- coding: utf-8 -*-
   from keycloak import Client

   kc = Client()
   pat = kc.pat()

   resources = [
        {
             "resource_id": "8762039c-cdfa-4ef9-9f70-45248863c4da",
             "resource_scopes": ["create", "read", "update", "delete]
        }
   ]
   ticket = kc.find_ticket(resources, pat["access_token"]
