"""
Request Models
Pydantic models for API request validation.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal


class ChatRequest(BaseModel):
    """
    Universal chat request model for all platforms.
    
    ═══════════════════════════════════════════════════════════════
    INTEGRATION GUIDE FOR PLATFORMS
    ═══════════════════════════════════════════════════════════════
    
    WEB INTEGRATION (JavaScript/React/Vue/Angular):
    ────────────────────────────────────────────────────────────────
    ```javascript
    // Example: User reports error
    async function sendMessage(message) {
      const response = await fetch('https://api.yourserver.com/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: getUserId(), // e.g., "web_user_12345"
          message: message,     // e.g., "I'm getting ER001 error"
          platform: 'web'
        })
      });
      
      const data = await response.json();
      
      // Handle diagnostic response
      if (data.type === 'diagnostic') {
        displayErrorCode(data.error_code);
        displayDescription(data.description);
        displaySolutions(data.solutions);
      }
      
      return data;
    }
    ```
    
    ANDROID INTEGRATION (Kotlin + Retrofit):
    ────────────────────────────────────────────────────────────────
    ```kotlin
    // Define request model
    data class ChatRequest(
        val user_id: String,
        val message: String?,
        val action: String?,
        val platform: String = "android"
    )
    
    // Retrofit interface
    interface ChatApi {
        @POST("/v1/chat")
        suspend fun sendMessage(@Body request: ChatRequest): ChatResponse
    }
    
    // Usage
    val request = ChatRequest(
        user_id = getDeviceId(),
        message = "error 301 showing",
        platform = "android"
    )
    
    val response = chatApi.sendMessage(request)
    
    when (response.type) {
        "diagnostic" -> showDiagnosticView(response)
        "flow" -> showOptionsView(response)
        "ai" -> showTextResponse(response)
    }
    ```
    
    iOS INTEGRATION (Swift + URLSession/Alamofire):
    ────────────────────────────────────────────────────────────────
    ```swift
    struct ChatRequest: Codable {
        let user_id: String
        let message: String?
        let action: String?
        let platform: String
    }
    
    func sendMessage(_ text: String) async throws -> ChatResponse {
        let request = ChatRequest(
            user_id: getUserId(),
            message: text,
            action: nil,
            platform: "ios"
        )
        
        let url = URL(string: "https://api.yourserver.com/v1/chat")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = try JSONEncoder().encode(request)
        
        let (data, _) = try await URLSession.shared.data(for: urlRequest)
        let response = try JSONDecoder().decode(ChatResponse.self, from: data)
        
        return response
    }
    ```
    """
    
    user_id: str = Field(
        ...,
        description="Unique user/device identifier from client platform",
        min_length=1,
        max_length=255,
        examples=["web_user_12345", "android_uuid_xyz", "ios_device_abc"]
    )
    
    message: Optional[str] = Field(
        None,
        description="User's text message (e.g., 'I have ER001 error')",
        max_length=2000
    )
    
    action: Optional[str] = Field(
        None,
        description="Specific action trigger (e.g., 'start', 'troubleshoot', 'contact_support')",
        max_length=100
    )
    
    platform: Literal["web", "android", "ios"] = Field(
        ...,
        description="Client platform identifier"
    )
    
    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        """Ensure user_id is not empty after stripping."""
        if not v.strip():
            raise ValueError("user_id cannot be empty")
        return v.strip()
    
    @field_validator("message")
    @classmethod
    def validate_message(cls, v: Optional[str]) -> Optional[str]:
        """Strip and validate message."""
        if v is not None:
            v = v.strip()
            return v if v else None
        return v
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "web_user_12345",
                    "message": "I'm getting ER001 error on my charging station",
                    "platform": "web"
                },
                {
                    "user_id": "android_user_67890",
                    "message": "gun temperature high",
                    "platform": "android"
                },
                {
                    "user_id": "ios_user_abc",
                    "action": "start",
                    "platform": "ios"
                }
            ]
        }
    }
