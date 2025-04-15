import React, { useContext } from "react";
import { AuthContext } from "../context/AuthContext";

const Account = () => {
  const { isAuthenticated } = useContext(AuthContext);

  if (!isAuthenticated) return <p style={{ color: "white" }}>Unauthorized</p>;

  return (
    <div style={{ color: "white", textAlign: "center", marginTop: "4rem" }}>
      <h1>My Account</h1>
      <p>This is your account page.</p>
    </div>
  );
};

export default Account;
