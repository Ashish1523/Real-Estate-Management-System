-- Create Database
CREATE DATABASE IF NOT EXISTS rems33;
USE rems33;

-- Drop existing tables if they exist
DROP TABLE IF EXISTS payment;
DROP TABLE IF EXISTS maintenance;
DROP TABLE IF EXISTS bill;
DROP TABLE IF EXISTS lease_agreements;
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
  DueDate datetime NOT NULL,  -- Changed to datetime
  Status enum('Unpaid','Paid') DEFAULT 'Unpaid',
  PRIMARY KEY (BillID),
  KEY LeaseID (LeaseID),
  CONSTRAINT bill_fk FOREIGN KEY (LeaseID) REFERENCES lease (LeaseID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Maintenance Table with AlertStatus column
CREATE TABLE maintenance (
  ReqID int NOT NULL AUTO_INCREMENT,
  LeaseID int NOT NULL,
  ReqDate datetime NOT NULL,  -- Changed to datetime to capture time
  Description text,
  Status enum('Requested','In Progress','Completed') DEFAULT 'Requested',
  AlertStatus varchar(50) DEFAULT NULL,
  PRIMARY KEY (ReqID),
  KEY LeaseID (LeaseID),
  CONSTRAINT maintenance_fk FOREIGN KEY (LeaseID) REFERENCES lease (LeaseID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Payment Table
CREATE TABLE payment (
  PaymentID int NOT NULL AUTO_INCREMENT,
  TenantID int NOT NULL,
  BillID int NOT NULL,
  PaymentDate datetime NOT NULL,  -- Changed to datetime
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

-- Create Lease Agreements Table
CREATE TABLE lease_agreements (
  AgreementID INT NOT NULL AUTO_INCREMENT,
  LeaseID INT NOT NULL,
  AgreementText TEXT NOT NULL,
  PRIMARY KEY (AgreementID),
  FOREIGN KEY (LeaseID) REFERENCES lease (LeaseID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Admin User
INSERT INTO user (Username, Password, UserType) VALUES ('admin', 'admin123', 'Admin');

-- Enable Event Scheduler (if not already enabled)
SET GLOBAL event_scheduler = ON;

-- Set a custom delimiter
DELIMITER $$

-- Trigger: Payment Confirmation Trigger (Modified)
CREATE TRIGGER before_payment_insert
BEFORE INSERT ON payment
FOR EACH ROW
BEGIN
  DECLARE expected_amount DECIMAL(10,2);
  SELECT Amount INTO expected_amount FROM bill WHERE BillID = NEW.BillID;
  IF NEW.Amount != expected_amount THEN
    -- Prevent the insertion and display an error
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Payment amount does not match the billed amount.';
  END IF;
END$$

-- Event: Automatic Maintenance Alert (runs every 1 minute)
CREATE EVENT maintenance_alert_event
ON SCHEDULE EVERY 1 MINUTE STARTS NOW()
DO
BEGIN
  UPDATE maintenance
  SET AlertStatus = 'Alert'
  WHERE Status = 'Requested' AND TIMESTAMPDIFF(MINUTE, ReqDate, NOW()) >= 2 AND (AlertStatus IS NULL OR AlertStatus != 'Alert');
END$$

-- Stored Procedure: Generate Lease Agreements (Fixed)
CREATE PROCEDURE generate_lease_agreement(IN lease_id INT)
BEGIN
  DECLARE tenant_name VARCHAR(100);
  DECLARE property_name VARCHAR(100);
  DECLARE start_date DATE;
  DECLARE end_date DATE;
  DECLARE agreement_text TEXT;

  SELECT t.Name INTO tenant_name
  FROM tenant t
  JOIN lease l ON t.TenantID = l.TenantID
  WHERE l.LeaseID = lease_id;

  SELECT p.Name INTO property_name
  FROM property p
  JOIN lease l ON p.PropertyID = l.PropertyID
  WHERE l.LeaseID = lease_id;

  SELECT StartDate, EndDate INTO start_date, end_date
  FROM lease
  WHERE LeaseID = lease_id;

  SET agreement_text = CONCAT(
    'Lease Agreement between ', tenant_name, ' (Tenant) and ', property_name, ' (Property). ',
    'Lease Start Date: ', DATE_FORMAT(start_date, '%Y-%m-%d'), '. ',
    'Lease End Date: ', DATE_FORMAT(end_date, '%Y-%m-%d'), '. ',
    'This agreement is legally binding and outlines the terms and conditions of the lease.'
  );

  INSERT INTO lease_agreements (LeaseID, AgreementText)
  VALUES (lease_id, agreement_text);
END$$

-- Event: Monthly Billing Generation (Automatic)
CREATE EVENT monthly_billing_event
ON SCHEDULE EVERY 2 MINUTE STARTS NOW()
DO
BEGIN
  CALL generate_monthly_bills();
END$$

-- Stored Procedure: Monthly Billing Generation (Modified)
CREATE PROCEDURE generate_monthly_bills()
BEGIN
  DECLARE done INT DEFAULT FALSE;
  DECLARE lease_id INT;
  DECLARE tenant_id INT;
  DECLARE amount DECIMAL(10,2);
  DECLARE lease_cursor CURSOR FOR SELECT LeaseID, TenantID FROM lease WHERE Status = 'Accepted';
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

  OPEN lease_cursor;

  read_loop: LOOP
    FETCH lease_cursor INTO lease_id, tenant_id;
    IF done THEN
      LEAVE read_loop;
    END IF;

    -- Get the rent amount from property price
    SELECT p.Price INTO amount
    FROM property p
    JOIN lease l ON p.PropertyID = l.PropertyID
    WHERE l.LeaseID = lease_id;

    -- Insert a new bill with due date 2 minutes from now (for testing)
    INSERT INTO bill (LeaseID, BillType, Amount, DueDate, Status)
    VALUES (lease_id, 'Monthly Rent', amount, DATE_ADD(NOW(), INTERVAL 2 MINUTE), 'Unpaid');

  END LOOP;

  CLOSE lease_cursor;
END$$

DELIMITER $$

DROP FUNCTION IF EXISTS calculate_late_payment_penalty$$

DELIMITER $$

-- Function: Calculate Tenant Rating
CREATE FUNCTION calculate_tenant_rating(tenant_id INT) RETURNS DECIMAL(3,2)
DETERMINISTIC
BEGIN
  DECLARE total_payments INT;
  DECLARE on_time_payments INT;
  DECLARE rating DECIMAL(3,2);

  SELECT COUNT(*) INTO total_payments FROM bill b
  JOIN lease l ON b.LeaseID = l.LeaseID
  WHERE l.TenantID = tenant_id;

  SELECT COUNT(*) INTO on_time_payments FROM bill b
  JOIN lease l ON b.LeaseID = l.LeaseID
  JOIN payment p ON b.BillID = p.BillID
  WHERE l.TenantID = tenant_id AND b.DueDate >= p.PaymentDate;

  IF total_payments = 0 THEN
    SET rating = 5.0; -- Default rating
  ELSE
    SET rating = (on_time_payments / total_payments) * 5.0;
  END IF;

  RETURN ROUND(rating, 2);
END$$

-- Reset the delimiter
DELIMITER ;

-- Enable the event scheduler
SET GLOBAL event_scheduler = ON;