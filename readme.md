# 📰 CommuniCare

**CommuniCare** is an AI-powered FastAPI service that fetches local health-related news for a given city (default: Delhi), filters for **notable or urgent public health issues**, and generates a reader-friendly **Markdown newsletter** using **Google Gemini LLM**.

---

## 💡 What It Does

- Queries [newsdata.io](https://newsdata.io) for the latest **health news** in India
- Extracts and filters articles based on **public health relevance**
- Uses **Gemini 2.5 Flash** to generate a well-formatted, friendly newsletter
- Delivers the output via a simple API endpoint (`/generate-newsletter`)

---

## 🧰 Built With

- **FastAPI** – High-performance web framework
- **Google Generative AI (Gemini)** – For intelligent summarization
- **newsdata.io** – News source for health articles
- **dotenv** – For secure API key handling
- **requests** – For HTTP requests to external APIs

---

## 🔗 Endpoints

- `GET /` — Health check
- `GET /generate-newsletter` — Returns the AI-generated health newsletter
