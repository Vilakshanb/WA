from flask import Flask, request, jsonify
from flask_mail import Mail, Message
import logging
import requests
from datetime import date, datetime
from config import (
    INVESTWELL_API_URL,
    INVESTWELL_AUTH_NAME,
    INVESTWELL_AUTH_PASSWORD,
    WATI_API_URL,
    WATI_BEARER_TOKEN,
    WATI_API_ENDPOINT,
    PAN,
)
import json
from iwell import (
    create_portfolio_summary_message,
    format_portfolio_report,
    send_portfolio_report_and_message,
    get_portfolio_returns,
    send_capital_gain_summary,
)


app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Flask-Mail with your email server details
app.config["MAIL_SERVER"] = "smtp.example.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USERNAME"] = "your_email@example.com"
app.config["MAIL_PASSWORD"] = "your_password"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False

mail = Mail(app)


def send_message_via_wati(waid, message):
    # Check if portfolio_data is not empty
    if message:
        # Define the URL for sending the message
        # waid = "919910076952"
        url = f"https://live-server-7354.wati.io/api/v1/sendSessionMessage/{waid}?messageText={message}"

        # Set the authorization header
        headers = {"Authorization": WATI_BEARER_TOKEN}

        # Send the POST request
        try:
            response = requests.post(url, headers=headers)
            if response.status_code == 200:
                print("Message sent successfully.")
            else:
                print(f"Failed to send message. Status code: {response.status_code}")
                print(
                    "Response content:", response.content
                )  # Print API response for debugging
        except Exception as e:
            print(f"Error sending message: {str(e)}")
    else:
        print("No portfolio data available.")


def get_rm_code(waid):
    rmCode = "vb"
    return rmCode


# app route defination to keep hearing for requests from wati
@app.route("/webhook", methods=["POST"])
def wati_webhook():
    try:
        data = request.json
        waid = data.get("waId")
        print(f"Received waid: {waid}")
        text = data.get("text")
        print(f"Received text: {text}")
        listReply = data.get("listReply")
        if listReply:
            listReplyTitle = listReply.get("title")
        else:
            listReplyTitle = None

        # Print the received text
        print(f"Received text: {text}")

        # Use the received text if it's not available
        if text is None and listReplyTitle:
            text = listReplyTitle

        logger.info(f"Extracted waid: {waid}, text: {text}")
        logger.info(f"Received payload: {data}")

        # Check for specific messages and respond accordingly
        if text and text.lower() == "hello":
            send_welcome_message(waid)
        elif text and text.lower() == "portfolio overview":
            send_portfolio_overview_menu(waid)
        elif text and text.lower() == "view holdings":
            send_View_holding(waid)
        elif text and text.lower() == "portfolio summary report":
            send_portfolio_report_and_message(waid)
        elif text and text.lower() == "capital gain (prev fy)":
            year = datetime.now().year - 1
            send_capital_gain_summary(waid, year)
        elif text and text.lower() == "capital gain (curr fy)":
            year = datetime.now().year
            send_capital_gain_summary(waid, year)
        elif text and text.lower() == "investment options":
            send_investment_options_menu(waid)
        elif text and text.lower() == "equity funds":
            send_top5_equity(waid)
        elif text and text.lower() == "large cap":
            send_top5_large(waid)
        elif text and text.lower() == "mid cap":
            send_top5_mid(waid)
        elif text and text.lower() == "small cap":
            send_top5_small(waid)
        elif text and text.lower() == "large and mid cap":
            send_top5_large_mid(waid)
        elif text and text.lower() == "multi cap":
            send_top5_mutli(waid)
        elif text and text.lower() == "flexi cap":
            send_top5_flexi(waid)
        elif text and text.lower() == "sectoral":
            send_top5_sectoral(waid)
        elif text and text.lower() == "debt funds":
            send_top5_debt(waid)
        elif text and text.lower() == "liquid funds":
            send_top5_liquid(waid)
        elif text and text.lower() == "overnight funds":
            send_top5_overnight(waid)
        elif text and text.lower() == "banking and psu Funds":
            send_top5_banking_psu(waid)
        elif text and text.lower() == "corporate bond funds":
            send_top5_corporate(waid)
        elif text and text.lower() == "credit risk funds":
            send_top5_credit_risk(waid)
        elif text and text.lower() == "hybrid funds":
            send_top5_hybrid(waid)
        elif text and text.lower() == "balanced advantage funds":
            send_top5_balanced(waid)
        elif text and text.lower() == "multi asset funds":
            send_top5_multi_asset(waid)
        elif text and text.lower() == "fixed deposit":
            send_top5_fixed_deposit(waid)
        elif text and text.lower() == "transaction history":
            send_transaction_history_menu(waid)
        elif text and text.lower() == "faqs":
            send_faqs_menu(waid)
        elif text and text.lower() == "how to invest?":
            how_to_invest(waid)
        elif text and text.lower() == "how to withdraw?":
            how_to_withdraw(waid)
        elif text and text.lower() == "check portfolio":
            check_portfolio(waid)
        elif text and text.lower() == "contact support":
            contact_support(waid)
        elif text and text.lower() == "taxation on mutual funds":
            taxation(waid)
        elif text and text.lower() == "speak to advisor":
            speak_rm(waid)
        elif text and text.lower() == "settings":
            send_settings_menu(waid)
        else:
            # Send a welcome message for unrecognized messages
            send_welcome_message(waid)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


# working for sending welcome message
def send_welcome_message(waid):
    try:
        headers = {
            "Authorization": WATI_BEARER_TOKEN,
            "Content-Type": "application/json",
        }

        endpoint_url = f"{WATI_API_ENDPOINT}?whatsappNumber={waid}"

        payload = {
            "body": "Welcome to mNivesh Team's Whatsapp Chatbot! We are here to help you with your investments and any queries regarding it.\n\nPlease select one of the options below to proceed.",
            "buttonText": "Menu",
            "footer": "mNivesh Team",
            "sections": [
                {
                    "title": "Menu",
                    "rows": [
                        {
                            "title": "Portfolio Overview",
                        },
                        {
                            "title": "Investment Options",
                        },
                        {
                            "title": "FAQs",
                        },
                        {
                            "title": "Speak to your RM",
                        },
                        {
                            "title": "Settings",
                        },
                    ],
                }
            ],
        }

        response = requests.post(endpoint_url, headers=headers, json=payload)

        if response.status_code != 200:
            logger.error(
                f"Failed to send welcome message. Status Code: {response.status_code}, Response: {response.text}"
            )
        else:
            logger.info(
                f"Successfully sent welcome message. Status Code: {response.status_code}, Response: {response.text}"
            )

    except Exception as e:
        logger.error(f"An error occurred while sending the welcome message: {str(e)}")


# send_portfolio_overview_menu
def send_portfolio_overview_menu(waid):
    try:
        headers = {
            "Authorization": WATI_BEARER_TOKEN,
            "Content-Type": "application/json",
        }

        endpoint_url = f"{WATI_API_ENDPOINT}?whatsappNumber={waid}"
        portfolio_summary_message = create_portfolio_summary_message()
        payload = {
            "body": f"{portfolio_summary_message}\n\nPlease select an option below.",
            "buttonText": "Menu",
            "footer": "mNivesh Team",
            "sections": [
                {
                    "title": "Portfolio Overview",
                    "rows": [
                        {
                            "title": "View Holdings",
                        },
                        {
                            "title": "Portfolio Summary Report",
                        },
                        {
                            "title": "Capital Gain (Prev FY)",
                        },
                        {
                            "title": "Capital Gain (Curr FY)",
                        },
                    ],
                }
            ],
        }

        # Print a debug message
        print("Sending Portfolio Overview Menu")

        response = requests.post(endpoint_url, headers=headers, json=payload)

        if response.status_code != 200:
            logger.error(
                f"Failed to send Portfolio Overview Menu. Status Code: {response.status_code}, Response: {response.text}"
            )
        else:
            logger.info(
                f"Successfully sent Portfolio Overview Menu. Status Code: {response.status_code}, Response: {response.text}"
            )

    except Exception as e:
        logger.error(
            f"An error occurred while sending the Portfolio Overview Menu: {str(e)}"
        )


def send_investment_options_menu(waid):
    try:
        headers = {
            "Authorization": WATI_BEARER_TOKEN,
            "Content-Type": "application/json",
        }

        endpoint_url = f"{WATI_API_ENDPOINT}?whatsappNumber={waid}"

        payload = {
            "body": "Investment Options Menu:\n\nPlease select an option below.",
            "buttonText": "Menu",
            "footer": "mNivesh Team",
            "sections": [
                {
                    "title": "Investment Options",
                    "rows": [
                        {
                            "title": "Equity Funds",
                        },
                        {
                            "title": "Debt Funds",
                        },
                        {
                            "title": "Hybrid Funds",
                        },
                        {
                            "title": "Fixed Deposits",
                        },
                    ],
                }
            ],
        }

        response = requests.post(endpoint_url, headers=headers, json=payload)

        if response.status_code != 200:
            logger.error(
                f"Failed to send Investment Options Menu. Status Code: {response.status_code}, Response: {response.text}"
            )
        else:
            logger.info(
                f"Successfully sent Investment Options Menu. Status Code: {response.status_code}, Response: {response.text}"
            )

    except Exception as e:
        logger.error(
            f"An error occurred while sending the Investment Options Menu: {str(e)}"
        )


def send_transaction_history_menu(waid):
    try:
        headers = {
            "Authorization": WATI_BEARER_TOKEN,
            "Content-Type": "application/json",
        }

        endpoint_url = f"{WATI_API_ENDPOINT}?whatsappNumber={waid}"

        payload = {
            "body": "Transaction History Menu:\n\nPlease select an option below to view your transaction history.",
            "buttonText": "Menu",
            "footer": "mNivesh Team",
            "sections": [
                {
                    "title": "Transaction History",
                    "rows": [
                        {
                            "title": "Recent Transactions",
                        },
                        {
                            "title": "Transaction Details",
                        },
                        {
                            "title": "Statement of Account",
                        },
                    ],
                }
            ],
        }

        response = requests.post(endpoint_url, headers=headers, json=payload)

        if response.status_code != 200:
            logger.error(
                f"Failed to send Transaction History Menu. Status Code: {response.status_code}, Response: {response.text}"
            )
        else:
            logger.info(
                f"Successfully sent Transaction History Menu. Status Code: {response.status_code}, Response: {response.text}"
            )

    except Exception as e:
        logger.error(
            f"An error occurred while sending the Transaction History Menu: {str(e)}"
        )


def send_faqs_menu(waid):
    try:
        headers = {
            "Authorization": WATI_BEARER_TOKEN,
            "Content-Type": "application/json",
        }

        endpoint_url = f"{WATI_API_ENDPOINT}?whatsappNumber={waid}"

        payload = {
            "body": "FAQs Menu:\n\nPlease select a question below to view the answer.",
            "buttonText": "Menu",
            "footer": "mNivesh Team",
            "sections": [
                {
                    "title": "Frequently Asked Ques.",
                    "rows": [
                        {
                            "title": "How to Invest?",
                        },
                        {
                            "title": "how to withdraw?",
                        },
                        {
                            "title": "Check Portfolio",
                        },
                        {
                            "title": "Taxation on Mutual Funds",
                        },
                        {
                            "title": "Contact Support",
                        },
                    ],
                }
            ],
        }

        response = requests.post(endpoint_url, headers=headers, json=payload)

        if response.status_code != 200:
            logger.error(
                f"Failed to send FAQs Menu. Status Code: {response.status_code}, Response: {response.text}"
            )
        else:
            logger.info(
                f"Successfully sent FAQs Menu. Status Code: {response.status_code}, Response: {response.text}"
            )

    except Exception as e:
        logger.error(f"An error occurred while sending the FAQs Menu: {str(e)}")


def send_speak_to_advisor_menu(waid):
    try:
        headers = {
            "Authorization": WATI_BEARER_TOKEN,
            "Content-Type": "application/json",
        }

        endpoint_url = f"{WATI_API_ENDPOINT}?whatsappNumber={waid}"

        payload = {
            "body": "Speak to Advisor Menu:\n\nPlease select an option below to speak with our advisor.",
            "buttonText": "Menu",
            "footer": "mNivesh Team",
            "sections": [
                {
                    "title": "Speak to Advisor",
                    "rows": [
                        {
                            "title": "General Questions",
                        },
                        {
                            "title": "Investment Advice",
                        },
                        {
                            "title": "Account Assistance",
                        },
                        {
                            "title": "Feedback and Complaints",
                        },
                        {
                            "title": "Request a Callback",
                        },
                        {
                            "title": "Other Queries",
                        },
                    ],
                }
            ],
        }

        response = requests.post(endpoint_url, headers=headers, json=payload)

        if response.status_code != 200:
            logger.error(
                f"Failed to send Speak to Advisor Menu. Status Code: {response.status_code}, Response: {response.text}"
            )
        else:
            logger.info(
                f"Successfully sent Speak to Advisor Menu. Status Code: {response.status_code}, Response: {response.text}"
            )

    except Exception as e:
        logger.error(
            f"An error occurred while sending the Speak to Advisor Menu: {str(e)}"
        )


def send_settings_menu(waid):
    try:
        headers = {
            "Authorization": WATI_BEARER_TOKEN,
            "Content-Type": "application/json",
        }

        endpoint_url = f"{WATI_API_ENDPOINT}?whatsappNumber={waid}"

        payload = {
            "body": "Settings Menu:\n\nPlease select an option below to manage your settings.",
            "buttonText": "Menu",
            "footer": "mNivesh Team",
            "sections": [
                {
                    "title": "Settings",
                    "rows": [
                        {
                            "title": "Password",
                        },
                        {
                            "title": "Notify",
                        },
                        {
                            "title": "Lang",
                        },
                        {
                            "title": "Privy",
                        },
                        {
                            "title": "Acc deacvt",
                        },
                        {
                            "title": "menu",
                        },
                    ],
                }
            ],
        }

        response = requests.post(endpoint_url, headers=headers, json=payload)

        if response.status_code != 200:
            logger.error(
                f"Failed to send Settings Menu. Status Code: {response.status_code}, Response: {response.text}"
            )
        else:
            logger.info(
                f"Successfully sent Settings Menu. Status Code: {response.status_code}, Response: {response.text}"
            )

    except Exception as e:
        logger.error(f"An error occurred while sending the Settings Menu: {str(e)}")


def send_View_holding(waid):
    send_message_via_wati(waid, format_portfolio_report())


def send_top5_equity(waid):
    """Sends an interactive list of top 5 Equity mutual fund schemes on WhatsApp."""

    # Define the top 5 mutual fund schemes recommended by you
    recommended_schemes = """
        Scheme A
        Scheme B
        Scheme C
        Scheme D
        Scheme E
    """

    # Construct the interactive message
    body_message = (
        "Here are the top 5 Equity mutual fund schemes recommended by us:\n{}".format(
            recommended_schemes
        )
    )

    # Define the URL for sending the interactive message
    url = f"{WATI_API_URL}/api/v1/sendInteractiveListMessage?whatsappNumber={waid}"

    payload = {
        "sections": [
            {
                "rows": [
                    {"title": "Large Cap"},
                    {"title": "Mid Cap"},
                    {"title": "Small Cap"},
                    {"title": "Large and Mid"},
                    {"title": "Flexi Cap"},
                    {"title": "Multi Cap"},
                    {"title": "Sectoral"},
                ],
                "title": "Top Schemes",
            }
        ],
        "body": body_message,
        "buttonText": "Menu",
        "footer": "mNivesh Team",
    }
    headers = {"content-type": "text/json", "Authorization": WATI_BEARER_TOKEN}
    # print(response.text)
    # Send the interactive message
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"API Response: {response.text}")  # Log the full response for debugging
        if response.status_code == 200:
            return {"message": "Recommendation sent successfully!"}
        else:
            return {"error": f"Failed to send message. Response: {response.text}"}
    except Exception as e:
        return {"error": str(e)}


def send_top5_hybrid(waid):
    """Sends an interactive list of top 5 Equity mutual fund schemes on WhatsApp."""

    # Define the top 5 mutual fund schemes recommended by you
    recommended_schemes = """
        Scheme A
        Scheme B
        Scheme C
        Scheme D
        Scheme E
    """

    # Construct the interactive message
    body_message = (
        "Here are the top 5 Hybrid mutual fund schemes recommended by us:\n{}".format(
            recommended_schemes
        )
    )

    # Define the URL for sending the interactive message
    url = f"{WATI_API_URL}/api/v1/sendInteractiveListMessage?whatsappNumber={waid}"

    payload = {
        "sections": [
            {
                "rows": [
                    {"title": "Balanced Advantage Funds"},
                    {"title": "Multi Asset Funds"},
                ],
                "title": "Top Schemes",
            }
        ],
        "body": body_message,
        "buttonText": "Menu",
        "footer": "mNivesh Team",
    }
    headers = {"content-type": "text/json", "Authorization": WATI_BEARER_TOKEN}

    print(response.text)

    # Send the interactive message
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"API Response: {response.text}")  # Log the full response for debugging
        if response.status_code == 200:
            return {"message": "Recommendation sent successfully!"}
        else:
            return {"error": f"Failed to send message. Response: {response.text}"}
    except Exception as e:
        return {"error": str(e)}


def send_top5_debt(waid):
    """Sends an interactive list of top 5 mutual fund schemes on WhatsApp."""

    # Define the top 5 mutual fund schemes recommended by you
    recommended_schemes = """
        Scheme A
        Scheme B
        Scheme C
        Scheme D
        Scheme E
    """

    # Construct the interactive message
    body_message = (
        "Here are the top 5 Debt mutual fund schemes recommended by us:\n{}".format(
            recommended_schemes
        )
    )

    # Define the URL for sending the interactive message
    url = f"{WATI_API_URL}/api/v1/sendInteractiveListMessage?whatsappNumber={waid}"

    payload = {
        "sections": [
            {
                "rows": [
                    {"title": "Liquid Funds"},
                    {"title": "Overnight Funds"},
                    {"title": "Banking and PSU Funds"},
                    {"title": "Corporate Bond Funds"},
                    {"title": "Credit Risk Funds"},
                ],
                "title": "Top Schemes",
            }
        ],
        "body": body_message,
        "buttonText": "Menu",
        "footer": "mNivesh Team",
    }
    headers = {"content-type": "text/json", "Authorization": WATI_BEARER_TOKEN}

    print(response.text)

    # Send the interactive message
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"API Response: {response.text}")  # Log the full response for debugging
        if response.status_code == 200:
            return {"message": "Recommendation sent successfully!"}
        else:
            return {"error": f"Failed to send message. Response: {response.text}"}
    except Exception as e:
        return {"error": str(e)}


def send_top5_large(waid):
    """Sends an interactive list of top 5 mutual fund schemes on WhatsApp."""

    # Define the top 5 mutual fund schemes recommended by you
    recommended_schemes = """
        Scheme A
        Scheme B
        Scheme C
        Scheme D
        Scheme E
    """

    # Construct the interactive message
    body_message = "Here are the top 5 Large Cap mutual fund schemes recommended by us:\n{}".format(
        recommended_schemes
    )

    # Define the URL for sending the interactive message
    url = f"{WATI_API_URL}/api/v1/sendSessionMessage/{waid}?messageText={body_message}"

    headers = {"Authorization": WATI_BEARER_TOKEN}

    # Send the interactive message
    try:
        response = requests.post(url, headers=headers)
        print(f"API Response: {response.text}")  # Log the full response for debugging
        if response.status_code == 200:
            return {"message": "Recommendation sent successfully!"}
        else:
            return {"error": f"Failed to send message. Response: {response.text}"}
    except Exception as e:
        return {"error": str(e)}


def send_top5_mid(waid):
    """Sends an interactive list of top 5 mutual fund schemes on WhatsApp."""

    # Define the top 5 mutual fund schemes recommended by you
    recommended_schemes = """
        Scheme A
        Scheme B
        Scheme C
        Scheme D
        Scheme E
    """

    # Construct the interactive message
    body_message = (
        "Here are the top 5 Mid Cap mutual fund schemes recommended by us:\n{}".format(
            recommended_schemes
        )
    )

    # Define the URL for sending the interactive message
    url = f"{WATI_API_URL}/api/v1/sendSessionMessage/{waid}?messageText={body_message}"

    headers = {"Authorization": WATI_BEARER_TOKEN}

    print(response.text)
    # Send the interactive message
    try:
        response = requests.post(url, headers=headers)
        print(f"API Response: {response.text}")  # Log the full response for debugging
        if response.status_code == 200:
            return {"message": "Recommendation sent successfully!"}
        else:
            return {"error": f"Failed to send message. Response: {response.text}"}
    except Exception as e:
        return {"error": str(e)}


def send_top5_small(waid):
    """Sends an interactive list of top 5 mutual fund schemes on WhatsApp."""

    # Define the top 5 mutual fund schemes recommended by you
    recommended_schemes = """
        Scheme A
        Scheme B
        Scheme C
        Scheme D
        Scheme E
    """

    # Construct the interactive message
    body_message = "Here are the top 5 Small Cap mutual fund schemes recommended by us:\n{}".format(
        recommended_schemes
    )

    # Define the URL for sending the interactive message
    url = f"{WATI_API_URL}/api/v1/sendSessionMessage/{waid}?messageText={body_message}"

    headers = {"Authorization": WATI_BEARER_TOKEN}

    print(response.text)
    # Send the interactive message
    try:
        response = requests.post(url, headers=headers)
        print(f"API Response: {response.text}")  # Log the full response for debugging
        if response.status_code == 200:
            return {"message": "Recommendation sent successfully!"}
        else:
            return {"error": f"Failed to send message. Response: {response.text}"}
    except Exception as e:
        return {"error": str(e)}


def send_top5_large_mid(waid):
    """Sends an interactive list of top 5 mutual fund schemes on WhatsApp."""

    # Define the top 5 mutual fund schemes recommended by you
    recommended_schemes = """
        Scheme A
        Scheme B
        Scheme C
        Scheme D
        Scheme E
    """

    # Construct the interactive message
    body_message = "Here are the top 5 Large and Mid Cap mutual fund schemes recommended by us:\n{}".format(
        recommended_schemes
    )

    # Define the URL for sending the interactive message
    url = f"{WATI_API_URL}/api/v1/sendSessionMessage/{waid}?messageText={body_message}"

    headers = {"Authorization": WATI_BEARER_TOKEN}

    print(response.text)
    # Send the interactive message
    try:
        response = requests.post(url, headers=headers)
        print(f"API Response: {response.text}")  # Log the full response for debugging
        if response.status_code == 200:
            return {"message": "Recommendation sent successfully!"}
        else:
            return {"error": f"Failed to send message. Response: {response.text}"}
    except Exception as e:
        return {"error": str(e)}


def send_top5_flexi(waid):
    """Sends an interactive list of top 5 mutual fund schemes on WhatsApp."""

    # Define the top 5 mutual fund schemes recommended by you
    recommended_schemes = """
        Scheme A
        Scheme B
        Scheme C
        Scheme D
        Scheme E
    """

    # Construct the interactive message
    body_message = "Here are the top 5 Flexi Cap mutual fund schemes recommended by us:\n{}".format(
        recommended_schemes
    )

    # Define the URL for sending the interactive message
    url = f"{WATI_API_URL}/api/v1/sendSessionMessage/{waid}?messageText={body_message}"

    headers = {"Authorization": WATI_BEARER_TOKEN}

    print(response.text)
    # Send the interactive message
    try:
        response = requests.post(url, headers=headers)
        print(f"API Response: {response.text}")  # Log the full response for debugging
        if response.status_code == 200:
            return {"message": "Recommendation sent successfully!"}
        else:
            return {"error": f"Failed to send message. Response: {response.text}"}
    except Exception as e:
        return {"error": str(e)}


def send_top5_mutli(waid):
    """Sends an interactive list of top 5 mutual fund schemes on WhatsApp."""

    # Define the top 5 mutual fund schemes recommended by you
    recommended_schemes = """
        Scheme A
        Scheme B
        Scheme C
        Scheme D
        Scheme E
    """

    # Construct the interactive message
    body_message = "Here are the top 5 Multi Cap mutual fund schemes recommended by us:\n{}".format(
        recommended_schemes
    )

    # Define the URL for sending the interactive message
    url = f"{WATI_API_URL}/api/v1/sendSessionMessage/{waid}?messageText={body_message}"

    headers = {"Authorization": WATI_BEARER_TOKEN}

    print(response.text)
    # Send the interactive message
    try:
        response = requests.post(url, headers=headers)
        print(f"API Response: {response.text}")  # Log the full response for debugging
        if response.status_code == 200:
            return {"message": "Recommendation sent successfully!"}
        else:
            return {"error": f"Failed to send message. Response: {response.text}"}
    except Exception as e:
        return {"error": str(e)}


def send_top5_sectoral(waid):
    """Sends an interactive list of top 5 mutual fund schemes on WhatsApp."""

    # Define the top 5 mutual fund schemes recommended by you
    recommended_schemes = """
        Scheme A
        Scheme B
        Scheme C
        Scheme D
        Scheme E
    """

    # Construct the interactive message
    body_message = (
        "Here are the top 5 Sectoral mutual fund schemes recommended by us:\n{}".format(
            recommended_schemes
        )
    )

    # Define the URL for sending the interactive message
    url = f"{WATI_API_URL}/api/v1/sendSessionMessage/{waid}?messageText={body_message}"

    headers = {"Authorization": WATI_BEARER_TOKEN}

    print(response.text)
    # Send the interactive message
    try:
        response = requests.post(url, headers=headers)
        print(f"API Response: {response.text}")  # Log the full response for debugging
        if response.status_code == 200:
            return {"message": "Recommendation sent successfully!"}
        else:
            return {"error": f"Failed to send message. Response: {response.text}"}
    except Exception as e:
        return {"error": str(e)}


def send_top5_liquid(waid):
    """Sends an interactive list of top 5 mutual fund schemes on WhatsApp."""

    # Define the top 5 mutual fund schemes recommended by you
    recommended_schemes = """
        Scheme A
        Scheme B
        Scheme C
        Scheme D
        Scheme E
    """

    # Construct the interactive message
    body_message = (
        "Here are the top 5 Liquid mutual fund schemes recommended by us:\n{}".format(
            recommended_schemes
        )
    )

    # Define the URL for sending the interactive message
    url = f"{WATI_API_URL}/api/v1/sendSessionMessage/{waid}?messageText={body_message}"

    headers = {"Authorization": WATI_BEARER_TOKEN}

    print(response.text)
    # Send the interactive message
    try:
        response = requests.post(url, headers=headers)
        print(f"API Response: {response.text}")  # Log the full response for debugging
        if response.status_code == 200:
            return {"message": "Recommendation sent successfully!"}
        else:
            return {"error": f"Failed to send message. Response: {response.text}"}
    except Exception as e:
        return {"error": str(e)}


def send_top5_overnight(waid):
    """Sends an interactive list of top 5 mutual fund schemes on WhatsApp."""

    # Define the top 5 mutual fund schemes recommended by you
    recommended_schemes = """
        Scheme A
        Scheme B
        Scheme C
        Scheme D
        Scheme E
    """

    # Construct the interactive message
    body_message = "Here are the top 5 Overnight mutual fund schemes recommended by us:\n{}".format(
        recommended_schemes
    )

    # Define the URL for sending the interactive message
    url = f"{WATI_API_URL}/api/v1/sendSessionMessage/{waid}?messageText={body_message}"

    headers = {"Authorization": WATI_BEARER_TOKEN}

    print(response.text)
    # Send the interactive message
    try:
        response = requests.post(url, headers=headers)
        print(f"API Response: {response.text}")  # Log the full response for debugging
        if response.status_code == 200:
            return {"message": "Recommendation sent successfully!"}
        else:
            return {"error": f"Failed to send message. Response: {response.text}"}
    except Exception as e:
        return {"error": str(e)}


def send_top5_banking_psu(waid):
    """Sends an interactive list of top 5 mutual fund schemes on WhatsApp."""

    # Define the top 5 mutual fund schemes recommended by you
    recommended_schemes = """
        Scheme A
        Scheme B
        Scheme C
        Scheme D
        Scheme E
    """

    # Construct the interactive message
    body_message = "Here are the top 5 Banking and PSU mutual fund schemes recommended by us:\n{}".format(
        recommended_schemes
    )

    # Define the URL for sending the interactive message
    url = f"{WATI_API_URL}/api/v1/sendSessionMessage/{waid}?messageText={body_message}"

    headers = {"Authorization": WATI_BEARER_TOKEN}

    print(response.text)
    # Send the interactive message
    try:
        response = requests.post(url, headers=headers)
        print(f"API Response: {response.text}")  # Log the full response for debugging
        if response.status_code == 200:
            return {"message": "Recommendation sent successfully!"}
        else:
            return {"error": f"Failed to send message. Response: {response.text}"}
    except Exception as e:
        return {"error": str(e)}


def send_top5_corporate(waid):
    """Sends an interactive list of top 5 mutual fund schemes on WhatsApp."""

    # Define the top 5 mutual fund schemes recommended by you
    recommended_schemes = """
        Scheme A
        Scheme B
        Scheme C
        Scheme D
        Scheme E
    """

    # Construct the interactive message
    body_message = "Here are the top 5 Corporate Bond mutual fund schemes recommended by us:\n{}".format(
        recommended_schemes
    )

    # Define the URL for sending the interactive message
    url = f"{WATI_API_URL}/api/v1/sendSessionMessage/{waid}?messageText={body_message}"

    headers = {"Authorization": WATI_BEARER_TOKEN}

    print(response.text)
    # Send the interactive message
    try:
        response = requests.post(url, headers=headers)
        print(f"API Response: {response.text}")  # Log the full response for debugging
        if response.status_code == 200:
            return {"message": "Recommendation sent successfully!"}
        else:
            return {"error": f"Failed to send message. Response: {response.text}"}
    except Exception as e:
        return {"error": str(e)}


def send_top5_credit_risk(waid):
    """Sends an interactive list of top 5 mutual fund schemes on WhatsApp."""

    # Define the top 5 mutual fund schemes recommended by you
    recommended_schemes = """
        Scheme A
        Scheme B
        Scheme C
        Scheme D
        Scheme E
    """

    # Construct the interactive message
    body_message = "Here are the top 5 Credit Risk mutual fund schemes recommended by us:\n{}".format(
        recommended_schemes
    )

    # Define the URL for sending the interactive message
    url = f"{WATI_API_URL}/api/v1/sendSessionMessage/{waid}?messageText={body_message}"

    headers = {"Authorization": WATI_BEARER_TOKEN}

    print(response.text)
    # Send the interactive message
    try:
        response = requests.post(url, headers=headers)
        print(f"API Response: {response.text}")  # Log the full response for debugging
        if response.status_code == 200:
            return {"message": "Recommendation sent successfully!"}
        else:
            return {"error": f"Failed to send message. Response: {response.text}"}
    except Exception as e:
        return {"error": str(e)}


def send_top5_balanced(waid):
    """Sends an interactive list of top 5 mutual fund schemes on WhatsApp."""

    # Define the top 5 mutual fund schemes recommended by you
    recommended_schemes = """
        Scheme A
        Scheme B
        Scheme C
        Scheme D
        Scheme E
    """

    # Construct the interactive message
    body_message = "Here are the top 5 Balanced Advantage mutual fund schemes recommended by us:\n{}".format(
        recommended_schemes
    )

    # Define the URL for sending the interactive message
    url = f"{WATI_API_URL}/api/v1/sendSessionMessage/{waid}?messageText={body_message}"

    headers = {"Authorization": WATI_BEARER_TOKEN}

    print(response.text)
    # Send the interactive message
    try:
        response = requests.post(url, headers=headers)
        print(f"API Response: {response.text}")  # Log the full response for debugging
        if response.status_code == 200:
            return {"message": "Recommendation sent successfully!"}
        else:
            return {"error": f"Failed to send message. Response: {response.text}"}
    except Exception as e:
        return {"error": str(e)}


def send_top5_multi_asset(waid):
    """Sends an interactive list of top 5 mutual fund schemes on WhatsApp."""

    # Define the top 5 mutual fund schemes recommended by you
    recommended_schemes = """
        Scheme A
        Scheme B
        Scheme C
        Scheme D
        Scheme E
    """

    # Construct the interactive message
    body_message = "Here are the top 5 Multi-Asset mutual fund schemes recommended by us:\n{}".format(
        recommended_schemes
    )

    # Define the URL for sending the interactive message
    url = f"{WATI_API_URL}/api/v1/sendSessionMessage/{waid}?messageText={body_message}"

    headers = {"Authorization": WATI_BEARER_TOKEN}

    print(response.text)
    # Send the interactive message
    try:
        response = requests.post(url, headers=headers)
        print(f"API Response: {response.text}")  # Log the full response for debugging
        if response.status_code == 200:
            return {"message": "Recommendation sent successfully!"}
        else:
            return {"error": f"Failed to send message. Response: {response.text}"}
    except Exception as e:
        return {"error": str(e)}


def send_top5_fixed_deposit(waid):
    """Sends an interactive list of top 5 mutual fund schemes on WhatsApp."""

    # Define the top 5 mutual fund schemes recommended by you
    recommended_schemes = """
        Scheme A
        Scheme B
        Scheme C
        Scheme D
        Scheme E
    """

    # Construct the interactive message
    body_message = (
        "Here are the top 5 Fixed Deposit schemes recommended by us:\n{}".format(
            recommended_schemes
        )
    )

    # Define the URL for sending the interactive message
    url = f"{WATI_API_URL}/api/v1/sendSessionMessage/{waid}?messageText={body_message}"

    headers = {"Authorization": WATI_BEARER_TOKEN}

    print(response.text)
    # Send the interactive message
    try:
        response = requests.post(url, headers=headers)
        print(f"API Response: {response.text}")  # Log the full response for debugging
        if response.status_code == 200:
            return {"message": "Recommendation sent successfully!"}
        else:
            return {"error": f"Failed to send message. Response: {response.text}"}
    except Exception as e:
        return {"error": str(e)}


def how_to_invest1(waid):
    # Construct the interactive message
    body_message = f"The process to invest in mutual funds: \n\nStep 1: Talk to your Relationship Manager or click the link below if you're a new investor\nStep 2: Relationship Manager will gather information about your risk appetite, investment objective, tenure and other related questions\nStep 3: He'll recommend mutual funds as per your requirement\nStep 4: Open an account with us ( via electronically or physical forms )\nStep 5: Approve Transaction authentication Links\nStep 6: Your Relationship Manager will review your investment portfolio on regular basis and recommend changes after your approval\nStep 7: Start investing"

    # Define the URL for sending the interactive message
    url = f"{WATI_API_URL}/api/v1/sendSessionMessage/{waid}?messageText={body_message}"

    headers = {"Authorization": WATI_BEARER_TOKEN}

    print(response.text)
    # Send the interactive message
    try:
        response = requests.post(url, headers=headers)
        print(f"API Response: {response.text}")  # Log the full response for debugging
        if response.status_code == 200:
            return {"message": "How to Invest sent successfully!"}
        else:
            return {"error": f"Failed to send message. Response: {response.text}"}
    except Exception as e:
        return {"error": str(e)}


def how_to_invest(waid):
    # Define the URL for sending the interactive message
    url = f"{WATI_API_URL}/api/v1/sendInteractiveButtonsMessage?whatsappNumber={waid}"

    payload = {
        "buttons": [
            {"text": "Speak to your RM"},
            {"text": "Download mNivesh"},
            {"text": "Visit Website"},
        ],
        "body": f"The process to invest in mutual funds: \n\nStep 1: Talk to your Relationship Manager or click the link below if you're a new investor\nStep 2: Relationship Manager will gather information about your risk appetite, investment objective, tenure and other related questions\nStep 3: He'll recommend mutual funds as per your requirement\nStep 4: Open an account with us ( via electronically or physical forms )\nStep 5: Approve Transaction authentication Links\nStep 6: Your Relationship Manager will review your investment portfolio on regular basis and recommend changes after your approval\nStep 7: Start investing",
    }

    headers = {"content-type": "text/json", "Authorization": WATI_BEARER_TOKEN}

    response = requests.post(url, json=payload, headers=headers)
    return response.json()


def how_to_withdraw(waid):
    # Define the URL for sending the interactive message
    url = f"{WATI_API_URL}/api/v1/sendInteractiveButtonsMessage?whatsappNumber={waid}"

    payload = {
        "buttons": [
            {"text": "Speak to your RM"},
            {"text": "Download mNivesh"},
            {"text": "Visit Website"},
        ],
        "body": f"The process to withdraw from Mutual Funds:\n\nStep 1: Talk to your Relationship Manager or download our app or visit our website\nStep 2: Relationship Manager will provide you with best option feasible to avoid taxation as far as possible\nStep 3: Your Relationship Manager will send you the authentication Links after verification of your details\nStep 4: Approve Transaction authentication Links ( Our Service Manager team will guide you in the process )\nStep 5: You'll receive the amount in your registered bank account within 2-5 working days depending on your mutual fund schemes. \n\nStandard Withdrawal TAT\nT+1 is for Debt Mutual Fund Category\nT+2 is for Equity Mutual Fund and Hybrid Mutual Fund Categories\nT+4 is for International Mutual Funds and FOF categories",
    }

    headers = {"content-type": "text/json", "Authorization": WATI_BEARER_TOKEN}

    response = requests.post(url, json=payload, headers=headers)
    return response.json()


def check_portfolio(waid):
    # Define the URL for sending the interactive message
    url = f"{WATI_API_URL}/api/v1/sendInteractiveButtonsMessage?whatsappNumber={waid}"

    payload = {
        "buttons": [
            {"text": "Speak to your RM"},
            {"text": "Download mNivesh"},
            {"text": "Visit Website"},
        ],
        "body": (
            "You can check your portfolio through multiple routes:\n\nOption 1: You can visit our website https://niveshonline.com\nOption 2: You can download our iOS or Android App\nOption 3: You can avail our Whatsapp Service\nIn case of any query or need further help you, you can contact your relationship Manager"
        ),
    }

    headers = {"content-type": "text/json", "Authorization": WATI_BEARER_TOKEN}

    response = requests.post(url, json=payload, headers=headers)
    return response.json()


def taxation(waid):
    # Define the URL for sending the interactive message
    url = f"{WATI_API_URL}/api/v1/sendInteractiveButtonsMessage?whatsappNumber={waid}"

    body_payload = (
        "Taxation on Mutual Funds in India:\n\n"
        "*Equity Mutual Funds:*\n"
        "Short-term gains (held for less than 12 months): 15% tax.\n"
        "Long-term gains (held for more than 12 months): 10% tax on gains exceeding ₹1 lakh per year.\n\n"
        "*Debt Mutual Funds:*\n"
        "All interest earned are taxed as per individual's income tax slab.\n\n"
        "*Dividend Income:* It's taxable according to your income tax slab.\n\n"
        "*Switching or Redeeming Units:* Considered a transfer and may attract capital gains tax.\n\n"
        "*Note: Tax rules are subject to change. Always consult with your Relationship Manager for the latest information.*"
    )

    payload = {"buttons": [{"text": "Speak to your RM"}], "body": body_payload}

    headers = {"content-type": "text/json", "Authorization": WATI_BEARER_TOKEN}

    response = requests.post(url, json=payload, headers=headers)
    return response.json()


def contact_support(waid):
    # Define the URL for sending the interactive message
    url = f"{WATI_API_URL}/api/v1/sendInteractiveButtonsMessage?whatsappNumber={waid}"

    body_payload = (
        "Our Support is available 10 AM to 6 PM on working days except public holidays.\n\n"
        "You can email us at support@niveshonline.com \n"
        "or you may contact your Relationship Manager for any query\n\n"
        "For any other information or feedback, you can contact us at IVR +91 8269135135 or mail us at feedback@niveshonline.com"
    )

    payload = {"buttons": [{"text": "Speak to your RM"}], "body": body_payload}

    headers = {"content-type": "text/json", "Authorization": WATI_BEARER_TOKEN}

    response = requests.post(url, json=payload, headers=headers)
    return response.json()


def speak_rm(waid):
    # Define the URL for sending the interactive message
    rmCode = get_rm_code(waid)
    url = f"{WATI_API_URL}/api/v1/sendTemplateMessage?whatsappNumber={waid}"

    payload = {"broadcast_name": "rmDetails", "template_name": f"rm_detail_{rmCode}"}
    headers = {"content-type": "text/json", "Authorization": WATI_BEARER_TOKEN}

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)


# print(speak_rm("919910076952", "vb"))
# print(speak_rm("919910076952", "sm"))

if __name__ == "__main__":
    app.run(port=8181, debug=True)



vilakshan@Vilakshans-MacBook-Pro ~ % data='{
         "LoginId": "1346403",
         "MemberCode": "13464",
         "Password": "Mpcpl@113g",
         "TransType": "NEW",
         "STPType": "AMC",
         "ClientCode": "BZPPB4781I",
         "FromBSESchemeCode": "RMFTSGP-GR",
         "ToBSESchemeCode": "EOGP",
         "BuySellType": "Fresh",
         "TransactionMode": "P",
         "FolioNo": "401170768713",
         "STPRegNo": "",
         "IntRefNo": "20230923134641001",
         "StartDate": "10/10/2023",
         "FrequencyType": "MONTHLY",
         "NoOfTransfers": "12",
         "InstAmount": "5000",
         "InstUnit": "",
         "FirstOrderToday": "Y",
         "SubBrokerCode": "",
         "EUINDeclaration": "N",
         "EUINNumber": "",
         "Remarks": "test",
         "EndDate": "",
         "SubBrokerARN": "",
         "Filler1": "",
         "Filler2": "",
         "Filler3": "",
         "Filler4": "",
         "Filler5": ""
     }'
zsh: command not found: data
vilakshan@Vilakshans-MacBook-Pro ~ % 
