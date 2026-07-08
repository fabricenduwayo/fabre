# model-registry

A small Spring Boot service that reports candidate churn-model metadata,
deployment aliases, and a liveness signal. All data is loaded once at startup
from the bundled `registry-models.json` classpath resource and served
read-only; there is no persistence layer and no runtime write path.

The metadata this service reports is the registry's own view of each candidate.
It is not reconciled against experiment tracking or any other source at read
time — the service simply reflects what the bundled document says.

## Build and run

```sh
mvn package
java -jar target/model-registry-0.1.0.jar --server.port=8080
```

## Endpoints

| Method | Path                 | Response                                             |
| ------ | -------------------- | ---------------------------------------------------- |
| GET    | `/health`            | `{"status":"UP"}`                                    |
| GET    | `/models/candidates` | JSON array of all candidate models                   |
| GET    | `/models/{id}`       | the matching candidate object, or `404` if unknown   |
| GET    | `/aliases`           | JSON object mapping deployment alias to model id     |

## Tests

```sh
mvn test
```

The test suite exercises every endpoint in-process via MockMvc, so it runs
without binding a network port.
