# 🔌 EV Charging Diagnostic Chatbot Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Industry-grade headless AI + Rule hybrid chatbot backend for EV charging station diagnostics.**

## 🎯 Overview

A production-ready, scalable chatbot platform designed for **EV charging station technical support** with intelligent error code detection, multi-platform support, and hybrid AI + rule-based architecture.

### Key Features

- ⚡ **Intelligent Error Detection**: Detects 150+ error codes using regex + fuzzy matching
- 🤖 **AI + Rule Hybrid**: Combines deterministic rules with AI fallback
- 📱 **Multi-Platform**: Single API for Web, Android, and iOS
- 💾 **MongoDB Sessions**: Persistent conversation management
- 🚀 **Async-First**: Built on FastAPI for maximum performance
- 🔍 **Diagnostic Database**: Comprehensive error code knowledge base
- 🎨 **Headless Architecture**: Platform-independent REST API

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT PLATFORMS                      │
│         Web App    │    Android App    │    iOS App     │
└────────────────────┬────────────────────┬───────────────┘
                     │                    │
                     ▼                    ▼
            ┌────────────────────────────────────┐
            │      REST API (FastAPI)             │
            │      POST /v1/chat                  │
            └────────────┬───────────────────────┘
                         │
                         ▼
            ┌────────────────────────────────────┐
            │   CONVERSATION MANAGER              │
            │   (Priority Routing Logic)          │
            └────────┬───────────────────────────┘
                     │
        ┌────────────┼────────────┬───────────┐
        ▼            ▼            ▼           ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
   │Diagnostic│ │  Flow   │ │ Intent  │ │   AI    │
   │ Engine  │ │ Engine  │ │ Engine  │ │ Service │
   └─────────┘ └─────────┘ └─────────┘ └─────────┘
        │            │            │           │
        ▼            ▼            ▼           ▼
   Error Codes   Flows JSON   Keywords    OpenAI API
   Database                                (Optional)
```

### Priority Logic Flow

```
User Message → STEP 1: Error Code Detection? → YES → Diagnostic Response
                     ↓ NO
                STEP 2: Explicit Action? → YES → Flow Response
                     ↓ NO
                STEP 3: Intent Detected? → YES → Flow Response
                     ↓ NO
                STEP 4: AI Fallback → AI Response
```

---

## 📂 Project Structure

```
ecoplug_bot/
│
├── chatbot/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   └── routes_v1.py         # v1 API routes
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Environment configuration
│   │   └── logger.py            # Structured logging
│   │
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── diagnostic_engine.py # ★ Error code detection
│   │   ├── flow_engine.py       # Rule-based flows
│   │   ├── intent_engine.py     # Intent detection
│   │   └── conversation_manager.py # Main orchestrator
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py        # OpenAI integration
│   │   └── session_service.py   # MongoDB sessions
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request_models.py    # Pydantic request schemas
│   │   └── response_models.py   # Pydantic response schemas
│   │
│   ├── flows/
│   │   └── chatbot_flows.json   # Conversation flows
│   │
│   └── utils/
│       ├── __init__.py
│       └── text_utils.py        # Text processing utilities
│
├── error_codes_complete.json    # Diagnostic database (150+ codes)
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
└── README.md                    # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- MongoDB (local or cloud)
- (Optional) OpenAI API key

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd ecoplug_bot
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your MongoDB URL and other settings
```

5. **Run the application**
```bash
python -m chatbot.api.main
```

The API will be available at `http://localhost:8000`

### Verify Installation

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/v1/health

---

## 📱 Platform Integration

### Web Integration (JavaScript/React)

```javascript
async function sendMessage(message) {
  const response = await fetch('http://localhost:8000/v1/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: 'web_user_123',
      message: message,
      platform: 'web'
    })
  });
  
  const data = await response.json();
  
  // Handle different response types
  if (data.type === 'diagnostic') {
    displayErrorDiagnostic(data.error_code, data.solutions);
  } else if (data.type === 'flow') {
    displayOptions(data.options);
  } else {
    displayMessage(data.text);
  }
}
```

### Android Integration (Kotlin)

```kotlin
data class ChatRequest(
    val user_id: String,
    val message: String?,
    val platform: String = "android"
)

interface ChatApi {
    @POST("/v1/chat")
    suspend fun sendMessage(@Body request: ChatRequest): ChatResponse
}

// Usage
val response = chatApi.sendMessage(
    ChatRequest(
        user_id = getDeviceId(),
        message = "ER001 error showing"
    )
)
```

### iOS Integration (Swift)

```swift
struct ChatRequest: Codable {
    let user_id: String
    let message: String?
    let platform: String = "ios"
}

func sendMessage(_ text: String) async throws -> ChatResponse {
    let request = ChatRequest(user_id: getUserId(), message: text)
    // ... URLSession implementation
}
```

---

## 🔍 Error Code Detection

The diagnostic engine supports multiple error code formats:

- **Standard**: `ER001`, `ER015`
- **Lowercase**: `er001`
- **With prefix**: `error 15`, `ERROR 001`
- **Numeric**: `301`, `404` (with context)
- **Fuzzy matching**: "gun temperature high" → ER001

### Example Requests

```json
// Pattern 1: Direct error code
{
  "user_id": "user123",
  "message": "I'm getting ER001",
  "platform": "web"
}

// Pattern 2: Natural language
{
  "user_id": "user123",
  "message": "gun temperature is too high",
  "platform": "android"
}

// Pattern 3: Numeric code
{
  "user_id": "user123",
  "message": "showing error 301",
  "platform": "ios"
}
```

### Response Structure

```json
{
  "type": "diagnostic",
  "text": "I found information about ER001 - Gun Temperature Limit",
  "error_code": "ER001",
  "description": "The gun temperature exceeded the 90°C threshold",
  "solutions": [
    "Remove the gun from the vehicle...",
    "Check physical heating..."
  ],
  "session_id": "sess_abc123"
}
```

---

## 🤖 AI Integration

### OpenAI Setup (Optional)

1. **Install OpenAI SDK**
```bash
pip install openai
```

2. **Add API key to .env**
```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4
```

3. **Uncomment OpenAI code**

In `chatbot/services/ai_service.py`, uncomment the OpenAI client initialization and implementation code (clearly marked in comments).

The system will automatically use OpenAI for ambiguous queries when configured.

---

## 📊 API Endpoints

### POST /v1/chat

Main chat endpoint for all platforms.

**Request:**
```json
{
  "user_id": "string",
  "message": "optional string",
  "action": "optional string",
  "platform": "web | android | ios"
}
```

**Response:**
```json
{
  "type": "diagnostic | flow | ai",
  "text": "string",
  "error_code": "optional",
  "description": "optional",
  "solutions": ["optional"],
  "options": ["optional"],
  "steps": ["optional"],
  "action": "optional",
  "session_id": "string"
}
```

### GET /v1/health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-02-19T10:30:00Z",
  "diagnostics_loaded": true,
  "error_codes_count": 150
}
```

---

## 🧪 Testing

### Manual Testing

```bash
# Test health endpoint
curl http://localhost:8000/v1/health

# Test error detection
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "I have ER001 error",
    "platform": "web"
  }'
```

### Interactive API Docs

Visit `http://localhost:8000/docs` for interactive Swagger UI.

---

## 📈 Performance Optimization

- **Startup Loading**: All JSON files loaded once at startup
- **In-Memory Cache**: Error codes indexed for O(1) lookup
- **Async I/O**: Non-blocking database and API calls
- **Connection Pooling**: MongoDB connection pool configured
- **Session Cleanup**: Automatic TTL-based session expiry

---

## 🔐 Security Considerations

- [ ] Add API key authentication
- [ ] Implement rate limiting (middleware ready)
- [ ] Input sanitization (basic validation included)
- [ ] HTTPS in production
- [ ] Environment variable protection
- [ ] MongoDB authentication
- [ ] CORS configuration per environment

---

## 🚢 Deployment

### Docker Deployment (Recommended)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "chatbot.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

Set these in production:

- `MONGODB_URL`: Your MongoDB connection string
- `OPENAI_API_KEY`: OpenAI API key (if using AI)
- `LOG_LEVEL`: `INFO` or `WARNING` in production
- `DEBUG`: `False`
- `CORS_ORIGINS`: Specific allowed origins

---

## 📚 Knowledge Base Management

### Adding New Error Codes

Edit `error_codes_complete.json`:

```json
{
  "Error_Code": "ER999",
  "Tittle": "New Error Title",
  "Description": "Error description here",
  "Solution": [
    "Solution step 1",
    "Solution step 2"
  ]
}
```

Restart the application to reload.

### Updating Conversation Flows

Edit `chatbot/flows/chatbot_flows.json`:

```json
{
  "flows": {
    "new_node": {
      "text": "Node text here",
      "options": ["Option 1", "Option 2"],
      "steps": null,
      "action": null
    }
  }
}
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 License

MIT License - see LICENSE file for details

---

## 💡 Support

- **Documentation**: `/docs` endpoint
- **Issues**: GitHub Issues
- **Email**: support@evcharging.com

---

## 🗺️ Roadmap

- [ ] Add multilingual support
- [ ] Implement analytics dashboard
- [ ] Add webhook notifications
- [ ] Support image/video attachments
- [ ] Voice input integration
- [ ] Real-time WebSocket support
- [ ] Advanced ML-based intent classification

---

**Built with ❤️ for the EV charging community**
