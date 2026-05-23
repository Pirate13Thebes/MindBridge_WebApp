# 🌉 MindBridge Postpartum Support Platform
### A Dual-Interface Full-Stack Clinical Application with Live RDBMS & NoSQL Databases

MindBridge is a state-of-the-art support platform built to empower postpartum clinical teams and patients in recovery. The architecture utilizes a **Flask REST API backend**, a **TypeScript React frontend**, and a **Python CLI application** running on a unified live database layer utilizing **MySQL (RDBMS)** and **MongoDB (NoSQL)**.

---

## 🛠️ System Architecture & Database Mapping
* **Structured RDBMS (MySQL)**: Manages secure user profiles, clinical therapy session schedules, and medication compliance follow-up records.
* **Unstructured Document Store (MongoDB)**: Manages preloaded stage recovery physical exercises, mental health clinical guides, and confidential patient mood journals.

---

## 🚀 Quick Start Local Execution Guide
Follow these step-by-step instructions to clone, seed, and launch the platform on your local machine.

### 📋 Prerequisites
Ensure you have the following installed locally:
1. **Python 3.10+**
2. **Node.js v18+**
3. **MySQL Server** (Listening on standard port `3306`)
4. **MongoDB Community Server** (Listening on standard port `27017`)

---

### 📥 Step 1: Clone the Repository
Open your terminal and clone the project:
```bash
git clone https://github.com/Pirate13Thebes/MindBridge_WebApp.git
cd MindBridge_WebApp
```

---

### 🔑 Step 2: Configure Environment Variables
Create a **`.env`** file in the root project directory and add your database credentials:
```ini
# MySQL Configuration
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_root_password
MYSQL_DATABASE=mindbridge_db

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017
MONGO_DATABASE=mindbridge

# Flask Server Config
SECRET_KEY=change-me-in-production
JWT_SECRET=jwt-secret-key
FLASK_PORT=5000

# Frontend Configuration (Vite)
VITE_API_URL=http://localhost:5000/api/v1
```

---

### 📊 Step 3: Initialize Virtual Environment and Seed 20,000 Records
The database seeder automatically initializes your SQL tables and Mongo indexes, and imports the entire 20,000 realistic clinical timeline records!

**On Windows (PowerShell):**
```powershell
# 1. Create virtual environment
python -m venv .venv

# 2. Activate virtual environment
.venv\Scripts\activate

# 3. Install backend dependencies
pip install -r requirements.txt

# 4. Stream 20,000 clinical records live into MySQL & MongoDB
python import_data_to_dbs.py
```

**On macOS/Linux:**
```bash
# 1. Create virtual environment
python3 -m venv .venv

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Install backend dependencies
pip install -r requirements.txt

# 4. Stream 20,000 clinical records live into MySQL & MongoDB
python import_data_to_dbs.py
```

---

### 🖥️ Step 4: Run the Web Application

#### **1. Start the Flask REST API Backend**
From the root project directory (with your virtual environment active):
```bash
python api/server.py
```
* The backend will serve on **`http://localhost:5000`**. You can verify connectivity by checking **`http://localhost:5000/api/health`** in your browser!

#### **2. Start the React Frontend**
Open a new terminal window, navigate to the `frontend/` directory, install packages, and boot the Vite server:
```bash
cd frontend
npm install
npm run dev
```
* Open **`http://localhost:5173`** in your web browser to browse the sleek, responsive UI dashboard!

---

### 📟 Step 5: Run the Graded Python CLI Application
If your colleagues or grading team want to evaluate the interactive CLI system instead of the web dashboard:
1. Open your terminal in the root directory.
2. Run:
   ```bash
   python cli/main.py
   ```
3. Register a new user, log in, write confidential mood journals, or login as an Administrator to view aggregated metrics and export integrated patient CSV spreadsheets!
