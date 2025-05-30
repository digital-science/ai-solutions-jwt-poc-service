# JWT-token-PoC-app

A PoC dummy service that shows how a service can verify JWT token using Digital Science's developer portal.

### What is Developer Portal?

It is a platform that manages access to Digital Science's services. It creates API-keys/Public keys to pass Gateway.
You may ask organizations' admins to create public keys and API keys for you. If you are a registered user on our platform, please take a look at our [developer portal](https://platform.digital-science.com/).

### Verification Process

The verification of a JWT token with Digital Science's Developer Portal involves the following steps:

- Token Extraction: Extract the JWT token from the Authorization header
- Token Parsing: Split the token into its three parts and decode the payload
- Public Key Identification: Extract the public key ID from the payload
- Verification Request: Send a request to the Developer Portal's verification endpoint
- Response Handling: Process the verification response and determine token validity

### How it works

```plantuml
@startuml
sequenceDiagram
        actor User
        participant Service
        participant APG as API Gateway
        participant DevPortal as Develper Portal
        User->>Service: request /user
        Service->>Service: Generate a token
        Service->>APG: Send a request <API Gateway URL>/service_name with "Authorization: Bearer <TOKEN>"
        APG->>APG: Validate token
        APG->>Service: Forward request
        Service->>Cache: Check for public key
        Service->>DevPortal: get public key (/verify endpoint)
        Service->>Cache: Cache public key
        DevPortal->>Service: send back public key
        Service->>Service: validate token
        Service->>User: Return response
@enduml

```

### How to use

- build image: docker build -t jwt-token-poc-app .
- run it: docker run -p 3000:3000 jwt-token-poc-app
- make a request: curl localhost:3000 -H "Authorization: Bearer \<JWT_TOKEN\>" -H "X-service-id: \<service_id\>", where JWT_TOKEN - generated token, service_id - id of your service on developer portal (check it on /public-keys page)
- output example:

{
  "request_public_key_body": "\<public key body\>",
  "request_service_has_access": true/false
}
