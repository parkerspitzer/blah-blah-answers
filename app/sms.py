import logging

from flask import Blueprint, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator

from app import config, history, providers

log = logging.getLogger(__name__)

sms_bp = Blueprint("sms", __name__)

HELP_TEXT = (
    "Commands:\n"
    "CLEAR - erase conversation history\n"
    "HELP - show this message\n"
    "\nJust text any question to get an AI-powered answer."
)


def _validate_twilio_request(req):
    """Validate that the request actually came from Twilio."""
    if not config.TWILIO_AUTH_TOKEN:
        # If no auth token configured, skip validation (development mode)
        return True
    validator = RequestValidator(config.TWILIO_AUTH_TOKEN)
    url = req.url
    post_vars = req.form.to_dict()
    signature = req.headers.get("X-Twilio-Signature", "")
    return validator.validate(url, post_vars, signature)


@sms_bp.route("/sms", methods=["POST"])
def incoming_sms():
    if not _validate_twilio_request(request):
        log.warning("Invalid Twilio signature — rejecting request")
        return "Forbidden", 403

    from_number = request.form.get("From", "")
    body = request.form.get("Body", "").strip()

    log.info("SMS from %s: %s", from_number, body)

    resp = MessagingResponse()

    # Handle commands
    command = body.upper()
    if command == "HELP":
        resp.message(HELP_TEXT)
        return str(resp)

    if command == "CLEAR":
        history.clear_history(from_number)
        resp.message("Conversation history cleared.")
        return str(resp)

    # Get conversation history and query AI
    try:
        conv_history = history.get_history(from_number, config.MAX_HISTORY)
        answer = providers.query(conv_history, body)

        # SMS messages are limited to 1600 characters
        if len(answer) > 1600:
            answer = answer[:1597] + "..."

        # Store both messages in history
        history.add_message(from_number, "user", body)
        history.add_message(from_number, "assistant", answer)

        resp.message(answer)
    except Exception:
        log.exception("Error processing SMS from %s", from_number)
        resp.message("Sorry, something went wrong. Please try again.")

    return str(resp)
