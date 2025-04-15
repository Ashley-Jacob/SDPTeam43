import React, { useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import "./Navbar.css";

const Navbar = () => {
  const { isAuthenticated, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <nav className="custom-navbar">
      <div className="nav-left">
        {isAuthenticated ? (
          <>
            <Link to="/dashboard">Detections</Link>
            <Link to="/config">Configure</Link>
            <button onClick={handleLogout}>Logout</button>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/signup">Sign Up</Link>
          </>
        )}
      </div>

      {isAuthenticated && (
        <Link to="/account" className="nav-profile-circle" />
      )}
    </nav>
  );
};

export default Navbar;
