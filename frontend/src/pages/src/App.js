import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import { Navigate } from "react-router-dom"; 
import Home from "./pages/Home";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import Config from "./pages/Config";
import Account from "./pages/Account";
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";
import "bootstrap/dist/css/bootstrap.min.css";
import { useContext } from "react";
import { AuthContext } from "./context/AuthContext";

function App() {
  const { isAuthenticated, authChecked } = useContext(AuthContext);
  if (!authChecked) return <div>Loading...</div>;
  
  return (
    <Router>
      <Navbar isAuthenticated={isAuthenticated} />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute isAuthenticated={isAuthenticated}>
            <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/config"
          element={
            <ProtectedRoute isAuthenticated={isAuthenticated}>
            <Config />
            </ProtectedRoute>
          }
        />
      <Route
        path="/account"
        element={
          <ProtectedRoute isAuthenticated={isAuthenticated}>
          <Account />
          </ProtectedRoute>
        }
      />
        <Route
          path="*"
          element={
            <Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />
          }
        />
      </Routes>
    </Router>
  );
}

export default App;

