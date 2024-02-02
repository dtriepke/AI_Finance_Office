

DROP TABLE IF EXISTS [Products];

DROP TABLE IF EXISTS [Employees];

DROP TABLE IF EXISTS [JournalEntries];



-- Create 'Products' Table
CREATE TABLE Products (
    ProductID INT PRIMARY KEY,
    ProductName VARCHAR(255),
    UnitPrice DECIMAL(10, 2)
);

-- Create 'Employees' Table
CREATE TABLE Employees (
    EmployeeID INT PRIMARY KEY,
    EmployeeName VARCHAR(255)
);

-- Create 'JournalEntries' Table
CREATE TABLE JournalEntries (
    EntryID INT PRIMARY KEY,
    EntryDate DATE,
    ProductID INT,
    Quantity INT,
    UnitPrice DECIMAL(10, 2),
    Discount DECIMAL(5, 2),
    TotalPrice DECIMAL(10, 2),
    EntryType VARCHAR(50),
    EmployeeID INT,
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID),
    FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
);


-- Inserting into 'Products'
INSERT INTO Products (ProductID, ProductName, UnitPrice) VALUES
(1, 'Hard Drive', 80.00),
(2, 'Memory Card', 20.00),
(3, 'Keyboard', 25.00),
(4, 'Mouse', 15.00),
(5, 'Monitor', 150.00),
(6, 'Graphics Card', 200.00),
(7, 'Processor', 300.00),
(8, 'Motherboard', 120.00),
(9, 'Power Supply', 75.00),
(10, 'SSD', 100.00);


-- Inserting into 'Employees'
INSERT INTO Employees (EmployeeID, EmployeeName) VALUES
(1, 'John Doe'),
(2, 'Jane Smith'),
(3, 'Emma Johnson'),
(4, 'Mike Brown'),
(5, 'Sarah Davis');


-- Inserting the first 10 sales events with discounts into 'JournalEntries'
INSERT INTO JournalEntries (EntryID, EntryDate, ProductID, Quantity, UnitPrice, Discount, TotalPrice, EntryType, EmployeeID) VALUES
(1, '2024-01-01', 1, 2, 80.00, 5.00, 155.00, 'Sale', 1),
(2, '2024-01-02', 2, 3, 20.00, 2.00, 58.00, 'Sale', 2),
(3, '2024-01-03', 3, 1, 25.00, 1.00, 24.00, 'Sale', 3),
(4, '2024-01-04', 4, 2, 15.00, 0.50, 29.50, 'Sale', 4),
(5, '2024-01-05', 5, 1, 150.00, 10.00, 140.00, 'Sale', 5),
(6, '2024-01-06', 6, 1, 200.00, 20.00, 180.00, 'Sale', 1),
(7, '2024-01-07', 7, 1, 300.00, 15.00, 285.00, 'Sale', 2),
(8, '2024-01-08', 8, 1, 120.00, 5.00, 115.00, 'Sale', 3),
(9, '2024-01-09', 9, 3, 75.00, 7.50, 217.50, 'Sale', 4),
(10, '2024-01-10', 10, 2, 100.00, 10.00, 190.00, 'Sale', 5);

-- Inserting the next 10 sales events with discounts into 'JournalEntries'
INSERT INTO JournalEntries (EntryID, EntryDate, ProductID, Quantity, UnitPrice, Discount, TotalPrice, EntryType, EmployeeID) VALUES
(11, '2024-01-11', 1, 3, 80.00, 5.00, 225.00, 'Sale', 2),
(12, '2024-01-12', 2, 4, 20.00, 2.00, 72.00, 'Sale', 3),
(13, '2024-01-13', 3, 2, 25.00, 1.00, 48.00, 'Sale', 4),
(14, '2024-01-14', 4, 3, 15.00, 0.50, 43.50, 'Sale', 5),
(15, '2024-01-15', 5, 2, 150.00, 10.00, 280.00, 'Sale', 1),
(16, '2024-01-16', 6, 1, 200.00, 20.00, 180.00, 'Sale', 2),
(17, '2024-01-17', 7, 1, 300.00, 15.00, 285.00, 'Sale', 3),
(18, '2024-01-18', 8, 2, 120.00, 5.00, 230.00, 'Sale', 4),
(19, '2024-01-19', 9, 4, 75.00, 7.50, 290.00, 'Sale', 5),
(20, '2024-01-20', 10, 1, 100.00, 10.00, 90.00, 'Sale', 1);

-- Inserting sales events 21 to 30 with discounts into 'JournalEntries'
INSERT INTO JournalEntries (EntryID, EntryDate, ProductID, Quantity, UnitPrice, Discount, TotalPrice, EntryType, EmployeeID) VALUES
(21, '2024-01-21', 10, 2, 100.00, 10.00, 180.00, 'Sale', 2),
(22, '2024-01-22', 1, 1, 80.00, 8.00, 72.00, 'Sale', 3),
(23, '2024-01-23', 2, 5, 20.00, 1.00, 95.00, 'Sale', 4),
(24, '2024-01-24', 3, 3, 25.00, 2.50, 67.50, 'Sale', 5),
(25, '2024-01-25', 4, 2, 15.00, 1.00, 28.00, 'Sale', 1),
(26, '2024-01-26', 5, 1, 150.00, 15.00, 135.00, 'Sale', 2),
(27, '2024-01-27', 6, 2, 200.00, 20.00, 360.00, 'Sale', 3),
(28, '2024-01-28', 7, 1, 300.00, 25.00, 275.00, 'Sale', 4),
(29, '2024-01-29', 8, 2, 120.00, 10.00, 220.00, 'Sale', 5),
(30, '2024-01-30', 9, 3, 75.00, 5.00, 210.00, 'Sale', 1);

-- Inserting sales events 31 to 40 with discounts into 'JournalEntries'
INSERT INTO JournalEntries (EntryID, EntryDate, ProductID, Quantity, UnitPrice, Discount, TotalPrice, EntryType, EmployeeID) VALUES
(31, '2024-02-01', 10, 3, 100.00, 10.00, 270.00, 'Sale', 2),
(32, '2024-02-02', 1, 2, 80.00, 5.00, 150.00, 'Sale', 3),
(33, '2024-02-03', 2, 1, 20.00, 2.00, 18.00, 'Sale', 4),
(34, '2024-02-04', 3, 4, 25.00, 3.00, 88.00, 'Sale', 5),
(35, '2024-02-05', 4, 1, 15.00, 1.50, 13.50, 'Sale', 1),
(36, '2024-02-06', 5, 2, 150.00, 15.00, 270.00, 'Sale', 2),
(37, '2024-02-07', 6, 1, 200.00, 10.00, 190.00, 'Sale', 3),
(38, '2024-02-08', 7, 3, 300.00, 30.00, 810.00, 'Sale', 4),
(39, '2024-02-09', 8, 1, 120.00, 12.00, 108.00, 'Sale', 5),
(40, '2024-02-10', 9, 2, 75.00, 7.50, 135.00, 'Sale', 1);


-- Inserting the first 10 retour events into 'JournalEntries'
INSERT INTO JournalEntries (EntryID, EntryDate, ProductID, Quantity, UnitPrice, Discount, TotalPrice, EntryType, EmployeeID) VALUES
(41, '2024-02-11', 1, 1, 80.00, 0.00, 80.00, 'Retour', 1),
(42, '2024-02-12', 2, 2, 20.00, 0.00, 40.00, 'Retour', 2),
(43, '2024-02-13', 3, 1, 25.00, 0.00, 25.00, 'Retour', 3),
(44, '2024-02-14', 4, 1, 15.00, 0.00, 15.00, 'Retour', 4),
(45, '2024-02-15', 5, 1, 150.00, 0.00, 150.00, 'Retour', 5),
(46, '2024-02-16', 6, 1, 200.00, 0.00, 200.00, 'Retour', 1),
(47, '2024-02-17', 7, 1, 300.00, 0.00, 300.00, 'Retour', 2),
(48, '2024-02-18', 8, 1, 120.00, 0.00, 120.00, 'Retour', 3),
(49, '2024-02-19', 9, 2, 75.00, 0.00, 150.00, 'Retour', 4),
(50, '2024-02-20', 10, 1, 100.00, 0.00, 100.00, 'Retour', 5);
