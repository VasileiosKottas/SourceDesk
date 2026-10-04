import { useEffect, useState } from "react";
import { getMe } from "./api";
import AuthPage from "./AuthPage.jsx";
import Desk from "./Desk.jsx";

export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMe()
      .then((data) => setUser(data.user))
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <p className="status">Loading...</p>;
  }

  if (!user) {
    return <AuthPage onLogin={setUser} />;
  }

  return <Desk user={user} onLogout={() => setUser(null)} />;
}
