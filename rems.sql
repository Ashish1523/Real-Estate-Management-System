CREATE DATABASE IF NOT EXISTS rems_3;
USE rems_3;

-- Drop existing tables
DROP TABLE IF EXISTS payment;
DROP TABLE IF EXISTS maintenance;
DROP TABLE IF EXISTS bill;
DROP TABLE IF EXISTS lease;
DROP TABLE IF EXISTS propertyimages;
DROP TABLE IF EXISTS property;
DROP TABLE IF EXISTS tenant;
DROP TABLE IF EXISTS owner;
DROP TABLE IF EXISTS user;

-- Create User Table with Admin UserType
CREATE TABLE user (
  UserID int NOT NULL AUTO_INCREMENT,
  Username varchar(50) NOT NULL,
  Password varchar(255) NOT NULL,
  UserType enum('Tenant','Owner','Admin') NOT NULL,
  PRIMARY KEY (UserID),
  UNIQUE KEY Username (Username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Tenant Table
CREATE TABLE tenant (
  TenantID int NOT NULL,
  Name varchar(100) NOT NULL,
  ContactNo varchar(15) DEFAULT NULL,
  Email varchar(100) DEFAULT NULL,
  PRIMARY KEY (TenantID),
  CONSTRAINT tenant_fk FOREIGN KEY (TenantID) REFERENCES user (UserID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Owner Table
CREATE TABLE owner (
  OwnerID int NOT NULL,
  Name varchar(100) NOT NULL,
  ContactNo varchar(15) DEFAULT NULL,
  Email varchar(100) DEFAULT NULL,
  PRIMARY KEY (OwnerID),
  CONSTRAINT owner_fk FOREIGN KEY (OwnerID) REFERENCES user (UserID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Property Table
CREATE TABLE property (
  PropertyID int NOT NULL AUTO_INCREMENT,
  OwnerID int NOT NULL,
  Name varchar(100) NOT NULL,
  Type varchar(50) DEFAULT NULL,
  Location varchar(255) DEFAULT NULL,
  Size varchar(50) DEFAULT NULL,
  Price decimal(10,2) DEFAULT NULL,
  Bedrooms int DEFAULT NULL,
  Bathrooms int DEFAULT NULL,
  Availability varchar(50) DEFAULT NULL,
  Furnished enum('Yes','No') DEFAULT NULL,
  PetFriendly enum('Yes','No') DEFAULT NULL,
  PRIMARY KEY (PropertyID),
  KEY OwnerID (OwnerID),
  CONSTRAINT property_fk FOREIGN KEY (OwnerID) REFERENCES owner (OwnerID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Lease Table
CREATE TABLE lease (
  LeaseID int NOT NULL AUTO_INCREMENT,
  TenantID int NOT NULL,
  PropertyID int NOT NULL,
  StartDate date NOT NULL,
  EndDate date NOT NULL,
  Status enum('Pending','Accepted','Rejected') DEFAULT 'Pending',
  PRIMARY KEY (LeaseID),
  KEY TenantID (TenantID),
  KEY PropertyID (PropertyID),
  CONSTRAINT lease_tenant_fk FOREIGN KEY (TenantID) REFERENCES tenant (TenantID),
  CONSTRAINT lease_property_fk FOREIGN KEY (PropertyID) REFERENCES property (PropertyID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Bill Table
CREATE TABLE bill (
  BillID int NOT NULL AUTO_INCREMENT,
  LeaseID int NOT NULL,
  BillType varchar(50) DEFAULT NULL,
  Amount decimal(10,2) NOT NULL,
  DueDate date NOT NULL,
  Status enum('Unpaid','Paid') DEFAULT 'Unpaid',
  PRIMARY KEY (BillID),
  KEY LeaseID (LeaseID),
  CONSTRAINT bill_fk FOREIGN KEY (LeaseID) REFERENCES lease (LeaseID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Maintenance Table
CREATE TABLE maintenance (
  ReqID int NOT NULL AUTO_INCREMENT,
  LeaseID int NOT NULL,
  ReqDate date NOT NULL,
  Description text,
  Status enum('Requested','In Progress','Completed') DEFAULT 'Requested',
  PRIMARY KEY (ReqID),
  KEY LeaseID (LeaseID),
  CONSTRAINT maintenance_fk FOREIGN KEY (LeaseID) REFERENCES lease (LeaseID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Payment Table
CREATE TABLE payment (
  PaymentID int NOT NULL AUTO_INCREMENT,
  TenantID int NOT NULL,
  BillID int NOT NULL,
  PaymentDate date NOT NULL,
  Amount decimal(10,2) NOT NULL,
  PRIMARY KEY (PaymentID),
  KEY TenantID (TenantID),
  KEY BillID (BillID),
  CONSTRAINT payment_tenant_fk FOREIGN KEY (TenantID) REFERENCES tenant (TenantID),
  CONSTRAINT payment_bill_fk FOREIGN KEY (BillID) REFERENCES bill (BillID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create PropertyImages Table
CREATE TABLE propertyimages (
  ImageID int NOT NULL AUTO_INCREMENT,
  PropertyID int NOT NULL,
  ImagePath varchar(255) NOT NULL,
  PRIMARY KEY (ImageID),
  KEY PropertyID (PropertyID),
  CONSTRAINT images_fk FOREIGN KEY (PropertyID) REFERENCES property (PropertyID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Admin User
INSERT INTO user (Username, Password, UserType) VALUES ('admin', 'admin123', 'Admin');

-- -- Set a custom delimiter
-- DELIMITER $$

-- -- AFTER INSERT trigger to update metrics (Example)
-- CREATE TRIGGER after_lease_insert
-- AFTER INSERT ON lease
-- FOR EACH ROW
-- BEGIN
--     -- Placeholder for actual implementation
--     -- For example, update a summary table or log the event
--     -- SET @dummy = 0;
-- END$$

-- -- AFTER UPDATE trigger to notify tenants about lease status changes
-- CREATE TRIGGER after_lease_update
-- AFTER UPDATE ON lease
-- FOR EACH ROW
-- BEGIN
--     IF NEW.Status != OLD.Status THEN
--         -- Placeholder for notification logic
--         -- Add a dummy statement to avoid syntax error
--         SET @dummy = 0;
--     END IF;
-- END$$

-- -- AFTER UPDATE trigger to create a new bill when a lease is accepted
-- CREATE TRIGGER after_lease_accept
-- AFTER UPDATE ON lease
-- FOR EACH ROW
-- BEGIN
--     IF NEW.Status = 'Accepted' AND OLD.Status != 'Accepted' THEN
--         INSERT INTO bill (LeaseID, BillType, Amount, DueDate, Status)
--         VALUES (NEW.LeaseID, 'Rent', 1000.00, CURDATE(), 'Unpaid');
--     END IF;
-- END$$

-- -- Function to calculate total unpaid bills
-- CREATE FUNCTION total_unpaid_bills() RETURNS INT
-- DETERMINISTIC
-- READS SQL DATA
-- BEGIN
--     DECLARE total INT;
--     SELECT COUNT(*) INTO total FROM bill WHERE Status='Unpaid';
--     RETURN total;
-- END$$

-- -- Reset the delimiter
-- DELIMITER ;