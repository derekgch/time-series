import warnings
import more_itertools
import itertools
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import pylab
warnings.filterwarnings("ignore")
plt.style.use('fivethirtyeight')
import pandas as pd
import statsmodels.api as sm
import matplotlib
from pylab import rcParams

# from fbprophet import Prophet

matplotlib.rcParams['axes.labelsize'] = 14
matplotlib.rcParams['xtick.labelsize'] = 12
matplotlib.rcParams['ytick.labelsize'] = 12
matplotlib.rcParams['text.color'] = 'k'


df = pd.read_excel("Superstore.xls")
furniture = df.loc[df['Category'] == 'Furniture']

furniture['Order Date'].min(), furniture['Order Date'].max()

cols = ['Row ID', 'Order ID', 'Ship Date', 'Ship Mode', 'Customer ID', 'Customer Name', 'Segment', 'Country', 'City', 'State', 'Postal Code', 'Region', 'Product ID', 'Category', 'Sub-Category', 'Product Name', 'Quantity', 'Discount', 'Profit']
furniture.drop(cols, axis=1, inplace=True)
furniture = furniture.sort_values('Order Date')

furniture.isnull().sum()
furniture['Order Date'].min()
furniture['Order Date'].max()

furniture = furniture.groupby('Order Date')['Sales'].sum().reset_index()
furniture.head()

furniture = furniture.set_index('Order Date')
furniture.index
y = furniture['Sales'].resample('MS').mean()
y['2017':]

# y.plot(figsize=(15, 6))
# plt.show()

rcParams['figure.figsize'] = 18, 8

decomposition = sm.tsa.seasonal_decompose(y, model='additive')

# fig = decomposition.plot()
# plt.show()
# print( y['2017':] )

p = d = q = range(0, 2)
pdq = list(itertools.product(p, d, q))
seasonal_pdq = [(x[0], x[1], x[2], 12) for x in list(itertools.product(p, d, q))]

# # print('Examples of parameter combinations for Seasonal ARIMA...')
# # print('SARIMAX: {} x {}'.format(pdq[1], seasonal_pdq[1]))
# # print('SARIMAX: {} x {}'.format(pdq[1], seasonal_pdq[2]))
# # print('SARIMAX: {} x {}'.format(pdq[2], seasonal_pdq[3]))
# # print('SARIMAX: {} x {}'.format(pdq[2], seasonal_pdq[4]))


for param in pdq:
    for param_seasonal in seasonal_pdq:
        try:
            mod = sm.tsa.statespace.SARIMAX(y,
                                            order=param,
                                            seasonal_order=param_seasonal,
                                            enforce_stationarity=False,
                                            enforce_invertibility=False)

            results = mod.fit()

            # print('ARIMA{}x{}12 - AIC:{}'.format(param, param_seasonal, results.aic))
        except:
            continue

mod = sm.tsa.statespace.SARIMAX(y,
                                order=(1, 1, 1),
                                seasonal_order=(1, 1, 0, 12),
                                enforce_stationarity=False,
                                enforce_invertibility=False)

# results = mod.fit()

# # print(results.summary().tables[1])

# # results.plot_diagnostics(figsize=(16, 8))
# # plt.show()


pred = results.get_prediction(start=pd.to_datetime('2017-01-01'), dynamic=False)
pred_ci = pred.conf_int()

ax = y['2014':].plot(label='observed')
pred.predicted_mean.plot(ax=ax, label='One-step ahead Forecast', alpha=.7, figsize=(14, 7))

ax.fill_between(pred_ci.index,
                pred_ci.iloc[:, 0],
                pred_ci.iloc[:, 1], color='k', alpha=.2)

ax.set_xlabel('Date')
ax.set_ylabel('Furniture Sales')
plt.legend()

plt.show()

# furniture = furniture.rename(columns={'Order Date': 'ds', 'Sales': 'y'})
# furniture_model = Prophet(interval_width=0.95)
# furniture_model.fit(furniture)

# furniture_forecast = furniture_model.make_future_dataframe(periods=36, freq='MS')
# furniture_forecast = furniture_model.predict(furniture_forecast)

# plt.figure(figsize=(18, 6))
# furniture_model.plot(furniture_forecast, xlabel = 'Date', ylabel = 'Sales')
# plt.title('Furniture Sales')