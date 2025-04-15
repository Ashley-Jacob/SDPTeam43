import React, { useState, useEffect } from 'react';

const DetectionDisplay = () => {
  const [images, setImages] = useState([]);

  // Function to fetch detection images from the server
  const fetchDetections = async () => {
    try {
      const response = await fetch('/api/detections');
      const data = await response.json();
      setImages(data);
    } catch (error) {
      console.error('Error fetching detection images:', error);
    }
  };

  useEffect(() => {
    fetchDetections(); // initial fetch
    const interval = setInterval(fetchDetections, 5000); // poll every 5 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ textAlign: 'center' }}>
      <h2>Bear Detections</h2>
      <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center' }}>
        {images.length > 0 ? (
          images.map((imgUrl, index) => (
            <div key={index} style={{ margin: '10px' }}>
              <img 
                src={imgUrl} 
                alt={`Detection ${index + 1}`} 
                style={{ width: '300px', height: 'auto', border: '1px solid #ccc' }} 
              />
            </div>
          ))
        ) : (
          <p>No detections yet.</p>
        )}
      </div>
    </div>
  );
};

export default DetectionDisplay;
