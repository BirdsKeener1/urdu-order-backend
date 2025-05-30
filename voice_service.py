from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
import os
from typing import Optional, Dict, Any
from datetime import datetime

class VoiceService:
    def __init__(self):
        self.client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER")

    def generate_ivr_response(self, order_number: str) -> str:
        """Generate TwiML for IVR system"""
        response = VoiceResponse()
        
        # Welcome message in Urdu
        response.say(
            f"آپ کا آرڈر نمبر {order_number} ہے۔ براہ کرم اپنے آرڈر کی تصدیق کے لیے 1 دبائیں۔ آرڈر منسوخ کرنے کے لیے 0 دبائیں۔ سپورٹ ٹیم سے بات کرنے کے لیے 2 دبائیں۔",
            language="ur-PK"
        )

        # Gather user input
        gather = Gather(
            num_digits=1,
            timeout=10,
            action=f"/api/voice/handle-input/{order_number}",
            method="POST"
        )
        response.append(gather)

        # If no input is received, repeat the message
        response.redirect("/api/voice/welcome")

        return str(response)

    def make_call(self, to_number: str, order_number: str) -> Dict[str, Any]:
        """Initiate a call to the customer"""
        try:
            call = self.client.calls.create(
                to=to_number,
                from_=self.from_number,
                url=f"{os.getenv('BASE_URL')}/api/voice/welcome/{order_number}"
            )
            return {
                "call_sid": call.sid,
                "status": call.status,
                "timestamp": datetime.utcnow()
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.utcnow()
            }

    def handle_input(self, order_number: str, digit: str) -> str:
        """Handle IVR input from customer"""
        response = VoiceResponse()

        if digit == "1":
            # Order confirmed
            response.say(
                "آپ کے آرڈر کی تصدیق ہو گئی ہے۔ آپ کا شکریہ۔",
                language="ur-PK"
            )
            # Update order status in database
            # This will be handled by the webhook endpoint

        elif digit == "0":
            # Order cancelled
            response.say(
                "آپ کا آرڈر منسوخ کر دیا گیا ہے۔",
                language="ur-PK"
            )
            # Update order status in database
            # This will be handled by the webhook endpoint

        elif digit == "2":
            # Transfer to support
            response.say(
                "آپ کو سپورٹ ٹیم سے جوڑا جا رہا ہے۔",
                language="ur-PK"
            )
            response.dial(os.getenv("SUPPORT_PHONE_NUMBER"))

        else:
            # Invalid input
            response.say(
                "معذرت، یہ ایک غلط انپٹ ہے۔",
                language="ur-PK"
            )
            response.redirect(f"/api/voice/welcome/{order_number}")

        return str(response)

    def get_call_status(self, call_sid: str) -> Optional[Dict[str, Any]]:
        """Get the status of a call"""
        try:
            call = self.client.calls(call_sid).fetch()
            return {
                "call_sid": call.sid,
                "status": call.status,
                "duration": call.duration,
                "timestamp": datetime.utcnow()
            }
        except Exception:
            return None 