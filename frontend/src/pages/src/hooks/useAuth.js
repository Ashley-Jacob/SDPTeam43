import { useState, useEffect } from "react";

export default function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authChecked, setAuthChecked] = useState(false);

  useEffect(() => {
    fetch("/api/check-auth", { credentials: "include" })
      .then((res) => res.json())
      .then((data) => setIsAuthenticated(data.loggedIn))
      .catch(() => setIsAuthenticated(false))
      .finally(() => setAuthChecked(true));
  }, []);

  return { isAuthenticated, authChecked };
}
