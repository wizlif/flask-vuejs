Authentication
==============

``generics.restapi`` uses JWT for Authentication.

That means that any authentication requiring method or endpoint should include a JWT Bearer token in it's header or else it will fail.

For example, to authenticate using HTTP bearer auth, you'd set an ``Authorization`` header:

.. code-block:: http

  GET /api/v1 HTTP/1.1
  Authorization: Bearer JWT_TOKEN
  Accept: application/json

HTTP client libraries usually contain helper functions to produce a proper ``Authorization`` header for you based on given credentials.

Using the ``requests`` library, you'd set up a bearer auth like this:

.. code-block:: python

    import requests

    response = requests.get(url,
    headers={
    'Authorization':'Bearer JWT_TOKEN',
    'Content-type':'application/json'
    })

Using the javascript ``axios`` library with vuejs or nodejs.

.. code-block:: javascript

    import axios from 'axios';

    axios.defaults.headers.common['Authorization'] = 'Bearer JWT';
    axios.get(url)
    .then(response => {
    // Handle response
    }).catch(error => {
    // Handle Error
    });

Or the same example using ``curl``:

.. code-block:: bash

     curl -XGET -H "Content-type: application/json" -H 'Authorization: Bearer JWT' $URL

Acquiring a token (login)
^^^^^^^^^^^^^^^^^^^^^^^^^^

A JWT token can be acquired by posting a user's credentials to the ``login``
endpoint.

..  http:example:: curl wget httpie python-requests

    POST /api/v1/login HTTP/1.1
    Host: localhost:5000
    Accept: application/json
    Content-Type: application/json

    {
        "username": "admin",
        "password": "secret"
    }

The server responds with a JSON object containing the user token and access token.

``user_token`` is a base64 encoding of required user data

``access_token`` is a JWT auth to be used for all `Authorization` HTTP header requests

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1NDMzOTIyNTYsIm5iZiI6MTU0MzM5MjI1NiwianRpIjoiZTI5MzNkOTQtZmFkNC00MTFhLWE5MmMtMzk3ZTU3ZWY2N2E4IiwiZXhwIjoxNTQzNDAzMDU2LCJpZGVudGl0eSI6MjA5LCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MifQ.visqnE2urdROlRKUg2KdJEIJQviVZEsBzUhfLyMLzL4",
        "user_token": "eyJhZG1pbl9pZCI6IG51bGwsICJjaXR5IjogImthbXBhbGEiLCAiY291bnRyeSI6ICJVRyIsICJjcmVhdGVkX2F0IjogIk1vbiwgMDEgT2N0IDIwMTggMDU6MjU6NTIgR01UIiwgImNyZWRpdF9iYWxhbmNlIjogODg3NC4wLCAiZW1haWwiOiAiaW9iZWxsYUBpM2MuY28udWciLCAiZmF4IjogbnVsbCwgImZpcnN0bmFtZSI6ICJvYmVsbGEiLCAiaWQiOiAyMDksICJsYXN0X2xvZ2luIjogIldlZCwgMjggTm92IDIwMTggMDk6MDg6MjkgR01UIiwgImxhc3RuYW1lIjogImlzYWFjIiwgIm1pbl9iYWxhbmNlIjogbnVsbCwgIm1vYmlsZV9waG9uZSI6ICIrMjU2Ljc3ODkxNjM1MyIsICJuYW1lIjogIm9iZWxsYSBpc2FhYyIsICJuczEiOiAibnMxLmNmaS5jby51ZyIsICJuczFfaXAiOiAiNTAuMjIuMjA4LjEzMCIsICJuczIiOiAibnMyLmNmaS5jby51ZyIsICJuczJfaXAiOiAiNTAuMjIuMjA4LjE0MCIsICJuczMiOiAibnMzLmNmaS5jby51ZyIsICJuczNfaXAiOiAiMTk4LjIzLjkwLjE1NSIsICJuczQiOiAibnM0LmNmaS5jby51ZyIsICJuczRfaXAiOiAiMTkyLjE2OC4xMDAuMjQ5IiwgIm9yZ2FuaXphdGlvbiI6ICJpbmZpbml0eSBjb21wdXRlcnMiLCAicGFzc3dvcmRfcmVzZXRfc2VudF9hdCI6ICJNb24sIDAzIFNlcCAyMDE4IDE3OjUxOjU5IEdNVCIsICJwaG9uZSI6ICIrMjU2Ljc3ODkxNjM1MyIsICJwb3N0YWxfY29kZSI6ICI2NzgyIiwgInByaXZpbGVnZXMiOiAiU3VwZXIgQWRtaW4iLCAic3RhdGVfcHJvdmluY2UiOiAiY2VudHJhbCIsICJzdGF0dXMiOiAiQUNUSVZFIiwgInN0cmVldF9hZGRyZXNzIjogInBsb3QgNmIgd2luZHNvciBsb29wIiwgInVwZGF0ZWRfYXQiOiBudWxsfQ=="
    }


