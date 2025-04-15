import { createContext, useEffect, useState } from "react";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authChecked, setAuthChecked] = useState(false);

  const checkAuth = () => {
    fetch("/api/check-auth", { credentials: "include" })
      .then((res) => res.json())
      .then((data) => setIsAuthenticated(data.authenticated))
      .finally(() => setAuthChecked(true));
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const login = async (username, password) => {
    const res = await fetch("/api/login", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (res.ok) {
      checkAuth(); // refresh global state
      return true;
    }

    return false;
  };

  const logout = async () => {
    await fetch("/api/logout", {
      method: "POST",
      credentials: "include",
    });
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider
      value={{ isAuthenticated, authChecked, login, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
};
