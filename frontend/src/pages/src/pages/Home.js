import React from "react";
import { useNavigate } from "react-router-dom";

const Home = () => {
  const navigate = useNavigate();

  return (
    <div className="container text-center mt-5">
      <h1>Welcome to Our Web Server</h1>
      <p className="lead">A simple Flask and React web application.</p>
      <button className="btn btn-primary" onClick={() => navigate("/login")}>
        Login
      </button>
    </div>
  );
};

export default Home;
