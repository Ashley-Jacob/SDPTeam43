import React, { useEffect, useState } from "react";

const Config = () => {
  const [config, setConfig] = useState({ id: 21, time: 30 });

  useEffect(() => {
    fetch("/api/pi/config")
      .then((res) => res.json())
      .then((data) => setConfig(data.config));
  }, []);

  const handleChange = (key, value) => {
    setConfig((prev) => ({ ...prev, [key]: value }));
  };

  const handleSave = () => {
    fetch("/api/pi/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(config),
    }).then(() => alert("Config sent to Pi!"));
  };

  return (
    <div className="container mt-4">
      <h2>Update Pi Config</h2>
      <label>ID:</label>
      <input
        type="number"
        value={config.id}
        onChange={(e) => handleChange("id", parseInt(e.target.value))}
      />

      <label className="mt-2">Time:</label>
      <input
        type="number"
        value={config.time}
        onChange={(e) => handleChange("time", parseInt(e.target.value))}
      />

      <button className="btn btn-success mt-3" onClick={handleSave}>
        Send to Pi
      </button>
    </div>
  );
};

export default Config;
