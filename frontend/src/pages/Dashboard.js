import React, { useEffect, useState } from "react";
import placeholder from '../resources/placeholder.jpg';
import './Dashboard.css';
//import { BiRefresh } from "react-icons/bi";

const Card = (props) => {
  return (
    <div className={props.type === "bulk" ? "img-card" : "last-img"}>
      <img
        src={props.imgURL || placeholder}
        alt="detection"
        style={{ cursor: 'pointer' }}
        onClick={() => window.open(props.imgURL || placeholder, '_blank')}
      />
      <div className="text">
        <span>{props.animal}</span>
        <span>{props.info}</span>
      </div>
    </div>
  )
}



const Dashboard = () => {
  const [cardData, setCardData] = useState([]);

  const CardDisplay = (props) => {
  
    return (
      <div className="cards">
        {cardData.map((card, index) => (
          <Card
            key={index}
            animal={card.animal}
            info={card.info}
            type={card.type}
            imgURL = {card.imgUrl}
          />
          
        ))}
      </div>
    );
  };

  const refreshApp = async () => 
  {
    const response = await fetch("http://localhost:5000/geturls"); 
    const imagePaths = (await response.json())["urls"]; 

    const updatedData = imagePaths.map(path => {
        const fullUrl = `http://localhost:5000/${path.url}`;
        const animal = path.animal
        const dateStr = path.date

        console.log(fullUrl)

        return {
          animal: animal,
          info: dateStr,
          type: "bulk",
          imgUrl: fullUrl
        };
      });

    setCardData(updatedData);
  };

  return (
    <div className="dash-content">
      <div className="page-name">
        <span>Dashboard</span>
      </div>
      <div className='refresh-button'>
        <button onClick = {refreshApp}>
        </button>
      </div>
      <div className="notifications">
        <div className="latest-card">
          <img src="http://localhost:5000/static/camera.png" alt="latest detection" style={{ cursor: 'pointer' }} onClick={() => window.open(placeholder, '_blank')} />
        </div>
        <div className="update-text">
          <div className="update-title">Latest Updates</div>
          <div className="update-entry">• Bear detected at 9:34 PM - April 1, 2025</div>
          <div className="update-entry">• Bear detected at 7:22 PM - March 31, 2025</div>
          <div className="update-entry">• Cat detected at 12:41 PM - March 29, 2025</div>
        </div>
      </div>
      <CardDisplay data={cardData} />
    </div>
  );
};

export default Dashboard;