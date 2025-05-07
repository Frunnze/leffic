let accessToken = null;
let baseUrl = import.meta.env.VITE_GATEWAY_URL || "http://localhost:8888";


export function getBaseUrl() {
    return baseUrl;
}

export function setAccessToken(token) {
    accessToken = token;
}

async function getAccessToken() {
    try {
        const response = await fetch(`${baseUrl}/api/user/refresh-token`, {
            method: "POST",
            credentials: "include"
        });

        if (response.status === 401) {
            setAccessToken(null);
            window.location.href = "/login";
            return null;
        }

        if (response.ok) {
            const data = await response.json();
            return data.access_token;
        }
    } catch (err) {
        console.error("Error refreshing token:", err);
        return null;
    }
}

export async function apiRequest({ 
    endpoint, 
    method = "GET", 
    headers = {}, 
    body = null, 
    withToken = true, 
    credentials = "same-origin"
}) {
    if (withToken && !accessToken) {
        accessToken = await getAccessToken();
        if (!accessToken) return null;
    }

    const customFetch = async (token=null) => {
        let url = `${baseUrl}${endpoint}`;

        const config = {
            method: method,
            headers: {
                ...headers,
            },
            credentials: credentials
        };

        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        if (body) {
            let contentType = await inferContentType(body);
            if (contentType) {
                config.headers["Content-Type"] = contentType;
            }
            if (contentType === "application/json"){
                config.body = JSON.stringify(body);
            } else {
                config.body = body;
            }
        }
        console.log(`config ${endpoint}`, config)
        const response = await fetch(url, config);
        return response;
    };
    let response = await customFetch(accessToken);

    if (response.status === 401) {
        accessToken = await getAccessToken();
        if (!accessToken) return null;
        response = await customFetch(accessToken);
    }

    return response;
}

async function inferContentType(body) {
    if (body instanceof FormData) {
        return null;
    }
    if (body instanceof Blob && body.type) {
      return body.type;
    }
    if (typeof body === 'string') {
      return 'text/plain';
    }
    if (typeof body === 'object') {
        return 'application/json';
    }
    return null;
}