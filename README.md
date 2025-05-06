# Group 4 Final Project: ARK Invest Dashboard 
 Group 4 Members: Christina DePerro, Matt Rock, Andres Gomez Lenero, and Parker Gage 

Welcome to our repository exploring ARK Invest.  This repository’s main objective is to provide an interactive way to explore ARK Invest’s multiple funds.   

## **Included Resources:** 

**ARK Invest Powerpoint** 

O The Powerpoint’s primary focus is to provide background information on the project.  It focuses on what ARK Invest is, a high level overview of the process we followed while developing our tool, and some potential ways to utilize the Streamlit dashboard.  

**Summary Overview** 

O The summary overview is a short two page description that goes into the features and functionality of the python code.  It also explains some of the reasoning behind the decisions we made throughout the project.  

**Python Files** 

O Auto_Download.py – This file is used to scrape the ARK Invest website to compile the most recent .csv files from their website.  You’ll want to run this daily to ensure you have the most robust data to analyze.  

O stock_class.py – This python code creates a class called Stock, which we use to run in our main code.  Stock_class.py is used in conjunction with yfinance to gather historical stock price data for analysis. 

O Streamlit_Group4.py – This is the primary file that users will run to be able to launch the Streamlit interactive dashboard and run their analysis on ARK Invest.   

  

**Get Started:** 

We’d recommend first looking at the slideshow and Summary Overview if you aren’t familiar with ARK Invest.  If, however, you’re ready to get going first run the Auto_Download.py file to gather the most up to date fund information.  This will create a new .csv file where all the historical data will be compiled.  Once you’ve done that you can jump into the Group4_ARK.py file.   

  

## **Additional Resources:** 

[Ark Invest Funds website]( https://www.ark-funds.com/download-fund-materials) 

[Streamlit](https://streamlit.io/playground) 

 