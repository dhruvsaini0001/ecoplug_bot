"""
Response Models
Standardized response format with diagnostic support.
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal


class ChatResponse(BaseModel):
    """
    Universal chatbot response model with diagnostic capabilities.
    
    ═══════════════════════════════════════════════════════════════
    RESPONSE TYPE HANDLING
    ═══════════════════════════════════════════════════════════════
    
    Type: "diagnostic" - Error code detected and diagnosed
    ────────────────────────────────────────────────────────────────
    Fields populated: text, error_code, description, solutions
    
    Example:
    {
      "type": "diagnostic",
      "text": "I found information about ER001 - Gun Temperature Limit",
      "error_code": "ER001",
      "description": "The gun temperature exceeded the 90°C threshold",
      "solutions": ["Remove the gun...", "If physical heating..."],
      "options": null,
      "steps": null,
      "session_id": "sess_abc123"
    }
    
    Type: "flow" - Rule-based conversation flow
    ────────────────────────────────────────────────────────────────
    Fields populated: text, options, steps, action
    
    Example:
    {
      "type": "flow",
      "text": "How can I help you today?",
      "options": ["Report Error", "Troubleshoot", "Contact Support"],
      "steps": null,
      "action": null,
      "session_id": "sess_abc123"
    }
    
    Type: "ai" - AI-generated fallback response
    ────────────────────────────────────────────────────────────────
    Fields populated: text
    
    Example:
    {
      "type": "ai",
      "text": "I can help you with EV charging station diagnostics...",
      "options": null,
      "session_id": "sess_abc123"
    }
    
    
    ═══════════════════════════════════════════════════════════════
    FRONTEND RENDERING GUIDE
    ═══════════════════════════════════════════════════════════════
    
    WEB (React Example):
    ────────────────────────────────────────────────────────────────
    ```jsx
    function ChatMessage({ response }) {
      return (
        <div className="chat-message">
          <p>{response.text}</p>
          
          {response.type === 'diagnostic' && (
            <DiagnosticCard
              errorCode={response.error_code}
              description={response.description}
              solutions={response.solutions}
            />
          )}
          
          {response.options && (
            <div className="options">
              {response.options.map(opt => (
                <button onClick={() => handleOption(opt)}>{opt}</button>
              ))}
            </div>
          )}
          
          {response.steps && (
            <ol>
              {response.steps.map((step, i) => <li key={i}>{step}</li>)}
            </ol>
          )}
        </div>
      );
    }
    ```
    
    ANDROID (Kotlin/Jetpack Compose):
    ────────────────────────────────────────────────────────────────
    ```kotlin
    @Composable
    fun ChatMessage(response: ChatResponse) {
        Column {
            Text(response.text)
            
            when (response.type) {
                "diagnostic" -> {
                    DiagnosticCard(
                        errorCode = response.error_code,
                        description = response.description,
                        solutions = response.solutions
                    )
                }
                "flow" -> {
                    response.options?.forEach { option ->
                        Button(onClick = { handleOption(option) }) {
                            Text(option)
                        }
                    }
                }
            }
        }
    }
    ```
    
    iOS (SwiftUI):
    ────────────────────────────────────────────────────────────────
    ```swift
    struct ChatMessageView: View {
        let response: ChatResponse
        
        var body: some View {
            VStack(alignment: .leading) {
                Text(response.text)
                
                if response.type == "diagnostic" {
                    DiagnosticCardView(
                        errorCode: response.error_code,
                        description: response.description,
                        solutions: response.solutions
                    )
                }
                
                if let options = response.options {
                    ForEach(options, id: \\.self) { option in
                        Button(option) {
                            handleOption(option)
                        }
                    }
                }
            }
        }
    }
    ```
    """
    
    type: Literal["diagnostic", "flow", "ai"] = Field(
        ...,
        description="Response type: diagnostic (error detected), flow (rule-based), ai (AI fallback)"
    )
    
    text: str = Field(
        ...,
        description="Main response text to display",
        examples=["I found information about ER001"]
    )
    
    # Diagnostic-specific fields (populated when type="diagnostic")
    error_code: Optional[str] = Field(
        None,
        description="Detected error code (e.g., 'ER001')",
        examples=["ER001"]
    )
    
    description: Optional[str] = Field(
        None,
        description="Error description",
        examples=["The gun temperature exceeded the 90°C threshold"]
    )
    
    solutions: Optional[list[str]] = Field(
        None,
        description="List of solution steps for the error"
    )
    
    # Flow-specific fields (populated when type="flow")
    options: Optional[list[str]] = Field(
        None,
        description="Clickable options/buttons for user selection"
    )
    
    steps: Optional[list[str]] = Field(
        None,
        description="Sequential steps or information items"
    )
    
    action: Optional[str] = Field(
        None,
        description="Special action identifier for client-side handling"
    )
    
    # Common fields
    session_id: str = Field(
        ...,
        description="Session identifier for conversation continuity"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "type": "diagnostic",
                    "text": "I found information about ER001 - Gun Temperature Limit",
                    "error_code": "ER001",
                    "description": "The gun temperature exceeded the 90°C threshold",
                    "solutions": [
                        "Remove the gun from the vehicle and physical heating on both ends.",
                        "If physical heating is available, please verify the gun's condition."
                    ],
                    "options": None,
                    "steps": None,
                    "action": None,
                    "session_id": "sess_abc123"
                },
                {
                    "type": "flow",
                    "text": "Welcome to EV Charging Support. How can I help?",
                    "error_code": None,
                    "description": None,
                    "solutions": None,
                    "options": ["Report Error", "Troubleshoot", "Track Service"],
                    "steps": None,
                    "action": None,
                    "session_id": "sess_abc123"
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., examples=["healthy"])
    version: str = Field(..., examples=["1.0.0"])
    timestamp: str = Field(..., examples=["2026-02-19T10:30:00Z"])
    diagnostics_loaded: bool = Field(..., examples=[True])
    error_codes_count: int = Field(..., examples=[150])
