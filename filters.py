import json

from bs4 import BeautifulSoup
from ollama_python.endpoints import GenerateAPI
from ollama_python.models.generate import Completion
from protonmail.models import Message


ollama = GenerateAPI(base_url="http://localhost:11434/api", model="gemma3:12b")


def html_to_plaintext(html_string: str) -> str:
    # Parse the HTML
    soup = BeautifulSoup(html_string, "html.parser")

    # Get the text content, optionally adding a separator between elements
    text = soup.get_text(separator=" ")

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def is_review_solicitation(message: Message) -> bool:
    prompt = """You are a text classifier that determines if an email is explicitly asking the recipient to leave a review on Trustpilot.
Specifically, you must decide whether the email invites, requests, or directs the reader to post a review on Trustpilot.

Please follow these steps:

1. Read the email text carefully.
2. Decide if there is an explicit or implicit call to action for the user to review the sender on Trustpilot.
   - Examples of calls to action include phrases like “bedøm os,” “giv os en anmeldelse,” “leave a review,”
     “share your feedback,” “please rate us on https://dk.trustpilot.com/evaluate/…,” etc.
   - Merely mentioning Trustpilot, including a link, or referencing Trustpilot as part of a receipt/invoice
     (for example, “we are listed on Trustpilot” or “read about us on Trustpilot”) without an explicit invitation
     to leave a review does not count as soliciting a review.
3. Return only a single JSON object with the key "is_soliciting_trustpilot_reviews" and a boolean value:
   - true if the email is requesting or encouraging a Trustpilot review.
   - false if it only mentions Trustpilot in passing or never mentions Trustpilot at all.

Your output must follow this exact JSON format (with no extra text outside the JSON):

```json
{
  "is_soliciting_trustpilot_reviews": true/false
}
```"""

    response = apply_prompt(message, prompt)

    info = json.loads(response.response)

    return info["is_soliciting_trustpilot_reviews"]


def is_shipping_update(message: Message) -> bool:
    prompt = """You are a text classifier that determines if an email is a shipping update.
Specifically, you must decide whether the email contains information about the status of a package delivery. 
Please follow these steps:
1. Read the email text carefully.
2. Decide if the email contains information about the status of a package delivery."
Examples of shipping updates include phrases like “your order has shipped,” “your package is on the way,” “your package is out for delivery,” etc." 
3. Return only a single JSON object with the key "is_shipping_update" and a boolean value:" 
    true if the email contains a shipping update.
    false if the email does not contain a shipping update.
    Your output must follow this exact JSON format (with no extra text outside the JSON):
    ```json"
    { 
    "is_shipping_update": true/false
    } \
    ```"""

    response = apply_prompt(message, prompt)

    info = json.loads(response.response)

    return info["is_shipping_update"]



def apply_prompt(message: Message, prompt: str) -> Completion:
    plain_text = f"{message.subject}\n\n {html_to_plaintext(message.body)}"

    response = ollama.generate(
        f"{prompt}\ne-mail:\n{plain_text}", format="json", options={"num_ctx": 8192}
    )

    return response

def is_linkedin_shit_emails(message: Message) -> bool:

    prompt = """You are an AI assistant that classifies LinkedIn-related emails. Your task is to determine whether an email is **directly relevant** to the user.

### **Criteria for Relevance (`true`):**  
An email is relevant if it:
1. **Mentions the user’s name explicitly** in a way that indicates direct interaction (e.g., “John, your post got a comment,” “John, someone mentioned you”).
2. **Contains a comment on a post made by the user**.
3. **Is a direct message sent to the user**.

If none of these conditions are met, classify the email as **`false`**.

Strong indicators of false could also be:

1. **Call to follow somebody**
2. **General call to action on linkedins site**

### **Input format:**  
A plain text email. The content may include a subject line, body text, and metadata.

### **Output:**  
Return a valid JSON object with a single key `"relevant"`, where the value is either `true` or `false`.


**Input:**
"""
    if "@linkedin.com" not in message.sender.address:
        return False

    response = apply_prompt(message, prompt)

    info = json.loads(response.response)

    return not info["relevant"]


def is_general_social_media(message: Message):

    if "facebook" in message.sender.address:
        return True
    if "instagram" in message.sender.address:
        return True
    if "twitter" in message.sender.address:
        return True
    if "snapchat" in message.sender.address:
        return True
    if "pinterest" in message.sender.address:
        return True
    if "tiktok" in message.sender.address:
        return True
    if "youtube" in message.sender.address:
        return True
    if "reddit" in message.sender.address:
        return True
    if "discord" in message.sender.address:
        return True
    if "whatsapp" in message.sender.address:
        return True
    if "telegram" in message.sender.address:
        return True
    if "signal" in message.sender.address:
        return True
    if "linkedin" in message.sender.address:
        return True
    if "twitch" in message.sender.address:
        return True
    if "clubhouse" in message.sender.address:
        return True
    if "medium" in message.sender.address:  
        return True
    if "substack" in message.sender.address:
        return True

    return False
    
def is_take_away(message: Message) -> bool:
    prompt = """You are a text classifier that determines if an email is explicitly related to a purchase of takeaway food.
Specifically, you must decide whether the email confirms, references, or provides details about a takeaway food order.

Please follow these steps:

1. Read the email text carefully.
2. Decide if the email explicitly indicates that the recipient has purchased takeaway food.
   - Examples of relevant indicators include phrases like “your order is confirmed,” “thank you for your order,” “your food is on the way,” “pickup is ready,” or references to specific food items, order numbers, or delivery details.
   - Emails that only mention food in a general sense (e.g., promotions, newsletters, or restaurant advertisements without a purchase confirmation) should not be classified as takeaway purchase emails.
3. Return only a single JSON object with the key "is_takeaway_purchase" and a boolean value:
   - true if the email confirms, references, or provides details about a takeaway food order.
   - false if the email only mentions food in a general sense or does not relate to a purchase at all.

Your output must follow this exact JSON format (with no extra text outside the JSON):

```json
{
  "is_takeaway_purchase": true/false
}
```"""

    response = apply_prompt(message, prompt)

    info = json.loads(response.response)

    return info["is_takeaway_purchase"]

def is_receipt(message: Message) -> bool:
    prompt = """You are a text classifier that determines if an email contains a receipt for a purchase.
Specifically, you must decide whether the email confirms a transaction, provides an invoice, or includes proof of payment.

Please follow these steps:

1. Read the email text carefully.
2. Decide if the email explicitly indicates that it contains a receipt or proof of purchase.
   - Examples of relevant indicators include phrases like:
     - **English:** “your receipt,” “invoice attached,” “payment confirmation,” “order summary,” “transaction details.”
     - **German:** “Ihre Rechnung,” “Zahlungsbestätigung,” “Quittung,” “Bestellübersicht,” “Transaktionsdetails.”
     - **Danish:** “din kvittering,” “faktura vedhæftet,” “betalingsbekræftelse,” “ordrebekræftelse,” “transaktionsdetaljer.”
   - Emails that merely mention purchases in a general sense (e.g., advertisements, promotions, or newsletters) without providing proof of payment should not be classified as receipts.
3. Return only a single JSON object with the key "is_receipt" and a boolean value:
   - `true` if the email contains a receipt, invoice, or payment confirmation.
   - `false` if the email does not provide explicit proof of purchase.

Your output must follow this exact JSON format (with no extra text outside the JSON):

```json
{
  "is_receipt": true/false
}
```"""
    if len([x for x in message.attachments if 'application/pdf' in x.type]) == 0:
        return False


    response = apply_prompt(message, prompt)

    info = json.loads(response.response)

    return info["is_receipt"]


def is_spam(message: Message) -> bool:
    prompt = """You are a text classifier that determines if an email is spam.
Specifically, you must decide whether the email is unsolicited, promotional, deceptive, or irrelevant to the recipient.

Please follow these steps:

1. Read the email text carefully.
2. Decide if the email exhibits common characteristics of spam, such as:
   - Unsolicited marketing, promotional offers, or phishing attempts.
   - Requests for donations, particularly for **American political campaigns**, such as appeals to support a senator or politician.
   - Generic greetings like "Dear friend" or "Congratulations, you have won!"
   - Urgency tactics such as “Act now,” “Limited time offer,” or “Final notice.”
   - Suspicious links, attachments, or financial requests.
   - Poor grammar, excessive capitalization, or misleading subject lines.
3. Return only a single JSON object with the key "is_spam" and a boolean value:
   - `true` if the email is unsolicited spam, political solicitation, or deceptive.
   - `false` if the email appears legitimate and not spam.

Your output must follow this exact JSON format (with no extra text outside the JSON):

```json
{
  "is_spam": true/false
}
```"""

    response = apply_prompt(message, prompt)

    info = json.loads(response.response)

    return info["is_spam"]
