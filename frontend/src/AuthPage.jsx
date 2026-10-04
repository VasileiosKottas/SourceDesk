import { useState } from "react";
import { login, register } from "./api";

export default function AuthPage({ onLogin }) {
  const [mode, setMode] = useState("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    try {
      const data =
        mode === "register"
          ? await register(name, email, password)
          : await login(email, password);
      if (mode === "register") {
        const loggedIn = await login(email, password);
        onLogin(loggedIn.user);
        return;
      }
      onLogin(data.user);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <main className="auth">
      <section className="card">
        <p className="eyebrow">SourceDesk</p>
        <h1>{mode === "login" ? "Welcome back" : "Create an account"}</h1>
        <p className="muted">Save links and files, then ask an agent about them later.</p>
        <form onSubmit={handleSubmit}>
          {mode === "register" && (
            <label>
              Name
              <input value={name} onChange={(event) => setName(event.target.value)} required />
            </label>
          )}
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>
          {error && <p className="error">{error}</p>}
          <button type="submit">{mode === "login" ? "Log in" : "Sign up"}</button>
        </form>
        <button
          className="text-button"
          type="button"
          onClick={() => {
            setMode(mode === "login" ? "register" : "login");
            setError("");
          }}
        >
          {mode === "login" ? "Need an account? Sign up" : "Already have an account? Log in"}
        </button>
      </section>
    </main>
  );
}
