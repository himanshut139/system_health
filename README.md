# Cross-Platform Machine Health Monitoring System

A system that collects machine health data via a cross-platform utility and displays it on an admin dashboard.  
Includes:

- **System Utility (Client)** — Cross-platform binary (`bin/` folder contains ready-to-download builds for Windows, Linux, macOS)
- **Backend API** — Receives machine data
- **Admin Dashboard** — Vue 3 frontend to view & filter machine statuses

---

## 📦 Deliverables

### Repository Structure

---

project-root/
├── bin/ # Prebuilt client binaries (Windows, Linux, macOS)
├── client/ # Source code for cross-platform client utility
│ └── health_client.py
├── frontend/ # Vue 3 frontend app
│ └── ...
├── server/ # Flask backend API
│ ├── app.py
│ └── requirements.txt
└── README.md


---

## 🚀 Setup Instructions

1️⃣ Run the Backend

> Requires **Python 3.9+**

```bash
cd server
python -m venv venv
source venv/bin/activate    
pip install -r requirements.txt
python app.py


Backend runs at:

http://localhost:5000


2️⃣ Run the Frontend
Requires Node.js 16+

bash-  
cd frontend
npm install
npm run dev


Frontend runs at:

http://localhost:5173


Set the API URL in frontend/.env:

VITE_API_BASE_URL=http://localhost:5000

---------------------


Using the System Utility
Pre-built binaries are available in the Releases section of this repository.

Windows
Download: health_client_windows.exe

Open Command Prompt and run:

powershell

health_client_windows.exe
The utility will start in the background and report periodically.

Linux
Download: health_client_ubuntu-latest

Make it executable:

bash

chmod +x health_client_ubuntu-latest
./health_client_ubuntu-latest
macOS
Download: health_client_macos-latest

Make it executable:

bash

chmod +x health_client_macos-latest
./health_client_macos-latest

---------------

Features
Checks disk encryption status

Checks OS update status

Verifies antivirus presence

Ensures sleep settings ≤ 10 min

Sends updates only if changes are detected

Low resource usage

Admin dashboard for viewing and filtering machine statuses