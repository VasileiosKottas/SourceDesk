async function request(path, options = {}) {
  const response = await fetch(path, {
    credentials: "include",
    ...options,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.message || data.error || "Request failed");
  }
  return data;
}

export function getMe() {
  return request("/me");
}

export function register(name, email, password) {
  return request("/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password }),
  });
}

export function login(email, password) {
  return request("/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
}

export function logout() {
  return request("/logout", { method: "POST" });
}

export function getLinks() {
  return request("/links");
}

export function getLink(id) {
  return request(`/links/${id}`);
}

export function createLink(url, title, notes) {
  return request("/links", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, title, notes }),
  });
}

export function deleteLink(id) {
  return request(`/links/${id}`, { method: "DELETE" });
}

export function getFiles() {
  return request("/files");
}

export function getFile(id) {
  return request(`/files/${id}`);
}

export function getFilePages(id) {
  return request(`/files/${id}/pages`);
}

export function uploadFile(file) {
  const body = new FormData();
  body.append("file", file);
  return request("/files", { method: "POST", body });
}

export function deleteFile(id) {
  return request(`/files/${id}`, { method: "DELETE" });
}

export function getQuestions() {
  return request("/questions");
}

export function deleteQuestion(id) {
  return request(`/questions/${id}`, { method: "DELETE" });
}

export function askQuestion(question) {
  return request("/ask-question", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
}
