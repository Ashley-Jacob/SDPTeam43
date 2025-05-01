import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import './AuthForm.css';

const Signup = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const response = await fetch("/api/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (response.ok) {
      alert("Signup successful! Redirecting to login...");
      navigate("/login");
    } else {
      alert("Signup failed, please try again.");
    }
  };

  return (
    <div className="auth-container signup">
      <div className="auth-header">
        <h2>Sign Up</h2>
        <div className="dots"><div></div><div></div><div></div></div>
      </div>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Email</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit" className="submit">Submit</button>
      </form>
      <p className="switch-link"><a href="/login">Already have an account? Log in</a></p>
    </div>
  );
};

export default Signup;

