# Committee Workflow System

## Overview

Committee Workflow System (CommOps) is a comprehensive web-based platform designed to streamline the entire lifecycle of academic committees in universities. 
Built with Python and Streamlit, the system manages committee creation, faculty applications, member selection, direct assignment, and service history tracking.
The platform supports seven distinct user roles with appropriate permissions and provides complete audit trails for all actions.

## Key Features

The system implements a complete committee lifecycle from draft to archival with automated workflows, notifications, and status tracking.
Faculty members can view eligible committees, submit applications, track status, and view service history.
Administrators can initiate committees, review applications, directly assign members, and monitor workload distribution. 
All assignments generate notifications, update workload calculations, and create audit log entries.

## Technical Architecture

The application is built on a modern Python stack with Streamlit as the frontend framework and SQLite as the database.
The modular backend includes separate modules for visibility rules, eligibility checks, workflow management, selection engine, notifications, workload calculations,
and export functionality. The system includes comprehensive audit logging for all major actions.

## Security and Data Integrity

Security measures include SHA-256 password hashing, account lockout after five failed attempts, role-based access control, and input validation.
The system maintains data integrity through foreign key constraints, unique constraints, and transaction-based operations. Automatic migration capabilities 
ensure smooth schema upgrades.

## Deployment

The application is designed for deployment on Render.com with persistent disk storage for SQLite data. 
The deployment is fully automated through GitHub integration with every push triggering a rebuild. 
The free tier provides 750 hours of runtime per month, making it ideal for academic projects.

## Requirements and Installation

The system requires Python 3.11 or higher and can be installed by cloning the repository, creating a virtual environment, and installing dependencies from requirements.txt.
Database initialization and dummy data seeding are handled automatically on first run.

## Conclusion

Committee Workflow System provides a comprehensive, secure, and efficient solution for managing academic committees in universities. 
Its role-based access control, automated workflows, transparent processes, and complete audit trails address the critical needs of academic institutions for accountability 
and efficiency in committee management.
The system is production-ready, deployable on professional hosting platforms, and designed to scale with institutional requirements.
