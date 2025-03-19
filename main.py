import os
import logging
from protonmail import ProtonMail
from protonmail.models import Message
from dotenv import load_dotenv

from filters import (
    is_review_solicitation,
    is_shipping_update,
    is_linkedin_shit_emails,
    is_general_social_media,
    is_take_away,
    is_receipt,
    is_spam,
)

proton = ProtonMail()

proton_labels = []

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def restore_session():
    # check for .proton-session and load session
    if os.path.isfile(".proton-session"):
        logger.info("Restoring session from .proton-session")
        proton.load_session(".proton-session")
    else:
        load_dotenv()
        if "PROTON_USERNAME" in os.environ and "PROTON_PASSWORD" in os.environ:
            logger.info("Using environment variables for login")
            proton.login(os.environ["PROTON_USERNAME"], os.environ["PROTON_PASSWORD"])
        else:
            username = input("Enter your ProtonMail username: ")
            password = input("Enter your ProtonMail password: ")
            proton.login(username, password)

        proton.save_session(".proton-session")


def apply_label(message: Message, label: str) -> None:
    global proton_labels

    try:
        label_obj = [x for x in proton_labels if x.name == label][0]
    except IndexError:
        logger.error(f"Label {label} not found")
        return

    proton.set_label_for_messages(label_obj, [message])


def remove_label(message: Message, label: str) -> None:
    global proton_labels

    try:
        label_obj = [x for x in proton_labels if x.name == label][0]
    except IndexError:
        logger.error(f"Label {label} not found")
        return

    proton.unset_label_for_messages(label_obj, [message])


def trash_message(message: Message) -> None:
    move_message(message, "Inbox", "Trash", mark_as_read=True)


def move_message(
    message: Message, from_label: str, to_label: str, mark_as_read: bool = True
) -> None:
    if mark_as_read:
        proton.mark_messages_as_read([message])

    apply_label(message, to_label)
    remove_label(message, from_label)
    logger.info(
        f"Moved message {message.subject} from {from_label} to {to_label}, marked as read = {mark_as_read}"
    )


def apply_filters(message: Message) -> None:
    if is_spam(message):
        move_message(message, "Inbox", "Spam")
        return

    if is_review_solicitation(message):
        trash_message(message)
        return

    if is_receipt(message):
        move_message(message, "Inbox", "Kvitteringer")
        return

    if is_shipping_update(message):
        move_message(message, "Inbox", "Forsendelser", False)
        return

    if is_general_social_media(message):
        if is_linkedin_shit_emails(message):
            trash_message(message)
        else:
            move_message(
                message,
                "Inbox",
                "Sociale medier",
                mark_as_read="linkedin" not in message.sender.address,
            )
        return

    if is_take_away(message):
        move_message(message, "Inbox", "Take away")

    # Add more filters here


def handle_callback(response: dict):
    messages = response.get("Messages", [])

    if len(messages) == 0:
        return

    try:
        for message_dict in messages:
            message = proton.read_message(message_dict["ID"], mark_as_read=False)
            logger.info(f"{message.sender.address}: {message.subject}")
            apply_filters(message)

    except ConnectionError:
        logger.error("Connection error - skipping message")
        return None


def main():
    global proton_labels

    proton_labels = proton.get_all_labels()
    proton_labels.extend(proton.get_user_labels())
    logger.info(f"Loaded {len(proton_labels)} labels")

    try:
        inbox_label = [label for label in proton_labels if label.name == "Inbox"][0]
    except IndexError:
        logger.error("Inbox label not found - exiting")
        return

    logger.info("Performing inital inbox scan")
    messages = proton.get_messages(label_or_id=inbox_label)

    for message in messages:
        logger.info(f"{message.sender.address}: {message.subject}")
        try:
            message = proton.read_message(message, mark_as_read=False)
            apply_filters(message)
        except ConnectionError:
            logger.error("Connection error - skipping message")

            continue

    logger.info("Starting event polling - monitoring for new messages")
    proton.event_polling(handle_callback, interval=60)


if __name__ == "__main__":
    restore_session()

    main()
