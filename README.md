**Cloud Voting System**

A containerized microservices-based online voting platform built with Flask, RabbitMQ, SQLite, Docker, and Docker Compose.

CloudVote demonstrates how a distributed voting system can be designed using event-driven architecture, service isolation, and asynchronous vote processing.

**Architecture**

┌─────────────┐  
│ Frontend │  
└──────┬──────┘  
│  
▼  
┌─────────────┐  
│ Vote API │  
└──────┬──────┘  
│ Publish Vote  
▼  
┌─────────────┐  
│ RabbitMQ │  
└──────┬──────┘  
│ Consume Vote  
▼  
┌─────────────┐  
│ Vote Worker │  
└──────┬──────┘  
│ Store Results  
▼  
┌─────────────┐  
│ DB Service │  
└─────────────┘  
  
▲  
│  
┌─────────────┐  
│ Admin Panel │  
└─────────────┘

**Features**

*   OTP-based voter verification
*   Secure voter authentication workflow
*   Candidate selection and vote casting
*   Asynchronous vote processing using RabbitMQ
*   Admin dashboard for election monitoring
*   Constituency-wise vote tracking
*   Containerized deployment with Docker
*   Microservices architecture
*   REST API communication between services

**Technology Stack**

**Backend**

*   Python 3
*   Flask
*   SQLite
*   RabbitMQ

**DevOps**

*   Docker
*   Docker Compose

**Frontend**

*   HTML
*   CSS
*   JavaScript
*   Flask Templates

**Project Structure**

cloudvote-docker/  
│  
├── frontend/ # User-facing voting application  
├── vote-api/ # Vote submission API  
├── vote-worker/ # Background vote processor  
├── db-service/ # Database service  
├── admin/ # Election administration dashboard  
│  
├── docker-compose.yml  
├── .env  
├── README.md  
│  
└── docs/

**Services Overview**

**Frontend Service**

Handles:

*   Voter login
*   OTP verification
*   Candidate selection
*   Vote submission

**Vote API Service**

Responsible for:

*   Receiving votes
*   Validating voter eligibility
*   Publishing vote events to RabbitMQ

**Vote Worker Service**

Responsible for:

*   Consuming vote messages
*   Processing vote records
*   Updating election results

**Database Service**

Provides:

*   Voter data management
*   Vote storage
*   Election statistics

**Admin Service**

Provides:

*   Election monitoring
*   Result visualization
*   Administrative controls

**Getting Started**

**Prerequisites**

Install:

*   Docker
*   Docker Compose

Verify installation:

docker --version  
docker compose version

**Installation**

Clone the repository:

git clone https://github.com/<your-username>/cloudvote.git  
cd cloudvote

Create environment variables:

cp .env.example .env

Update values as required.

**Running the Application**

Build and start all services:

docker compose up --build

Run in detached mode:

docker compose up -d --build

Stop all services:

docker compose down

**Service Endpoints**

| Service | URL |
| --- | --- |
| Frontend | http://localhost:5000 |
| Vote API | http://localhost:5001 |
| Database Service | http://localhost:5002 |
| Admin Dashboard | http://localhost:5003 |
| RabbitMQ Management | http://localhost:15672 |

**RabbitMQ Dashboard**

Default credentials:

Username: guest  
Password: guest

Access:

http://localhost:15672

**Environment Variables**

Example:

DOCKERHUB\_USER=your-dockerhub-username

Additional variables may be configured depending on deployment requirements.

**API Workflow**

**Voting Process**

1.  Voter enters voter ID.
2.  OTP is generated and verified.
3.  Voter selects a candidate.
4.  Vote API validates voter status.
5.  Vote is published to RabbitMQ.
6.  Vote Worker consumes the message.
7.  Vote is stored in the database.
8.  Results are updated.

**Development**

Build a specific service:

docker compose build frontend

View logs:

docker compose logs -f

View logs for a service:

docker compose logs -f vote-api

**Known Limitations**

Current version is intended for educational and demonstration purposes.

Areas for future improvement:

*   Persistent database volumes
*   Enhanced security controls
*   JWT authentication
*   HTTPS support
*   Database migration to PostgreSQL
*   High-availability RabbitMQ setup
*   Distributed deployment support
*   Improved duplicate-vote protection
*   Production-grade logging and monitoring

**Future Enhancements**

*   Multi-constituency elections
*   Real OTP integration (SMS/Email)
*   Role-based access control
*   Kubernetes deployment
*   CI/CD pipelines
*   Real-time analytics dashboard
*   Audit logging
*   Election reporting

**Security Notice**

This project is designed for learning and demonstration purposes and should not be used for real-world elections without substantial security, reliability, and compliance enhancements.

**License**

MIT License

Feel free to use, modify, and distribute this project for educational and non-commercial purposes.

**Author**

**Shaik Mahammad Muqhthaar Ahmad**

B. Tech Data Science Student

GitHub: [https://github.com/Muqthaar](https://github.com/Muqthaar)
