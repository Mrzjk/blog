# Blog & Social System

A modern full-stack blog and social platform built with Vue 3 (Frontend) and FastAPI (Backend). The project features a dark sci-fi UI design, real-time chat, a system-wide notification center, and comprehensive blog management capabilities.

[中文文档](README.zh-CN.md)

## 🚀 Key Features

*   **Modern UI/UX Design**: Dark sci-fi theme utilizing Glassmorphism effects, responsive layout, and smooth transitions.
*   **User Authentication & Security**: Secure user registration, login, and state management powered by JWT.
*   **Level & EXP System**: Interactive user progression system where active time and interactions yield EXP, automatically calculating and displaying User Levels (`Lv.X`) across comments, profiles, and chat.
*   **Blog Management System**:
    *   Rich-text editor with full Markdown support.
    *   Article categorization and tagging system.
    *   Interactions: View counts, likes, and a multi-level nested (flattened display) comment system.
    *   Personal Profile: Displays user info, EXP progress, and a paginated list of published articles.
*   **Real-time Social System (Instant Messaging)**:
    *   Low-latency real-time communication built on WebSockets.
    *   Friend System: Search users, send/accept/reject friend requests.
    *   Split-pane Chat Layout: Global friend list on the left, independent chat window on the right.
    *   **Unilateral Message Control**: Support for unilaterally clearing chat history, deleting sessions, or deleting single messages without affecting the other user's history.
*   **Admin Dashboard**:
    *   Comprehensive data statistics and real-time system monitoring.
    *   System Settings: Configure global rules like "Registration Allowed" and "Require Article Review".
    *   User Management: Manage roles, adjust EXP/Levels, and apply bans/mutes.
    *   Global Announcements: Broadcast system-wide notifications to all users.
*   **Notification Center**: Centralized management for friend requests, article likes, comments, and system announcements.

## 🛠️ Technology Stack

### Frontend
*   **Framework**: Vue 3 (Composition API, `<script setup>`)
*   **Build Tool**: Vite
*   **State Management**: Pinia
*   **Routing**: Vue Router
*   **UI Library**: Element Plus
*   **Styling**: Tailwind CSS + Custom CSS Variables
*   **Networking**: Axios, Native WebSockets

### Backend
*   **Framework**: FastAPI (Python)
*   **Database**: SQLite (managed via SQLAlchemy ORM)
*   **Authentication**: Passlib (Bcrypt), python-jose, JWT
*   **Real-time Comm**: FastAPI WebSockets

## 📂 Project Structure

```text
blog/
├── frontend/             # Vue 3 Frontend App
│   ├── src/
│   │   ├── api/          # API Integrations
│   │   ├── components/   # Reusable Vue Components
│   │   ├── layouts/      # Admin and User Layouts
│   │   ├── router/       # Vue Router Configuration
│   │   ├── store/        # Pinia State Management
│   │   ├── utils/        # Utility Functions (e.g., Axios Interceptors)
│   │   └── views/        # Page Views (Home, Chat, Admin Dashboard, etc.)
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
└── backend/              # FastAPI Backend App
    ├── app/
    │   ├── api/          # API Endpoints (Auth, Posts, Chat, Admin, etc.)
    │   ├── core/         # Core Config (Security, Environment Variables)
    │   ├── models/       # SQLAlchemy Database Models
    │   ├── schemas/      # Pydantic Validation Models
    │   └── main.py       # FastAPI Entry Point
    ├── seed.py           # Database Seeder / Mock Data Script
    └── requirements.txt  # Python Dependencies
```

## 🏁 Getting Started

### Prerequisites
*   Docker & Docker Compose (Recommended)
*   OR Node.js (v16+) and Python (v3.8+) for local development

### 🐳 Quick Start with Docker (Recommended)

The easiest way to get the project running is using Docker.

1.  Clone the repository:
    ```bash
    git clone <repository-url>
    cd blog
    ```
2.  Build and start the containers:
    ```bash
    docker-compose up -d --build
    ```
3.  Access the application:
    *   Frontend: `http://localhost`
    *   Backend API Docs: `http://localhost:8001/docs`

*Note: The backend will automatically create a local SQLite database (`blog_social.db`) on its first run.*

### 💻 Local Development Setup

If you prefer to run the frontend and backend separately for development:

#### Backend Setup

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```
2.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Initialize the database and generate test data (Highly recommended for a rich preview):
    ```bash
    python seed.py
    ```
4.  Start the FastAPI server (Runs on port 8001 by default):
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
    ```
    *Once started, you can access the auto-generated API documentation via Swagger UI at `http://127.0.0.1:8001/docs`.*

### Frontend Setup

1.  Navigate to the frontend directory:
    ```bash
    cd frontend
    ```
2.  Install Node dependencies:
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    ```
    *The frontend will typically run on `http://localhost:5173` or `http://localhost:5174`. Check the console output.*

## 📝 Configuration

Ensure the frontend is correctly pointing to the backend API address.
If the backend port changes, please verify the proxy settings in `frontend/vite.config.ts` or the `baseURL` in `frontend/src/utils/request.ts` to ensure it matches your FastAPI server port.