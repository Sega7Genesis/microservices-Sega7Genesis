-- file: 10-create-user-and-db.sql
CREATE ROLE program WITH PASSWORD 'test';
CREATE DATABASE orders OWNER program;
CREATE DATABASE store OWNER program;
CREATE DATABASE warehouse OWNER program;
CREATE DATABASE warranty OWNER program;
ALTER ROLE program WITH LOGIN;