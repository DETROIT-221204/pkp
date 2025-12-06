
import requests
import time
from bs4 import BeautifulSoup
import pandas as pd
from flask import Flask, render_template, request, url_for,redirect,session
import plotly.express as px
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
import plotly.graph_objects as go
from io import StringIO
from flask import jsonify
import json
import plotly.offline as pyo
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from gainerslosers import get_top_gainers,get_top_losers
from prophet import Prophet
from overallstocknews import get_news
from getstockanalysis import get_stock_analysis,analyze_company_data
from getcompanynews import get_company_news,finbert_sentiment
from getnifty import get_nifty,process_nifty_index
from getstockprice import get_stock_price
from gold import get_gold_price,get_gold_news,gold_growth,get_gold_average,generate_gold_advice,calculate_gold_investment
from generateaiadvice import generate_ai_advice
from stockfuture import predict_future_price
from realestateinsight import get_real_estate_insight
from compareassets import process_compare_assets
from mutualfunds import process_mutual_fund
app = Flask(__name__)
app.secret_key = ""   # change this in production

API_KEY = ""  #DEEPSEEK

API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Read data from CSV
try:
    data_df = pd.read_csv('NSE Symbols.CSV') # Renamed to data_df to avoid conflict with 'data' variable in index function
    name_company = [{'company': data_df['Company Name'][_], 'code': data_df['Scrip'][_]} for _ in range(len(data_df))]
except FileNotFoundError:
    print("Error: CSV file 'NSE Symbols.CSV' not found.")
    name_company = []


        # print(f"\n📈 Predicted Next Close Price: ₹{next_price[0][0]:.2f}")


# def get_data(scrip,start,end):
#     scrip=scrip+".BO"
#     data=yf.download(scrip,start=start,end=end,group_by='ticker',auto_adjust=True)
#     return data
#     pass




# def get_AI_advice(company):
#     API_KEY = "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"
#     API_URL = "https://openrouter.ai/api/v1/chat/completions"
#     user_message = f'Should i invest in {company}'
#     headers = {
#         "Authorization": f"Bearer {API_KEY}",
#         "Content-Type": "application/json",
#         "HTTP-Referer": "https://www.yoursite.com",
#         "X-Title": "FlaskChatApp"
#     }
#
#     payload = {
#         "model": "deepseek/deepseek-r1:free",
#         "messages": [{"role": "user", "content": user_message}]
#     }
#     try:
#         response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
#         response.raise_for_status()
#         data = response.json()
#         reply = data["choices"][0]["message"]["content"]
#         return jsonify({"reply": reply})
#     except Exception as e:
#         return jsonify({"reply": f"Error: {str(e)}"})

@app.route('/')
def home():
    headlines=get_news()
    return render_template('home.html',headlines=headlines)
@app.route('/stock', methods=['GET'])
def search():
    gainers=get_top_gainers()
    losers=get_top_losers()
    selected_ticker = request.args.get('company')
    price = get_stock_price(selected_ticker) if selected_ticker else "Select a company"
    nifty=get_nifty()
    nifty_name=['NIFTY 50','SENSEX','Nifty Bank','Nifty IT','S&P BSE SmallCap']
    nifty_data = dict(zip(nifty_name, nifty))
    # Fetch most active stocks
    most_active = []
    try:
        india_page = 'https://www.google.com/finance/markets/most-active?hl=en&gl=IN'
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(india_page, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        stock_elements = [stock.text.strip() for stock in soup.find_all("div", class_="ZvmM7")]
        most_active = stock_elements[:10]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching most active stocks: {e}")

    # Fetch financial news
    headlines=get_news()

    return render_template('search.html', name_company=name_company, price=price,
                           most_active=most_active, headlines=headlines,
                           nifty_data=nifty_data, gainers=gainers,losers=losers)





@app.route("/get_ai_advice", methods=["POST"])
def get_ai_advice():
    try:
        data = request.get_json()
        company = data.get("company", "").strip()

        reply = generate_ai_advice(company)

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"⚠️ An error occurred: {str(e)}"})



data_df = pd.read_csv('NSE Symbols.CSV') # Renamed to data_df to avoid conflict with 'data' variable in index function
name_company1 = [{'company': data_df['Company Name'][_], 'code': data_df['Scrip'][_]} for _ in range(len(data_df))]
@app.route('/<string:company>', methods=['GET', 'POST'])
def index(company):
    results = analyze_company_data(company, name_company1, request)

    future_price = predict_future_price(company, name_company1)

    price = get_stock_price(results["scrip_code"])
    news_data = get_company_news(company=company)

    return render_template(
        'graph.html',
        company=company,
        scrip_code=results["scrip_code"],
        table_data=results["table_data"],
        fig_html=results["fig_html"],
        error=results["error"],
        start_date_display=results["start_date_display"],
        end_date_display=results["end_date_display"],
        price=price,
        months=results["months"],
        trend=results["trend"],
        average_return=results["average_return"],
        avg_volatility=results["avg_volatility"],
        best_month=results["best_month"],
        worst_month=results["worst_month"],
        max_vol_row=results["max_vol_row"],
        suggestion=results["suggestion"],
        return_percentage=results["return_percentage"],
        future_price=future_price,

        headlines=news_data["headlines"],       # list of headlines + sentiment
        overall_sentiment=news_data["overall_sentiment"],
        sentiment_summary=news_data["summary"]
    )

@app.route('/get_ai_goldadvice', methods=['POST'])
def get_ai_goldadvice():
    try:
        response_text = generate_gold_advice()
        return jsonify({"reply": response_text})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

@app.route('/gold', methods=['GET', 'POST'])
def gold():
    news = get_gold_news()
    data_df = pd.read_csv('gold_data.csv')
    data_df['Date'] = pd.to_datetime(data_df['Date'], dayfirst=True)

    # Plot graph
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data_df['Date'], y=data_df['High'], mode='lines', name='Gold Price'))
    fig.update_layout(
        title='Gold Price (Last 10 Years)',
        xaxis_title='Date',
        yaxis_title='Price ($)',
        template='plotly_dark',
        width=700,
        height=400
    )
    fig_html = fig.to_html(full_html=False)

    # Static prices
    gold_prices = {
        2025: 102000, 2024: 78245, 2023: 63203, 2022: 55017, 2021: 48099, 2020: 50151,
        2019: 39108, 2018: 31391, 2017: 29156, 2016: 27445, 2015: 24931, 2014: 26703,
        2013: 28422, 2012: 30859, 2011: 27329, 2010: 20728, 2009: 16686, 2008: 13630,
        2007: 10598, 2006: 9265, 2005: 7638, 2004: 6307, 2003: 5600, 2002: 4990,
        2001: 4300, 2000: 4400
    }

    # Default values
    investment_result = None

    if request.method == 'POST':
        try:
            year = int(request.form['year'])
            amount = float(request.form['amount'])
            investment_result = calculate_gold_investment(year, amount, gold_prices)
        except Exception as e:
            print("❌ Error:", e)

    return render_template(
        'gold.html',
        fig_html=fig_html,
        gold_price=get_gold_price(),
        gold_average=get_gold_average(),
        gold_price_chart=gold_growth(),
        investment_result=investment_result,
        news=news
    )

@app.route('/nifty/<string:name>', methods=['GET', 'POST'])
def Nifty(name):
    index_info = {
        'NIFTY 50': {
            'csv': 'dataset/Nifty50_history.csv',
            'url': 'https://www.google.com/finance/quote/NIFTY_50:INDEXNSE?hl=en',
            'news': 'https://www.google.com/finance/quote/NIFTY_50:INDEXNSE?hl=en'
        },
        'SENSEX': {
            'csv': 'dataset/Sensex_hstry.csv',
            'url': 'https://www.google.com/finance/quote/SENSEX:INDEXBOM?hl=en',
            'news': 'https://www.google.com/finance/quote/SENSEX:INDEXBOM?hl=en'
        },
        'Nifty Bank': {
            'csv': 'dataset/Nifty_bank_histor.csv',
            'url': 'https://www.google.com/finance/quote/NIFTY_BANK:INDEXNSE?hl=en',
            'news': 'https://www.google.com/finance/quote/NIFTY_BANK:INDEXNSE?hl=en'
        },
        'Nifty IT': {
            'csv': 'dataset/Nifty_IT.csv',
            'url': 'https://www.google.com/finance/quote/NIFTY_IT:INDEXNSE?hl=en',
            'news': 'https://www.google.com/finance/quote/NIFTY_IT:INDEXNSE?hl=en'
        }
    }

    if name not in index_info:
        return "Index not found", 404

    results = process_nifty_index(name, index_info)

    return render_template(
        'nifty.html',
        name=name,
        fig_html=results["fig_html"],
        price_tag=results["price"],
        headlines=results["headlines"]
    )
@app.route('/compare')
def compare():
    stock1 = request.args.get('stock1')
    stock2 = request.args.get('stock2')
    months=request.args.get('months',6,type=int)
    data1 = get_stock_analysis(stock1,months)
    data2 = get_stock_analysis(stock2,months)

    return render_template('compare.html',
                           name_company=name_company,
                           stock1_data=data1,
                           stock2_data=data2)
dta = pd.read_csv('dataset/NHDMumbai.csv')
@app.route('/real_estate',methods=['GET','POST'])
def real_estate():


    locations = sorted(list(set(dta['Locality'].tolist())))

    return render_template('real_estate.html',locations=locations)

@app.route('/real_estate/<string:location>', methods=['GET', 'POST'])
def rs_insight(location):
    insight = get_real_estate_insight(location)

    return render_template('real_estate_insight.html',
        **insight )


@app.route('/real_estate/compare', methods=['GET', 'POST'])
def rs_compare():
    location1 = None
    location2 = None
    insight1 = None
    insight2 = None
    locations = sorted(list(set(dta['Locality'].tolist())))

    if request.method == 'POST':
        location1 = request.form['location1']
        location2 = request.form['location2']

        if location1 and location2:
            insight1 = get_real_estate_insight(location1)
            insight2 = get_real_estate_insight(location2)

    return render_template(
        'compare_rs.html',
        locations=locations,
        location1=location1,
        location2=location2,
        insight1=insight1,
        insight2=insight2
    )
locations = sorted(list(set(dta['Locality'].tolist())))
crypto_options = ["Bitcoin", "Ethereum", "Tether", "BNB", "USD Coin"]
gold_options = ["24K", "22K", "18K"]



@app.route('/compare_assets', methods=['GET', 'POST'])
def compare_assets():
    results = process_compare_assets(request)

    return render_template(
        "compare_assets.html",
        selected_assets=results["selected_assets"],
        selections=results["selections"],
        locations=locations,
        name_company=name_company,
        stock_data=results["stock_data"],
        gold_data=results["gold_data"],
        gold_price=get_gold_price(),
        gold_average=get_gold_average(),
        gold_price_chart=results["gold_price_chart"],
        return_percentage=results["return_percentage"],
        real_estate_graph=results["real_estate_graph"],
        real_estate_return=results["insight"]['return_percentage'] if results["insight"] else None,
        real_estate_insight=results["insight"]['advice'] if results["insight"] else None,
        months=results["months"],
        summary=results["summary"]
    )

# ✅ Replace with your actual API key
OPENROUTER_API_KEY = ""

@app.route("/Ai-Assistant")
def Assistant():
    return render_template("aiassistant.html")


@app.route("/api", methods=["POST"])
def chat_api():
    """Handles chat requests using OpenRouter NVIDIA Nemotron model."""
    try:
        import requests, json

        # ✅ Get user message from frontend
        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"reply": "⚠️ Please enter a valid message."})

        # ✅ Formatting prompt for structured Markdown reply
        structured_prompt = f"""
        Reformat the answer in a clear, structured way using Markdown:

        - Start with a short introduction.
        - Use ### Headings for sections.
        - Use bullet points (-) or numbered lists where appropriate.
        - If there are Pros and Cons, format them in a Markdown table.
        - End with a clear **Bottom Line**.

        User Question: {user_message}
        """

        # ✅ Send request to OpenRouter (NVIDIA Nemotron model)
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:5000",  # optional for ranking
                "X-Title": "DhanGyan AI Assistant",       # optional
            },
            data=json.dumps({
                "model": "nvidia/nemotron-nano-9b-v2:free",
                "messages": [
                    {
                        "role": "user",
                        "content": structured_prompt
                    }
                ],
            }),
        )

        # ✅ Handle API errors gracefully
        if response.status_code != 200:
            return jsonify({"reply": f"❌ API Error: {response.text}"})

        # ✅ Extract AI response safely
        response_data = response.json()
        ai_reply = (
            response_data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )

        # ✅ Return formatted AI response to frontend
        return jsonify({"reply": ai_reply.strip() or "⚠️ No response from AI."})

    except Exception as e:
        return jsonify({"reply": f"⚠️ An error occurred: {str(e)}"})
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///users.db"
db=SQLAlchemy(model_class=Base)
db.init_app(app)
class User(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    email: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)

    # One-to-many relationship with UserInterest
    interests = relationship("UserInterest", back_populates="user", cascade="all, delete-orphan")


class UserInterest(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    interest: Mapped[str] = mapped_column(String(100), nullable=False)

    user = relationship("User", back_populates="interests")

class Asset(db.Model):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asset_type: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    investment_options = relationship("InvestmentOption", back_populates="asset")

with app.app_context():

    db.create_all()

@app.route("/set_interest/<string:topic>", methods=["POST"])
def set_interest(topic):
    if "user_id" not in session:
        return jsonify({"status": "not_logged_in"}), 401

    user = User.query.get(session["user_id"])
    if not user:
        return jsonify({"status": "error"}), 400

    # Check if this interest already exists for the user
    existing = UserInterest.query.filter_by(user_id=user.id, interest=topic).first()
    if not existing:
        new_interest = UserInterest(user_id=user.id, interest=topic)
        db.session.add(new_interest)
        db.session.commit()

    interests = [i.interest for i in user.interests]
    return jsonify({"status": "success", "interests": interests})

@app.route("/signup", methods=["GET", "POST"])
def signup():
    user = False
    msg = None
    if request.method == "POST":
        name = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            msg = "Your account already exists. Please log in."
            return render_template("signup.html", msg=msg, user=user)

        # If new user -> save to DB
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        user = True

        # --- ADD SESSION ---
        session["user_id"] = new_user.id
        session["email"] = new_user.email
        # -----------------

        return redirect(url_for('home'))

    return render_template("signup.html", msg=msg, user=user)


@app.route("/login", methods=["GET", "POST"])
def login():

    logged_in = False   # rename variable to avoid confusion
    msg = None
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        # Check if user exists
        user = User.query.filter_by(email=email).first()

        if not user:
            msg = "Your email does not exist. Please signup first."
            return render_template("login.html", msg=msg, user=logged_in)

        # If user exists but password does not match
        if user.password != password:
            msg = "Incorrect password. Please try again."
            return render_template("login.html", msg=msg, user=logged_in)

        # If correct -> mark logged in
        logged_in = True

        # --- ADD SESSION ---
        session["user_id"] = user.id
        session["email"] = user.email
        # -----------------

        return render_template("home.html", user=logged_in)

    return render_template("login.html", msg=msg, user=logged_in)

@app.route('/mutualfunds')
def mutualfunds():
  return render_template('mutualfunds.html')

fund_news = {
    'Aditya':'https://www.moneycontrol.com/mutual-funds/nav/aditya-birla-sun-life-banking-psu-debt-fund-direct-plan-md-/MBS906#google_vignette',
    'Canara':'https://www.angelone.in/news/mutual-funds/canara-robeco-large-cap-fund-delivers-over-6x-returns-in-15-years',
    'Invesco':'https://economictimes.indiatimes.com/invesco-india-largecap-fund-direct-plan/mffactsheet/schemeid-16712.cms?from=mdr',
    'SBI':'https://economictimes.indiatimes.com/defaultinterstitial.cms',
    'DSP':'https://economictimes.indiatimes.com/dsp-large-cap-fund-direct-plan/mffactsheet/schemeid-16456.cms?from=mdr',
    'ICICI':'https://economictimes.indiatimes.com/icici-prudential-large-mid-cap-fund/mffactsheet/schemeid-534.cms?from=mdr'
}
@app.route('/mutualfunds/<fund_name>')
def fundanalysis(fund_name):

    result = process_mutual_fund(fund_name)

    return render_template(
        'fundanalysis.html',
        fund_name=fund_name,
        first_word=result["first_word"],
        fig_html=result["fig_html"],
        total_return=round(result["total_return"], 2) if result["total_return"] is not None else None,
        return_summary={k: (round(v, 2) if v is not None else None)
                        for k, v in result["return_summary"].items()},
        news=result["news"]
    )


@app.route('/personalizedadvice', methods=["GET", "POST"])
def personalizedadvice():
    gold=None
    filtered_names = None
    filtered_mutualfundsnames = None   # Initialize here ✅

    if request.method == "POST":
        amount = request.form.get('investment_amount')
        duration = request.form.get('investment_duration')
        risk_tolerance = request.form.get('risk_tolerance')
        assets = request.form.getlist('assets')

        stock = pd.read_csv('dataset/personaladvice/Stock.csv')
        mutualfund = pd.read_csv('dataset/personaladvice/MutualFunds.csv')

        # Strip whitespace from column names
        stock.columns = stock.columns.str.strip()
        mutualfund.columns = mutualfund.columns.str.strip()

        # Example filter
        # Stock
        if amount == 'low' and duration == 'short_term' and risk_tolerance == 'low':
            filtered = stock[
                (stock["Amount"] == "low") &
                (stock["duration"] == "short") &
                (stock["Risk tolerence"] == "low")
            ]

            if not filtered.empty:
                filtered_names = filtered["name"].tolist()  # <-- only names
            # Mutual Funds
            filtered_mutualfunds = mutualfund[
                (mutualfund["Amount"] == "low") &
                (mutualfund["duration"] == "short") &
                (mutualfund["Risk tolerence"] == "low")
            ]

            if not filtered_mutualfunds.empty:
                filtered_mutualfundsnames = filtered_mutualfunds["name"].tolist()  # <-- only names
            #Gold
            gold=['Gold']

        # Debug
        print("Amount:", amount, "Duration:", duration, "Risk:", risk_tolerance, "Assets:", assets)

    return render_template(
        'personalizedadvice.html',
        filtered=filtered_names,
        filtered_mutualfundsnames=filtered_mutualfundsnames,
        gold=gold
    )


# return {
#         'graph_div': graph_div,
#         'future_graph_div': future_graph_div,
#         'return_percentage': return_percentage,
#         'advice': advice,
#         'link': link,
#         'location': location,
#         'prices':prices1
#     }




# def index(company):
#     table_data = None
#     fig_html = None
#     error = None

    # --- Start of Ticker Lookup Logic ---
    # Try to find the company's scrip code from the data_df
    # The 'company' variable from the URL path will be the stock symbol (e.g., RELIANCE)
    # We need to ensure that 'company' from URL actually exists in our CSV data.

    # First, try to match directly with 'Scrip' column (for cases like "RELIANCE" coming from most_active)
    # If not found, try to match with 'Company Name' column (if you were linking from a list of full names)

    # Assuming 'company' from the URL is the 'Scrip' code for simplicity,
    # as it's the case for 'Most Active Stocks' links from search.html.
    # If the 'company' in the URL could be the full 'Company Name',
    # you'd need more robust lookup logic here.

    # Lookup the 'Scrip' (ticker code) in your data_df based on the 'company' value from the URL
    # We'll assume the 'company' in the URL is the 'Scrip' itself for direct lookup.
    # If the URL `company` parameter were the full company name, you'd need to adjust.

    # ticker_row = data_df[data_df['Scrip'] == company]  # Find row where 'Scrip' column matches the 'company' from URL
    #
    # if not ticker_row.empty:
    #     # If a match is found, take the 'Scrip' value and append '.NS'
    #     # .iloc[0] is used to get the first (and likely only) matching row
    #     ticker = ticker_row['Scrip'].iloc[0] + '.NS'
    # else:
    #     # If the 'company' from the URL doesn't match any 'Scrip' in your CSV,
    #     # it might be an invalid URL or a company name instead of a scrip.
    #     # For now, we'll set an error and stop processing.
    #     error = f"Stock symbol '{company}' not found in our records. Please select a valid company."
    #     return render_template('graph.html', company=company, table_data=table_data,
    #                            fig_html=fig_html, error=error,
    #                            start_date_display=datetime.now().strftime('%Y/%m/%d'),
    #                            end_date_display=(datetime.now() - timedelta(days=365)).strftime('%Y/%m/%d'))
    # # --- End of Ticker Lookup Logic ---
    #
    # # Set default dates for GET requests or if dates are not provided in POST
    # end_date_obj = datetime.now()
    # start_date_obj = end_date_obj - timedelta(days=365)  # One year ago
    #
    # start_date_str_display = start_date_obj.strftime('%Y/%m/%d')
    # end_date_str_display = end_date_obj.strftime('%Y/%m/%d')
    #
    # if request.method == 'POST':
    #     start_date_str = request.form.get('start_date')
    #     end_date_str = request.form.get('end_date')
    #
    #     try:
    #         # Validate and parse dates from form
    #         start_date_obj = datetime.strptime(start_date_str, '%Y/%m/%d')
    #         end_date_obj = datetime.strptime(end_date_str, '%Y/%m/%d')
    #
    #         start_date = start_date_obj.strftime('%Y-%m-%d')
    #         end_date = end_date_obj.strftime('%Y-%m-%d')
    #
    #     except ValueError as ve:
    #         error = f"Date format error: {ve}. Please use YYYY/MM/DD."
    #         return render_template('graph.html', company=company, table_data=table_data,
    #                                fig_html=fig_html, error=error,
    #                                start_date_display=start_date_str_display,
    #                                end_date_display=end_date_str_display)
    # else:  # This is a GET request
    #     start_date = start_date_obj.strftime('%Y-%m-%d')
    #     end_date = end_date_obj.strftime('%Y-%m-%d')
    #
    # try:
    #     ticker_obj = yf.Ticker(ticker)
    #     info = ticker_obj.info
    #     currency = info.get('currency', None)
    #
    #     if currency != 'INR':
    #         error = "Ticker is not in INR. Please enter a valid NSE stock ticker."
    #     else:
    #         data = yf.download(ticker, start=start_date, end=end_date)
    #
    #         if not data.empty:
    #             data.reset_index(inplace=True)
    #             data['Date'] = pd.to_datetime(data['Date'])
    #             table_data = data.to_html(classes='table table-striped', index=False)
    #
    #             if 'High' in data.columns:
    #                 fig = px.line(data, x='Date', y='High', title=f'{company} High Prices Over Time')
    #                 fig_html = fig.to_html(full_html=False)
    #             else:
    #                 error = f"Error: 'High' price data not found for {company}."
    #         else:
    #             error = "No data found for the given date range."
    #
    # except Exception as e:
    #     error = f"Error fetching data: {e}"
    #
    # return render_template('graph.html', company=company, table_data=table_data,
    #                        fig_html=fig_html, error=error,
    #                        start_date_display=start_date_str_display,
    #                        end_date_display=end_date_str_display)

if __name__ == '__main__':

    app.run(debug=True)