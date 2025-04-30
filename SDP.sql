DROP DATABASE if EXISTS sdplogin;
CREATE DATABASE sdplogin;
USE sdplogin;

CREATE TABLE USERPASS(
	ID INT AUTO_INCREMENT PRIMARY KEY,
    Username varchar(20) NOT NULL,
    Password varchar(20) NOT NULL,
);

INSERT INTO USERPASS (Username, Password)
VALUES
('Test', 'Password');