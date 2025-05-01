DROP DATABASE if EXISTS sdplogin;
CREATE DATABASE sdplogin;
USE sdplogin;

CREATE TABLE USERPASS(
    Username varchar(20) NOT NULL,
    Password varchar(20) NOT NULL,
    PRIMARY KEY(Username)
);

INSERT INTO USERPASS
VALUES
('Test', 'Password');