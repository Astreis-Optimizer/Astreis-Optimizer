# =============================================================================
# IMPORTS AND DEPENDENCIES
# =============================================================================
from groq import Groq
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtSvgWidgets import *
from gui.widgets import *

# =============================================================================
# ASTREIS FUNCTIONALITY CLASS
# =============================================================================
class AstreisFunc:
    # =============================================================================
    # AI CHAT FUNCTIONALITY
    # =============================================================================
    @staticmethod
    def send_message(input_field, scroll_layout, themes):
        client = Groq()
        user_input = input_field.text()
        if not user_input.strip():
            return

        # Add user message to chat
        user_message = QLabel(f"You: {user_input}")
        user_message.setStyleSheet(
            f"font: 10pt 'Segoe UI'; color: {themes['app_color']['text_description']}; "
            "background-color: #343B48; border-radius: 10px; padding: 10px; margin: 5px;"
        )
        user_message.setWordWrap(True)
        scroll_layout.addWidget(user_message)

        # Send request to Groq API
        try:
            completion = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {
                        "role": "user",
                        "content": user_input
                    }
                ],
                temperature=1,
                max_completion_tokens=1024,
                top_p=1,
                stream=True,
                stop=None,
            )

            # Add AI response label
            ai_response = QLabel("AI: ")
            ai_response.setStyleSheet(
                f"font: 10pt 'Segoe UI'; color: {themes['app_color']['text_description']}; "
                "background-color: #2A2F3B; border-radius: 10px; padding: 10px; margin: 5px;"
            )
            ai_response.setWordWrap(True)
            scroll_layout.addWidget(ai_response)

            # Stream response
            full_response = ""
            for chunk in completion:
                content = chunk.choices[0].delta.content or ""
                full_response += content
                ai_response.setText(f"AI: {full_response}")
                QApplication.processEvents()  # Update UI during streaming

        except Exception as e:
            error_message = QLabel(f"Error: {str(e)}")
            error_message.setStyleSheet(
                f"font: 10pt 'Segoe UI'; color: {themes['app_color']['context_color']}; "
                "background-color: #2A2F3B; border-radius: 10px; padding: 10px; margin: 5px;"
            )
            error_message.setWordWrap(True)
            scroll_layout.addWidget(error_message)

        input_field.clear()
        scroll_layout.addStretch()  # Keep messages aligned at top
