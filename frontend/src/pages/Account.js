import React, { useContext, useState } from "react";
import { AuthContext } from "../context/AuthContext";

const Account = () => {
  const { isAuthenticated } = useContext(AuthContext);

  const [newUsername, setNewUsername] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [message, setMessage] = useState("");

  const [activeSection, setActiveSection] = useState(null); // 'username', 'password', or null

  const handleUsernameUpdate = async (e) => {
    e.preventDefault();
    const res = await fetch("/api/update-account", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        new_username: newUsername,
        current_password: currentPassword,
        new_password: ""
      })
    });
    const data = await res.json();
    setMessage(data.message || data.error);

    if (!data.error) {
      setNewUsername("");
      setCurrentPassword("");
      setActiveSection(null);
    }
  };

  const handlePasswordUpdate = async (e) => {
    e.preventDefault();
    const res = await fetch("/api/update-account", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        new_username: "",
        current_password: currentPassword,
        new_password: newPassword
      })
    });
    const data = await res.json();
    setMessage(data.message || data.error);

    if (!data.error) {
      setNewPassword("");
      setCurrentPassword("");
      setActiveSection(null);
    }
  };

  const collapseSection = () => {
    setActiveSection(null);
    setNewUsername("");
    setNewPassword("");
    setCurrentPassword("");
  };  

  if (!isAuthenticated) return <p style={{ color: "white" }}>Unauthorized</p>;

  return (
    <div style={{ color: "white", textAlign: "center", marginTop: "2rem" }}>
      <h1>My Account</h1>

      {activeSection === null && (
        <>
          <button
            onClick={() => setActiveSection("username")}
            style={buttonStyle}
          >
            Change Username
          </button>
          <button
            onClick={() => setActiveSection("password")}
            style={buttonStyle}
          >
            Change Password
          </button>
        </>
      )}

      {activeSection === "username" && (
        <>
          <button onClick={collapseSection} style={buttonStyle}>
            Change Username <span style={{ fontSize: "1.2rem" }}>▲</span>
          </button>
          <form onSubmit={handleUsernameUpdate} style={formStyle}>
            <input
              type="text"
              placeholder="New Username"
              value={newUsername}
              onChange={(e) => setNewUsername(e.target.value)}
              style={inputStyle}
            />
            <input
              type="password"
              placeholder="Current Password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              required
              style={inputStyle}
            />
            <button type="submit" style={submitStyle}>
              Submit
            </button>
          </form>
        </>
      )}

      {activeSection === "password" && (
        <>
          <button onClick={collapseSection} style={buttonStyle}>
            Change Password <span style={{ fontSize: "1.2rem" }}>▲</span>
          </button>
          <form onSubmit={handlePasswordUpdate} style={formStyle}>
            <input
              type="password"
              placeholder="Current Password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              required
              style={inputStyle}
            />
            <input
              type="password"
              placeholder="New Password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              style={inputStyle}
            />
            <button type="submit" style={submitStyle}>
              Submit
            </button>
          </form>
        </>
      )}

      {message && (
        <p style={{ marginTop: "1rem", color: message.includes("success") ? "#8f8" : "#f88" }}>
          {message}
        </p>
      )}
    </div>
  );
};

const buttonStyle = {
  margin: "1rem",
  padding: "0.5rem 1.5rem",
  borderRadius: "999px",
  border: "none",
  background: "#fdf07b",
  color: "black",
  fontWeight: "bold",
  cursor: "pointer"
};

const formStyle = {
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  gap: "1rem",
  maxWidth: "400px",
  margin: "1rem auto"
};

const inputStyle = {
  padding: "0.5rem",
  borderRadius: "8px",
  width: "100%"
};

const submitStyle = {
  padding: "0.5rem 2rem",
  borderRadius: "999px",
  background: "black",
  color: "#fdf07b",
  border: "none",
  fontWeight: "bold"
};

export default Account;