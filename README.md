# Crewmate

[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=FFD62E)](https://vitejs.dev/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=white)](https://firebase.google.com/)

---

## 🚀 Hackathon Quickstart
- **Demo:** [https://crewmate-demo.vercel.app](https://crewmate-demo.vercel.app)
- **Live Deployment:** [https://crewmate-app.vercel.app](https://crewmate-app.vercel.app)
- `pnpm install && pnpm dev` in `apps/crewmate-dashboard` to run locally
- No login required—just click **Sign In** to view the dashboard!

> **Disclaimer:** Crewmate is a fan-made project and is not affiliated with Among Us or Innersloth LLC. All trademarks are property of their respective owners.

## Features
- Native integration with Discord, Slack, Telegram, and Teams
- AI-powered natural language commands
- Real-time analytics and reporting
- Secure, privacy-first design
- Lightning fast onboarding
- Modern web dashboard for managing tasks, performance, and teams

---

## 🗺️ Architecture Diagram

```mermaid
flowchart TD
  U1["User (Web)"]
  U2["User (Discord/Slack/Telegram/Teams)"]
  FE["React/Vite Frontend"]
  API["API Layer"]
  DiscordBot["Discord Bot (Python)"]
  SlackBot["Slack Bot (Coming Soon)"]
  TelegramBot["Telegram Bot (Coming Soon)"]
  TeamsBot["Teams Bot (Coming Soon)"]
  Firebase["Firebase (Auth, DB, Functions)"]
  U1 -->|"Browser"| FE
  U2 -->|"Chat Commands"| DiscordBot
  FE -->|"REST/Realtime"| API
  API -->|"Realtime/REST"| Firebase
  DiscordBot -->|"Realtime/REST"| Firebase
  SlackBot -->|"Realtime/REST"| Firebase
  TelegramBot -->|"Realtime/REST"| Firebase
  TeamsBot -->|"Realtime/REST"| Firebase
  FE -->|"Realtime"| Firebase
  FE -->|"Bot Management"| DiscordBot
  FE -->|"Bot Management"| SlackBot
  FE -->|"Bot Management"| TelegramBot
  FE -->|"Bot Management"| TeamsBot
```

---

## Getting Started

### Prerequisites
- Node.js (v16+ recommended)
- pnpm or npm

### Running the Dashboard

1. Navigate to the dashboard app directory:
   ```sh
   cd crewmate/apps/crewmate-dashboard
   ```
2. Install dependencies:
   ```sh
   pnpm install
   # or
   npm install
   ```
3. Start the development server:
   ```sh
   pnpm dev
   # or
   npm run dev
   ```
4. Open [http://localhost:5174](http://localhost:5174) in your browser.

### Running the Discord Bot

1. Navigate to the Discord app directory:
   ```sh
   cd crewmate/apps/discord
   ```
2. Install Python dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Configure your bot token and Firebase credentials as needed.
4. Run the bot:
   ```sh
   python main.py
   ```

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a pull request

## License

This project is for educational and demonstration purposes. 