import React, { useEffect, useState } from "react";

const Dashboard = () => {
  const [message, setMessage] = useState("");
  const [detections, setDetections] = useState([]);

  useEffect(() => {
    //fetch("/api/detections")
    fetch("/api/dashboard")
      .then((res) => res.json())
      .then((data) => {
        setMessage(data.message);
        setDetections(data.detections);
      })
      .catch((err) => console.error("Error fetching dashboard data:", err));
  }, []);

  return (
    <div className="container mt-5">
      <h2 className="text-center">Dashboard</h2>
      <p className="text-center">{message}</p>
      <div className="row">
        {detections.map((image, index) => (
          <div key={index} className="col-md-4 mb-4 text-center">
            <div className="card shadow p-2">
              <img src={`/detections/${encodeURIComponent(image)}`} className="img-fluid border rounded" alt="Detection" />
              <p className="mt-2 text-muted">{image}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;

