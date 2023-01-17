# Stock Overflow
This project is a variation of the one my friends and I submitted for Treasure Hacks 3.0. While our original project was made with React,
I used Django in this version.

## Current Features
- Stock Tracker Tool
- Asset Rebalance Tool
    - Momentum Investing Strategy
    - Sentiment Analysis Strategy
    - Risk Allocation Strategy
    - Expected Return Strategy

### Current Features Notes
The application does not make trades; it only provides the user with information and suggests management directions given the user's tracked assets.
Due the the 5 call per minute limit of the free tier of the AlphaVantage API, loading may take artificially long. In a production version of the app,
the paid tier would be purchased.

## Future Features
- Backtesting Tool
- Forecasting Tool
    - Monte Carlo Simulation
- Asset Rebalance Tool
    - Sentimental Analysis Strategy
        - Data Update Feature
- Help
 
### Future Features Notes
For strategy performance testing, take the user's favorited assets, and load only the data for these.
This would mean, of course, that the user may only incorporate these in the strategy to be
backtested. However, we are assuming that the user already tracks the assets with which
they plan to center strategies around. For Forecasting Tool, I plan to add a Monte Carlo simulation. Include all of our rebalancing strategies
as presets for the Backtesting and Forecasting Tools. Every time the sentimental analysis tool is run, 
have it check if the time the data was last updated was more than 60 minutes ago, and if this is true,
update the data. Add a "help" feature, which explains how to choose and tracks assets you think are valuable, 
and how to use Stock Overflow's tools to form strategies. Allow the user to upload code,
store it in a database, and associate that strategy with their User. Then, they may use it
in the Rebalance Tool, Backtesting Tool, or Forecasting Tool.

## Execution Instructions
1. Have Python installed on your system.
2. Navigate to the project folder.
3. Activate the virtual environment with:
```
source stockProjectEnv/bin/activate
```
4. Update listed assets list with:
```
python manage.py addsymbols
```
5. Serve the project locally with:
```
python manage.py runserver
```

If you have any questions or would like to collaborate, contact me at sactoa@gmail.com.

