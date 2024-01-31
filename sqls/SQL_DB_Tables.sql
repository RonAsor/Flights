-- Create Countries Table
CREATE TABLE Countries (
    Id INT PRIMARY KEY IDENTITY,
    Country_Name VARCHAR(255) UNIQUE,
);
go
-- Create User Roles Table
CREATE TABLE User_Roles (
    Id INT PRIMARY KEY IDENTITY,
    Role_Name VARCHAR(255) UNIQUE
);
go
-- Create Users Table
CREATE TABLE Users (
    Id BIGINT PRIMARY KEY IDENTITY,
    Username VARCHAR(255) UNIQUE,
    Password TEXT,
    Email VARCHAR(255) UNIQUE,
    User_Role INT FOREIGN KEY REFERENCES User_Roles(Id),
);
go
-- Create Airline Companies Table
CREATE TABLE Airline_Companies (
    Id BIGINT PRIMARY KEY IDENTITY,
    Airline_Name VARCHAR(255) UNIQUE,
    Country_Id INT FOREIGN KEY REFERENCES Countries(Id),
	User_Id BIGINT FOREIGN KEY REFERENCES Users(Id)
);
go
-- Create Customers Table
CREATE TABLE Customers (
    Id BIGINT PRIMARY KEY IDENTITY,
    First_Name TEXT,
    Last_Name TEXT,
    Address TEXT,
    Phone_No VARCHAR(255) UNIQUE,
    Credit_Card_No VARCHAR(255) UNIQUE,
    User_Id BIGINT FOREIGN KEY REFERENCES Users(Id) UNIQUE
);
go
-- Create Administrators Table
CREATE TABLE Administrators (
    Id INT PRIMARY KEY IDENTITY,
    First_Name TEXT,
    Last_Name TEXT,
    User_Id BIGINT FOREIGN KEY REFERENCES Users(Id)
);
go
-- Create Flights Table
CREATE TABLE Flights (
    Id BIGINT PRIMARY KEY IDENTITY,
    Airline_Company_Id BIGINT FOREIGN KEY REFERENCES Airline_Companies(Id),
    Origin_Country_Id INT FOREIGN KEY REFERENCES Countries(Id),
    Destination_Country_Id INT FOREIGN KEY REFERENCES Countries(Id),
    Departure_Time DATETIME,
    Landing_Time DATETIME,
    Remaining_Tickets INT
);
go
-- Create Tickets Table
CREATE TABLE Tickets (
    Id BIGINT PRIMARY KEY IDENTITY,
    Flight_Id BIGINT FOREIGN KEY REFERENCES Flights(Id) not null,
    Customer_Id BIGINT FOREIGN KEY REFERENCES Customers(Id) not null
	CONSTRAINT UQ_Tickets UNIQUE (Flight_Id,Customer_Id)
);
go
--Roles init with default role values
--INSERT INTO User_Roles values ('Customer'),('Flight Company'),('Administrator')
go


--procedure that takes a username and returns airline names associated with that username
ALTER PROCEDURE prc_get_airline_by_username @_username varchar(255)
as
	begin
		select ac.Airline_Name from Users u join Airline_Companies ac on u.id=ac.User_Id where u.Username = @_username
	end
go

--procedure that takes a username and returns customer full name associated with that username
ALTER PROCEDURE prc_get_customer_by_username @_username varchar(255)
as
	begin
		select concat(c.First_Name,' ',c.Last_Name) from Users u join Customers c on u.id=c.User_Id where u.Username = @_username
	end
go

--procedure that takes a username and returns anything associated with that username, for easier access to the db
ALTER PROCEDURE prc_get_user_by_username @_username varchar(255)
as
	begin
		select * from Users u where u.Username = @_username
	end
go

--procedure that takes 3 parameters: origin country id, destination country id, and date. and returns all the flights associated with those parameters
CREATE PROCEDURE prc_get_flights_by_parameters @_origin_country_id int, @_destination_country_id int, @_date date
as
	begin
		select * from Flights f where f.Destination_Country_Id = @_destination_country_id and f.Origin_Country_Id = @_origin_country_id and f.Departure_Time=@_date
	end
go

--a procedure that takes an airline company id and returns all the flights associated with that airline company
CREATE PROCEDURE prc_get_flights_by_airline_id @_airline_id bigint
as
	begin
	select * from Airline_Companies ac join Flights f on ac.Id=f.Airline_Company_Id
	end
go

--a procedure that takes all the landings within range of 12 hours from current time at the selected country
CREATE PROCEDURE prc_get_arrival_flights @_country_id int
as
	begin	
	select * from Flights f where @_country_id=f.Origin_Country_Id and DATEDIFF(HOUR,f.Landing_Time,GETDATE())<12
	end
go

--same, only for departures
CREATE PROCEDURE prc_get_departure_flights @_country_id int
as
	begin	
	select * from Flights f where @_country_id=f.Origin_Country_Id and DATEDIFF(HOUR,f.Departure_Time,GETDATE())<12
	end
go

--a procedure that takes a customer id and returns all the flight tickets of that customer
CREATE PROCEDURE prc_get_tickets_by_customer @_customer_id bigint
as
	begin
	select * from Tickets t where t.Customer_Id=@_customer_id
	end
go


begin
select * from Airline_Companies
select * from Countries
select * from Flights
select * from User_Roles
select * from Administrators
select * from Customers
select * from Users

select * from Tickets
end
go
---test for recent time
insert into Flights values (3,1,1,'2024-01-19 00:00:00','2024-01-19 02:00:00',5)

--order of deletions
delete from Tickets
delete from Customers
delete from Administrators


insert into Administrators values ('eli','israeli',1)

insert into Users values ('aspoidrhap','hkjfl','asrron1@gmail.com',2)
insert into Countries values ('Israel','')
insert into Airline_Companies values ('chakair',1,2) --using int as ids
insert into Customers values ('Ron','Asor','m.h','028502375','5598293','2')
insert into Flights values (3,1,1,'2023-05-05 00:00:00','2023-08-05 00:00:00',5)
insert into Tickets values (2,26)
exec prc_get_airline_by_username 'ronasor'
exec prc_get_customer_by_username 'ronasor'
exec prc_get_arrival_flights 1
exec prc_get_departure_flights 1
exec prc_get_flights_by_airline_id 3
exec prc_get_flights_by_parameters 1,1, '2023-05-05'
exec prc_get_tickets_by_customer 1
exec prc_get_user_by_username 'ronasor'
go

