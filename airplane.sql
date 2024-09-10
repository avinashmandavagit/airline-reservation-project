drop database Airline_Reservation_System;
create database Airline_Reservation_System;
use Airline_Reservation_System;

create table airplane(
airplane_id int auto_increment primary key,
airplane_name varchar(255) not null,
airplane_number varchar(255) not null,
first_class_no_of_seats varchar(255) not null,
business_class_no_of_seats varchar(255) not null,
economy_class_no_of_seats varchar(255) not null,
picture varchar(255) not null
);

create table customer(
customer_id int auto_increment primary key,
name varchar(255) not null,
phone varchar(255) not null,
email varchar(255) not null,
password varchar(255) not null,
gender varchar(255) not null,
address varchar(255) not null
);

create table airport(
airport_id int auto_increment primary key,
airport_name varchar(255) not null,
airport_code varchar(255) not null
);

create table flight(
flight_id int auto_increment primary key,
from_airport varchar(255) not null,
to_airport varchar(255) not null,
first_class_price varchar(255) not null,
business_class_price varchar(255) not null,
economy_class_price varchar(255) not null,
despature datetime not null,
arrival datetime not null,
date datetime not null,
gate_number varchar(255) not null,
search_date varchar(255) not null,
airplane_id int,
from_airport_id int,
to_airport_id int,
foreign key(airplane_id) references airplane(airplane_id),
foreign key(from_airport_id) references airport(airport_id),
foreign key(to_airport_id) references airport(airport_id)
);


create table bookings(
booking_id int auto_increment primary key,
class_type varchar(255) not null,
total_amount varchar(255) not null,
date datetime not null,
status varchar(255) not null,
seat_numbers varchar(255) not null,
flight_id int,
customer_id int,
foreign key(customer_id) references customer(customer_id),
foreign key(flight_id) references flight(flight_id)
);



create table boarding_pass(
boarding_pass_id int auto_increment primary key,
passenger_name varchar(255) not null,
seat_number varchar(255) not null,
gate_number varchar(255) not null,
boarding_time datetime not null,
to_airport varchar(255) not null,
from_airport varchar(255) not null,
booking_id int,
foreign key(booking_id) references bookings(booking_id)
);

alter table bookings modify date datetime not null;

create table payment(
payment_id int auto_increment primary key,
date varchar(255) not null,
amount varchar(255) not null,
card_number varchar(255) not null,
holder_name varchar(255) not null,
status varchar(255) not null,
booking_id int,
foreign key(booking_id) references bookings(booking_id)
);