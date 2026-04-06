# Coldguard-UdhbavaHackathon
Cold Storage Temperature Monitoring System – Uttar Pradesh (AG-03)

📌 Overview

Cold storage facilities in Uttar Pradesh store potatoes and vegetables, but manual temperature checking, missing records, and no alert mechanism often lead to sudden spoilage and financial loss.
This project proposes a software-based Cold Storage Monitoring System that records temperature (entered manually or via digital input), detects abnormal values, tracks power failures, stores historical data, and provides alerts to users.
The focus is on system design, logic, data handling, and documentation, without using any hardware sensors.

🎯 Objective

To design a system that maintains temperature records, tracks power failures, sends alerts for abnormal values, supports multiple storage units, and allows remote monitoring through a software application.

📘 Functional Features
Allow users to record temperature values (manual/digital input).
Store all readings in the database.
Detect abnormal temperature changes and trigger alerts automatically.
Display real-time status through a dashboard.
Enable managers to log maintenance activities.
Generate daily reports and summaries.
Support multiple cold storage units.
Track and record power failures.
Maintain historical logs for analytics.
Provide remote monitoring through a web/mobile interface.
Notify users via messages (SMS/Email).
Provide basic analytics and visualizations.
📚 Background
Workers manually check temperatures and write them in notebooks.
These records may be inaccurate, incomplete, or misplaced.
There is no automatic alert system when temperature reaches unsafe levels.
Power failures are not logged properly.
These issues cause spoilage and financial losses.

The proposed system digitalizes the entire process and increases reliability.

🛠️ Overall Approach

The system replaces handwritten logs with a centralized digital application.
Workers or managers enter temperature values and power failure information directly into the system.
The backend processes this data, identifies abnormal values, triggers alerts, and stores all information for reports and analytics.
A dashboard provides real-time visibility and supports multi-storage monitoring.

🏗️ System Architecture Overview

The system architecture consists of:

1. Input Layer
Manual entry of temperature readings
Manual entry of power outage information
Maintenance and activity logs
2. Processing Layer (Backend)
Data validation and storage
Threshold-based alert engine
Report generator
Analytics and trend detection
3. Database Layer
Temperature logs
Power failure logs
Maintenance records
User profiles
Storage unit information
4. User Interface Layer
Web/Mobile dashboard
Daily reports
Notifications
Multi-storage management

This software-first architecture aligns with project constraints and avoids hardware dependencies.

🔑 Key Components
Backend (Core System)
Data entry API
Alert/notification engine
Maintenance log module
Power failure tracking
Report generation module
Historical data manager
Frontend (User Interface)
Real-time dashboard
Graphs & analytics
Temperature entry screen
Storage unit selection
Message notification panel
Database
Tables for temperature, users, units, reports, maintenance logs, and power failures
🔁 Data Flow Summary
User enters temperature/power status in the system
Backend validates and saves the data
If temperature crosses limits, backend triggers an alert
Data is stored in databases for history, analytics, and reports
Dashboard shows updated readings in real time
Daily reports are generated automatically
Users receive alerts via SMS/email
⚙️ Design Decisions
Manual data entry chosen due to no sensors and minimal hardware use
Threshold-based alert rules to easily detect unsafe conditions
Centralized database for multi-storage management
Modular backend architecture to support future upgrades
Web/mobile UI for better accessibility
Using free tools and open-source technologies to meet constraints
Storing historical data to provide meaningful analytics
📌 Constraints
No sensors or hardware devices
Must use only free tools
Limited development time
Architecture, logic, and documentation are the main focus
📄 Deliverables

This repository includes:

✔ README (this file)
✔ System architecture diagram
✔ Problem understanding
✔ Solution approach
✔ Limitations & future scope
✔ Presentation slides
✔ Partial source code
👥 Stakeholders
Farmers
Cold storage owners
Storage managers/supervisors
Technicians
Software development team
Dashboard users (remote monitors)
❌ Existing System Limitations
Fully manual and error-prone
No automatic alerts
Paper logs can be lost/damaged
No historical analytics
No remote monitoring
Poor tracking of power failures
🤝 Assumptions
Temperature values are entered manually but accurately
Basic internet access is available
Users know how to use digital systems
Threshold values are predefined
Storage units have unique identification numbers
🚀 Future Scope
Integrate actual IoT sensors in next version
AI-based spoilage prediction
Automated cooling control
Mobile app offline mode
Government dashboard integration
