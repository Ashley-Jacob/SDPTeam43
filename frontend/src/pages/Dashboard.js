import React, { useEffect, useState } from "react";
import placeholder from '../resources/placeholder.jpg';
import './Dashboard.css';
import { BiRefresh } from "react-icons/bi";

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
        <span>{props.timeInfo}</span>
        <span>{props.info}</span>
      </div>
    </div>
  )
}



const Dashboard = () => {
  const [cardData, setCardData] = useState([]);
  const [startUp, setStartUp] = useState(true)
  const [updateData, setUpdateData] = useState([])

  const CardDisplay = (props) => {

    if (startUp) {
      refreshApp()
      setStartUp(false)
    }

    return (
      <div className="cards">
        {cardData.reverse().map((card, index) => (

          <Card
            key={index}
            animal={card.animal}
            info={card.info}
            type={card.type}
            imgURL = {card.imgUrl}
            timeInfo={card.timeInfo}
          />
          
        ))}
      </div>
    );
  };

  const Updates = (props) => {

    return (
      
      <div className="updates">
        <div className="update-title">Latest Updates</div>
        {updateData.reverse().map((card, index) => (
          <div className="update-text"><span>• {card}</span></div>
        )).slice(0,3)}
      </div>
    );
  }

  const refreshApp = async () => 
  {
    const response = await fetch("http://localhost:5000/geturls"); 
    const imagePaths = (await response.json())["urls"]; 

    var notifs = []

    const updatedData = imagePaths.map(path => {
        const fullUrl = `http://localhost:5000/${path.url}`;
        const animal = path.animal
        const dateStr = path.date
        const timeInfo = path.timeInfo

        notifs.push(animal + " detected at " + timeInfo + " - " + dateStr);

        console.log(fullUrl)

        return {
          animal: animal,
          info: dateStr,
          type: "bulk",
          imgUrl: fullUrl,
          timeInfo: timeInfo
        };
      });

    setUpdateData(notifs)
    setCardData(updatedData.reverse());
  };

  return (
    <div className="dash-content">
      <div className="page-name">
        <span>Dashboard</span>
        <div className='refresh'>
          <button className="refresh" onClick = {refreshApp}>Refresh</button>
        </div>
      </div>
      <div className="notifications">
        <div className="latest-card">
          <img src="http://localhost:5000/static/camera.png" alt="latest detection" style={{ cursor: 'pointer' }} onClick={() => window.open(placeholder, '_blank')} />
        </div>
        <div className="update-text">
          <Updates />
        </div>
      </div>
      <CardDisplay data={cardData} />
    </div>
  );
};

export default Dashboard;