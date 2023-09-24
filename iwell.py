import requests
import json
import traceback
from datetime import datetime
import time
import PyPDF2

# Define your PAN and other constants here if they are not already defined
from config import (
    PAN,
    WATI_BEARER_TOKEN,
    WATI_API_URL,
    WATI_API_ENDPOINT,
    INVESTWELL_API_URL,
    INVESTWELL_AUTH_PASSWORD,
    INVESTWELL_AUTH_NAME,
)

# Define a logger (you can configure it according to your requirements)
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)


def get_investwell_token():
    url = f"{INVESTWELL_API_URL}/auth/getAuthorizationToken"
    payload = json.dumps(
        {"authName": INVESTWELL_AUTH_NAME, "password": INVESTWELL_AUTH_PASSWORD}
    )
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, data=payload)
    data = response.json()
    token = data.get("result").get("token")
    # print(token)
    return token


def get_portfolio_returns():
    end_date = "2022-09-11"
    pan = PAN
    url = "https://demo.investwell.app/api/aggregator/reports/getPortfolioReturns"

    token = get_investwell_token()
    # Define the filters as a list of dictionaries
    filters = [{"endDate": end_date}, {"pan": pan}]

    # Define the group parameter
    group = "folioid"

    # Create query parameters
    query_params = {
        "filters": json.dumps(filters),  # Convert filters to JSON format
        "group": group,
        "token": token,
    }

    # Debugging: Print the token for verification
    # print("Token:", token)

    # Make the GET request
    try:
        response = requests.get(url, params=query_params)
        if response.status_code == 200:
            data = response.json()
            # print(data)
            return data  # Return the entire JSON response
        else:
            return {"error": f"Request failed with status code {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def format_portfolio_report():
    # Check if the JSON response is valid
    json_response = get_portfolio_returns()
    if "status" in json_response and json_response["status"] == 0:
        data = json_response["result"]["data"]
        if not data:
            return "No portfolio data found."

        # Calculate the CAGR for the entire portfolio
        total_investment = sum(portfolio["purchaseValue"] for portfolio in data)
        total_current_value = sum(portfolio["currentValue"] for portfolio in data)
        total_returns = total_current_value - total_investment
        portfolio_cagr = (total_returns / total_investment) ** (1 / len(data)) - 1
        portfolio_cagr_percentage = portfolio_cagr * 100

        # Sort the portfolio data by CAGR in descending order
        sorted_data = sorted(data, key=lambda x: x["CAGR"], reverse=True)

        # Create a report with the top 5 holdings and portfolio CAGR
        report = "Here is your portfolio summary:\n"
        report += f"Portfolio CAGR: {portfolio_cagr_percentage:.2f}%\n\n"
        report += "Top 5 Holdings:\n"

        # Include the top 5 holdings in the report
        for i, portfolio in enumerate(sorted_data[:5], start=1):
            report += f"{i}. Scheme Name: {portfolio['schemeName']}\n"
            report += f"   Folio ID: {portfolio['folioid']}\n"
            report += f"   CAGR: {portfolio['CAGR']:.2f}%\n\n"

        return report
    else:
        return f"Error: {json_response.get('message', 'Unknown error')}"


def create_portfolio_summary_message():
    # Check if the JSON response is valid
    json_response = get_portfolio_returns()
    if "status" in json_response and json_response["status"] == 0:
        data = json_response["result"]["data"]
        if not data:
            return "No portfolio data found."

        # Calculate the total market value, invested amount, gain, and one day change
        market_value = sum(portfolio["currentValue"] for portfolio in data)
        invested_amount = sum(portfolio["purchaseValue"] for portfolio in data)
        gain = market_value - invested_amount
        one_day_change = sum(portfolio["oneDayChange"] for portfolio in data)

        # Format the message
        message = f"Mr VILAKSHAN BHUTANI\n\n"
        message += "*Your Current Portfolio* - \n"
        message += f"*Market Value:* ₹{market_value:,.0f}\n"
        message += f"*Invested Amount:* ₹{invested_amount:,.0f}\n"
        message += f"*Gain:* ₹{gain:,.0f}\n"
        message += f"*One Day Change:* ₹{one_day_change:,.0f}"

        return message
    else:
        return f"Error: {json_response.get('message', 'Unknown error')}"


def send_portfolio_report_and_message(waid):
    # declare variables
    name = "Vilakshan Bhutani"
    apiDate = datetime.now().strftime("%Y-%m-%d")
    displayDate = datetime.now().strftime("%d-%b-%Y")
    pan = PAN
    token = get_investwell_token()

    try:
        # Define the URL for fetching the PDF report
        pdf_url = f"{INVESTWELL_API_URL}/reports/getPortfolioReport?filters=[{{%22endDate%22:%22{apiDate}%22,%22dataSource%22:%220%22,%22pan%22:%22{pan}%22}}]&token={token}"

        response = requests.get(pdf_url)

        # Logging the response and status code for troubleshooting
        print("PDF Response Status Code:", response.status_code)

        if response.status_code == 200:
            pdf_data = response.content

            # Send the PDF report via WATI
            url = f"{WATI_API_URL}/api/v1/sendSessionFile/{waid}"
            headers = {"Authorization": WATI_BEARER_TOKEN}
            files = {"file": ("Report.pdf", pdf_data, "application/pdf")}
            pdf_response = requests.post(url, files=files, headers=headers)

            # Logging the PDF response and status code for troubleshooting
            print("PDF Sending Response Status Code:", pdf_response.status_code)
            print("PDF Sending Response Content:", pdf_response)

            if pdf_response.status_code == 200:
                # Send a follow-up message with buttons
                url = f"{WATI_API_URL}/api/v1/sendInteractiveButtonsMessage?whatsappNumber={waid}"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": WATI_BEARER_TOKEN,
                }
                payload = {
                    "body": f"Dear {name}, \n\nHere's your Portfolio Valuation Report as on {displayDate}.",
                    "buttons": [{"text": "Send Report on mail"}],
                    "footer": "mNivesh Team",
                }
                msg_response = requests.post(url, json=payload, headers=headers)

                # Logging the message response and status code for troubleshooting
                print("Message Response Status Code:", msg_response)
                print("Message Response Content:", msg_response.text)

                if msg_response.status_code == 200:
                    # Both PDF and message sent successfully
                    return {"message": "Report and message sent successfully"}
                else:
                    # Failed to send the follow-up message
                    return {"error": "Failed to send follow-up message"}
            else:
                # Failed to send the PDF
                return {"error": "Failed to send PDF"}
        else:
            # Failed to fetch the PDF
            return {"error": "Failed to fetch PDF"}

    except Exception as e:
        # Handle other exceptions and log the error
        print(f"An error occurred: {str(e)}")
        traceback.print_exc()
        return {"error": "Internal server error"}


def get_appID_from_portfolio_returns():
    try:
        json_response = get_portfolio_returns()
        if "status" in json_response and json_response["status"] == 0:
            appID = json_response["result"]["data"][0]["appid"]
            if not appID:
                return "No appID data found."
            # print(f"AppID: {appID}")
            return appID
        else:
            print(f"Request failed with status.")
            return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


def send_capital_gain_summary(waid, year):
    # declare variables
    name = "Vilakshan Bhutani"
    apiDate = datetime.now().strftime("%Y-%m-%d")
    displayDate = datetime.now().strftime("%d-%b-%Y")
    pan = PAN
    token = get_investwell_token()
    # Call get_appID_from_portfolio_returns to get the appID
    appID = get_appID_from_portfolio_returns()
    print(appID)
    # Ensure that appID is not None
    if not appID:
        return {"error": "appID is None"}

    try:
        # Define the URL for fetching the PDF report
        # Define the URL for fetching the PDF report
        pdf_url = f"{INVESTWELL_API_URL}/reports/downloadRealizedCapitalGainPDF?filters=[{{%22casArnOption%22:%220%22,%22pan%22:%22{PAN}%22}}]&year={year}&pdfType=summary&clubTxns=false&preferences=[{{%22products%22:[{{%22name%22:%22MF%22,%22isRequired%22:true}},{{%22name%22:%22EQ%22,%22isRequired%22:true}}],%22gainTypes%22:[{{%22name%22:%22debtShortTerm%22,%22isRequired%22:true}},{{%22name%22:%22debtLongTerm%22,%22isRequired%22:true}},{{%22name%22:%22equityShortTerm%22,%22isRequired%22:true}},{{%22name%22:%22equityLongTerm%22,%22isRequired%22:true}}]}}]&token={token}"
        print(f"pdf_url: {pdf_url}")

        response = requests.get(pdf_url)

        # Logging the response and status code for troubleshooting
        print("PDF Response Status Code:", response.status_code)

        if response.status_code == 200:
            pdf_data = response.content

            # Send the PDF report via WATI
            url = f"{WATI_API_URL}/api/v1/sendSessionFile/{waid}"
            headers = {"Authorization": WATI_BEARER_TOKEN}
            files = {"file": ("Capital Gain Realised.pdf", pdf_data, "application/pdf")}
            pdf_response = requests.post(url, files=files, headers=headers)

            # Logging the PDF response and status code for troubleshooting
            print("PDF Sending Response Status Code:", pdf_response.status_code)
            print("PDF Sending Response Content:", pdf_response.content)

            if pdf_response.status_code == 200:
                # Send a follow-up message with buttons
                url = f"{WATI_API_URL}/api/v1/sendInteractiveButtonsMessage?whatsappNumber={waid}"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": WATI_BEARER_TOKEN,
                }
                payload = {
                    "body": f"Dear {name}, \n\nHere's your Realised Capital Gain Report for FY{year-1}-{year}.",
                    "buttons": [{"text": "Send on mail"}],
                    "footer": "mNivesh Team",
                }
                msg_response = requests.post(url, json=payload, headers=headers)

                # Logging the message response and status code for troubleshooting
                print("Message Response Status Code:", msg_response.status_code)

                if msg_response.status_code == 200:
                    # Both PDF and message sent successfully
                    return {"message": "Report and message sent successfully"}
                else:
                    # Failed to send the follow-up message
                    return {"error": "Failed to send follow-up message"}
            else:
                # Failed to send the PDF
                return {"error": "Failed to send PDF"}
        else:
            # Failed to fetch the PDF
            return {"error": "Failed to fetch PDF"}

    except Exception as e:
        # Handle other exceptions and log the error
        print(f"An error occurred: {str(e)}")
        traceback.print_exc()
        return {"error": "Internal server error"}


# if __name__ == "__main__":
# Assuming you have Flask's app defined elsewhere in the code
# app.run(debug=True)
# waid = "919910076952"
# print(send_portfolio_report_and_message(waid))
