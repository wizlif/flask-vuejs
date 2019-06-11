Introduction
============

.. sidebar:: API Browser Quick Guide
    :subtitle: **It can make your life easier** if you use some kind of **API browser application** to **explore the API** when diving into this documentation.

    * We recommend to use the free `Postman <http://www.getpostman.com/>`_ browser plugin.
    * For easy onboarding take a look at **our** :ref:`exploring-api-postman-onboarding` **Quick-Guide**.

A hypermedia API provides an entry point to the API, which contains hyperlinks the clients can follow.
Just like a human user of a regular website, who knows the initial URL of a website and then follows hyperlinks to navigate through the site.
This has the advantage that the client only needs to understand how to detect and follow links.
The URLs (apart from the inital entry point) and other details of the API can change without breaking the client.

The entry point to the Generics RESTful API is the portal root appended with ``/api/v1``.
The client can ask for a :term:`REST` API response by setting the ``'Accept'`` HTTP header to ``'application/json'``: