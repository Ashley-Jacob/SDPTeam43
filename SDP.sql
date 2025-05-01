DROP DATABASE if EXISTS sdp;
CREATE DATABASE sdp;
USE sdp;

CREATE TABLE USERPASS(
	ID INT AUTO_INCREMENT PRIMARY KEY,
    Username varchar(255) NOT NULL,
    Password varchar(255) NOT NULL
);

INSERT INTO USERPASS (Username, Password)
VALUES
('Test', 'Password');