const express = require('express');
const app = express();

require('dotenv').config();


// Example API endpoint
app.get('*', async (req, res) => {

    // check JWT token
    const token = req.headers['authorization'];
    if (!token) {
        return res.status(401).json({ message: 'No token provided' });
    }

    for (const key in req.headers) {
        res.appendHeader("request_"+key, req.headers[key]);
    }
    
    // Decode the token
    const decoded = Buffer.from(token.split('.')[1], 'base64').toString();
    // convert to JSON
    const json = JSON.parse(decoded);
    // Check if the token is valid
    const publicKeyId = json.key;
    const externalServiceId = process.env.EXTERNAL_SERVICE_ID;
    const devPortalURL = process.env.DEV_PORTAL_URL;

    const url = `${devPortalURL}/api/v1/public-keys/verify?service_id=${encodeURIComponent(externalServiceId)}&public_key_id=${encodeURIComponent(publicKeyId)}`;

    try {
        const devPortalResponse = await fetch(url, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
        },
        });

        if (!devPortalResponse.ok) {
            throw new Error(`failed request to developer portal: ${response.status}`);
        }

        const devPortalResponseJson = await devPortalResponse.json();

        if (devPortalResponseJson.service_has_access === undefined || devPortalResponseJson.public_key_body === undefined) {
            console.error('Invalid response from developer portal:', devPortalResponseJson);
        }
        else {
            res.json(devPortalResponseJson)
        }
    } catch (error) {
      console.error('Verification request failed:', error);
      return null;
    }
});

// Start the server
const PORT = process.env.PORT || 3000;
console.log(`configured port ${PORT}`);
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
