from flask import Flask, request, jsonify, make_response
import os
import json
import base64
import requests
from dotenv import load_dotenv
import asyncio
from loggger import logger

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get the external service ID and dev portal URL from environment variables
external_service_id = os.environ.get('EXTERNAL_SERVICE_ID')
dev_portal_url = os.environ.get('DEV_PORTAL_URL')


def token_process(token: str, external_service_id: str, dev_portal_url: str) -> requests.Response:
    # Check if token has 3 parts
    token_parts = token.split('.')
    if len(token_parts) != 3:
        raise ValueError("Invalid token format")

    # Decode the token (middle part contains the payload)
    # Need to handle padding for base64 decoding
    payload = token_parts[1]
    # Add padding if necessary
    # payload += '=' * ((4 - len(payload) % 4) % 4)
    decoded = base64.b64decode(payload).decode('utf-8')

    # Convert to JSON
    json_data = json.loads(decoded)

    # Check if the token is valid
    public_key_id = json_data.get('key')

    url = f"{dev_portal_url}/api/v1/public/public-keys/{public_key_id}/verify/{external_service_id}"
    logger.info(f"requested endpoint: {url}")
    dev_portal_response = requests.get(
        url,
        headers={'Accept': 'application/json'}
    )

    dev_portal_response.raise_for_status()

    return dev_portal_response


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # Check JWT token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"message": "No token provided"}), 401

    logger.info(f"headers: {request.headers}")
    logger.info(request.headers.get('X-service-id'))

    # Process token and update response
    service_id = request.headers.get('X-service-id') or external_service_id

    devportal_response = token_process(
        token, service_id, dev_portal_url)

    # Add request headers to response headers
    response_headers = {}
    logger.info("headers from dev portal:")
    for key, value in devportal_response.headers.items():
        response_headers[f"request_{key}"] = value
        logger.info("     ", key, " = ", value)

    response_json = {}
    logger.info("devportal_response.json()", devportal_response.json())
    logger.info("JSON values from dev portal:")
    for key, value in devportal_response.json().items():
        response_json[f"request_{key}"] = value
        logger.info("     {key} = {value}")

    response = make_response(jsonify(response_json))
    response.headers.update(response_headers)

    return response


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    logger.info(f"Configured port {port}")

    # in case JWT_TOKEN is set in the environment
    # in this case you don't need to make a request to the server
    jwt_token = os.environ.get('JWT_TOKEN')
    if jwt_token:
        response = token_process(
            f"BEARER {jwt_token}",
            external_service_id,
            dev_portal_url
        )
        logger.info("json:")
        logger.info(response.json())
        logger.info("headers:")
        logger.info(response.headers)
    else:
        # Start the server
        app.run(host='0.0.0.0', port=port, debug=True)
