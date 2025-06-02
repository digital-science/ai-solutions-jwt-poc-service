from flask import Flask, request, jsonify, make_response
import os
import json
import requests
from dotenv import load_dotenv
from loggger import logger
import time
import jwt

# Load environment variables from .env file
load_dotenv()
instance = jwt.JWT()

app = Flask(__name__)

# Get the external service ID and dev portal URL from environment variables
external_service_id = os.environ.get('EXTERNAL_SERVICE_ID')
dev_portal_url = os.environ.get('DEV_PORTAL_URL')
gateway_url = os.environ.get('GATEWAY_URL')


@app.route('/forwarded-request-endpoint')
def forwarded_request_endpoint():
    # Check JWT token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"message": "No token provided"}), 401

    if token.startswith('BEARER ') or token.startswith('Bearer '):
        token = token[7:]  # Remove "Bearer " prefix

    # Process token and update response
    json_data = instance.decode(token, key=private_key, algorithms=['RS256'])

    # Check if the token is valid
    public_key_id = json_data.get('key')

    url = f"{dev_portal_url}/api/v1/public/public-keys/{public_key_id}/verify/{external_service_id}"
    logger.info(f"requested endpoint: {url}")
    dev_portal_response = requests.get(
        url,
        headers={
            'Accept': 'application/json',
        }
    )

    dev_portal_response.raise_for_status()

    # Add request headers to response headers
    response_headers = {}
    logger.info("headers from dev portal:")
    for key, value in dev_portal_response.headers.items():
        response_headers[f"request_{key}"] = value
        logger.info(f"     {key} = {value}")

    response_json = {}
    try:
        logger.info(dev_portal_response.json())
        logger.info("JSON values from dev portal:")
        for key, value in dev_portal_response.json().items():
            response_json[f"request_{key}"] = value
            logger.info(f"     {key} = {value}")
    except json.JSONDecodeError:
        logger.info("no json in response from dev portal")

    response = make_response(jsonify(response_json))
    response.headers.update(response_headers)

    return response


@app.route("/user-endpoint", methods=["GET"])
def user_endpoint():
    # This is an example endpoint that can be used to test the JWT token
    token_payload = {
        "key": os.environ.get('PUBLIC_KEY_ID'),
        "exp": time.time() + 3600,  # Token valid for 1 hour
    }

    try:
        token = instance.encode(token_payload, private_key, alg='RS256')
    except Exception as e:
        logger.error(f"Error signing token: {e}")
        return jsonify({"error": f"Failed to sign token: {e}"}), 500

    request = requests.get(f"{os.environ.get('GATEWAY_URL')}/{external_service_id}",
                           headers={"Authorization": f"Bearer {token}"}
                           )
    request.raise_for_status()

    logger.info("request: ", request)

    logger.info("request: headers: ", request.headers)
    logger.info("request: json: ", request.json())

    public_key_body = request.json()["public_key_body"]

    try:
        token = instance.decode(token, key=public_key_body, algorithms=[
            'RS256'], do_time_check=True)
        logger.info(f"Decoded token: {token}")
        return jsonify({"message": "Token is valid"}), 200
    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        logger.error("Invalid token")
        return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        logger.error(f"Error decoding token: {e}")
        return jsonify({"error": "Failed to decode token"}), 500


private_key = None

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    logger.info(f"Configured port {port}")

    private_key_file = os.environ.get('PRIVATE_KEY_FILE')
    if private_key_file:
        with open(private_key_file, 'r') as f:
            private_key = f.read()
            private_key = jwt.jwk_from_pem(private_key.encode("utf-8"))
    else:
        logger.error("PRIVATE_KEY_FILE environment variable is not set.")
    if not os.environ.get('DEVELOPER_PORTAL_KEY_ID'):
        logger.error(
            "DEVELOPER_PORTAL_KEY_ID environment variable is not set.")
    if not os.environ.get('DEV_PORTAL_URL'):
        logger.error("DEV_PORTAL_URL environment variable is not set.")
    if not os.environ.get('EXTERNAL_SERVICE_ID'):
        logger.error("EXTERNAL_SERVICE_ID environment variable is not set.")
    if not os.environ.get('GATEWAY_URL'):
        logger.error("GATEWAY_URL environment variable is not set.")

    app.run(host='0.0.0.0', port=port, debug=True)
