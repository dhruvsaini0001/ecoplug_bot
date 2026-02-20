#!/usr/bin/env python3
# Add the _get_flow_context method to conversation_manager.py

method_code = '''
    
    def _get_flow_context(self, current_node: str) -> str:
        """
        Determine conversation context based on current flow node.
        
        This method categorizes nodes to enable context-aware detection:
        - "error_code": User is in error reporting flow
        - "payment": User is in payment/wallet flow
        - "normal": General conversation
        
        Args:
            current_node: Current flow node ID from session
            
        Returns:
            Context type: "error_code", "payment", or "normal"
        """
        # Error code detection context
        error_code_nodes = [
            "error_reporting",
            "other_error_code",
            "troubleshooting"
        ]
        
        # Payment/wallet context
        payment_nodes = [
            "wallet_issues",
            "balance_not_updating",
            "payment_failed",
            "refund_issues",
            "transaction_history",
            "payment_info"
        ]
        
        if current_node in error_code_nodes:
            return "error_code"
        elif current_node in payment_nodes:
            return "payment"
        else:
            return "normal"
'''

with open('chatbot/engine/conversation_manager.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Check if method already exists
if 'def _get_flow_context' not in content:
    # Find the last occurrence of 'return False' and add method after it
    if 'return False\n\n```' in content:
        content = content.replace('return False\n\n```', 'return False' + method_code)
    elif 'return False' in content:
        # Find the last return False and add after it
        idx = content.rfind('return False')
        if idx != -1:
            # Add the method after the last return False
            content = content[:idx+len('return False')] + method_code + content[idx+len('return False'):]
    
    # Clean up any markdown fences
    content = content.replace('\n```\n````', '')
    content = content.rstrip() + '\n'
    
    with open('chatbot/engine/conversation_manager.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Added _get_flow_context method")
else:
    print("✓ _get_flow_context method already exists")
