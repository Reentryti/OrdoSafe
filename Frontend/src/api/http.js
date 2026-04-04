const BASE_URL = "http://localhost:8000";

function getCookie(name) {
  const cookies = document.cookie.split(";");
  for (const cookie of cookies) {
    const trimmed = cookie.trim();
    if (trimmed.startsWith(name + "=")) {
      return decodeURIComponent(trimmed.substring(name.length + 1));
    }
  }
  return null;
}

async function request(method, path, { body, params } = {}) {
  let url = BASE_URL + path;

  if (params) {
    const qs = new URLSearchParams();
    for (const [k, v] of Object.entries(params)) {
      if (v !== undefined && v !== null && v !== "") qs.append(k, v);
    }
    const str = qs.toString();
    if (str) url += "?" + str;
  }

  const headers = {};
  const opts = { method, headers, credentials: "include" };

  if (body) {
    headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(body);
  }

  if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
    const csrfToken = getCookie("csrftoken");
    if (csrfToken) headers["X-CSRFToken"] = csrfToken;
  }

  const res = await fetch(url, opts);

  if (!res.ok) {
    if (res.status === 401) {
      const currentPath = window.location.pathname;
      if (!currentPath.startsWith("/login") && currentPath !== "/") {
        window.location.href = "/";
      }
    }

    let data;
    try {
      data = await res.json();
    } catch {
      data = { error: res.statusText };
    }

    const err = new Error(data.error || res.statusText);
    err.status = res.status;
    err.data = data;
    throw err;
  }

  const text = await res.text();
  return text ? JSON.parse(text) : {};
}

export default {
  get(path, opts) {
    return request("GET", path, opts);
  },
  post(path, body) {
    return request("POST", path, { body });
  },
  put(path, body) {
    return request("PUT", path, { body });
  },
  delete(path) {
    return request("DELETE", path);
  },
};
