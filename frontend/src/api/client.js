/**
 * This module is the frontend's API boundary.
 *
 * Components describe user interface behavior. This file handles HTTP details:
 * methods, headers, JSON conversion, tokens, and response errors. Keeping those
 * details here means every component uses the same request rules.
 */

// ApiError keeps the HTTP status beside the readable message. App can therefore
// recognize a 401 without checking message text.
export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

// All exported API functions eventually use this one request helper.
// The options object makes body, token, and cancellation optional.
async function request(path, { method = 'GET', token, body, signal } = {}) {
  const headers = {};

  // JSON content type is needed only when a request actually has a JSON body.
  if (body !== undefined) {
    headers['Content-Type'] = 'application/json';
  }

  // Protected endpoints receive the ID token in the Authorization header.
  // The token is not placed in the request body or URL.
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  let response;
  try {
    // fetch is the browser API that sends the real HTTP request. Relative paths
    // are forwarded to Python by the Vite proxy during local development.
    response = await fetch(path, {
      method,
      headers,
      // Convert a JavaScript object into JSON text for the Python server.
      body: body === undefined ? undefined : JSON.stringify(body),
      signal,
    });
  } catch (error) {
    // AbortError means useEffect intentionally cancelled a request; preserve it
    // so App can ignore it rather than showing a connection error.
    if (error.name === 'AbortError') throw error;

    // fetch throws here for network failures, such as the API being offline.
    throw new ApiError(
      'Could not reach the API. Make sure the Python server is running.',
      0,
    );
  }

  // Convert response JSON text back into a JavaScript object. The fallback
  // keeps error handling safe if a server ever returns an empty response.
  const data = await response.json().catch(() => ({}));

  // fetch resolves even for HTTP 400 or 500 responses, so response.ok must be
  // checked explicitly. Throwing lets App handle every failure in catch blocks.
  if (!response.ok) {
    throw new ApiError(data.error || `Request failed (${response.status}).`, response.status);
  }

  return data;
}

// Public authentication requests do not have a Bearer token yet.
export function register(credentials) {
  return request('/auth/register', { method: 'POST', body: credentials });
}

export function login(credentials) {
  return request('/auth/login', { method: 'POST', body: credentials });
}

// Every task function receives the current token because all task routes are
// protected by the Python authentication middleware.
export function listTasks(token, signal) {
  return request('/tasks', { token, signal });
}

// CRUD request bodies contain only fields accepted by the backend validator.
export function createTask(title, token) {
  return request('/tasks', {
    method: 'POST',
    token,
    body: { title },
  });
}

export function renameTask(id, title, token) {
  return request(`/tasks/${id}`, {
    method: 'PATCH',
    token,
    body: { title },
  });
}

export function completeTask(id, token) {
  return request(`/tasks/${id}/complete`, { method: 'POST', token });
}

export function deleteTask(id, token) {
  return request(`/tasks/${id}`, { method: 'DELETE', token });
}
