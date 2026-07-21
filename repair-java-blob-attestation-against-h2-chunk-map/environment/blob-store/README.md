# Blob store API

Runs on `http://localhost:8080`.

    GET  /health                    liveness
    GET  /objects                   list object ids
    PUT  /objects/{id}              ingest the request body as a new object
    POST /objects/{id}              replace an existing object's content with the request body
    GET  /objects/{id}              read the object as the store serves it
    GET  /objects/{id}/blob         read the object's materialised blob copy
    GET  /objects/{id}/declared     the length and digest the object was declared with
    GET  /objects/{id}/attestation  the status the store last recorded for the object
