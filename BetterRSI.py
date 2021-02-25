'''
    A better RSI indicator
'''
__author__ = "Alon horesh, Alpha Over Beta"
__credits__ = __author__
__license__ = "free"
__version__ = "0.0.1"
__maintainer__ = __author__
__email__ = "alon@alphaoverbeta.net"
__status__ = "Production"


import copy
import os
import matplotlib.pyplot as plt
import talib
from infrastructure import utility
from strategies.StrategyInterface import StrategyInterface


class better_rsi_indicator:
    def __init__(self, df, timeperiod):
        """
        Initiate class with data and lookback window
        :param df: the historical quotes to work with
        :param timeperiod: the lookback window size of the indicator
        """
        dfc = copy.deepcopy(df)

        dfc['rank'] = 0
        dfc['updown'] = -1
        dfc['base'] = dfc['Close'].shift(timeperiod)
        dfc['base-1'] = dfc['base'].shift(timeperiod)
        dfc.loc[dfc['Close'] > dfc['base'],'updown'] = 1

        # rank by same color
        runs_list=[]
        run_counter=1
        runs_list.append(run_counter)
        inner_run_list=[]
        current_bar = dfc['updown'].iloc[0]
        inner_run_counter = 1
        inner_run_list.append(inner_run_counter)
        for idx in range(1, len(dfc)):
            if dfc['updown'].iloc[idx] != current_bar:
                run_counter +=1
                current_bar=dfc['updown'].iloc[idx]
                inner_run_counter = 1
            runs_list.append(run_counter)
            inner_run_list.append(inner_run_counter)
            inner_run_counter +=1
        dfc['runs']=runs_list
        dfc['inner_runs']=inner_run_list

        last_run_length = dfc['inner_runs'].iloc[-1]
        this_run_df = dfc.iloc[-last_run_length:]
        # analyze last same color run
        for run_idx in range (dfc['runs'].max()-2, 0, -2):
            run_slice = dfc[dfc['runs'] == run_idx]
            if len(run_slice) > 3:
                break

        std = (dfc['base'] - dfc['base-1']).rolling(timeperiod).std()
        dfc['body_rank'] =  (dfc['Close'] - dfc['base'])/std

        # weigted volume
        dfc['weights'] = self.weights(series=dfc['Volume'], timeperiod=timeperiod)

        # price slope
        slope_rank = 0 if len(this_run_df)<2 else talib.LINEARREG_SLOPE(this_run_df['Close'].values, timeperiod=len(this_run_df))[-1]

        #   return current ranking
        dfc['rank'] = dfc['inner_runs'] * dfc['weights'] * dfc['body_rank']
        # dfc['rank'] = dfc['weights'] * dfc['body_rank']

        self.rsi = dfc['rank'].values

    def weights(self, series, timeperiod):
        weights_values= [None]*len(series)
        for idx in range(timeperiod, len(series)):
            slice = series[idx-timeperiod:idx]
            slice_w = [w/slice.sum() for w in slice]
            weights_values[idx] = slice_w[-1]
        return weights_values
