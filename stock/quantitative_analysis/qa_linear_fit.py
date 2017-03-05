from stock.common.common_func import load_stock_for_plot
from scipy.stats import linregress


def get_fitted_data_old(stock, days_of_data, days_to_fit):
    df = load_stock_for_plot(stock, days_of_data)
    df['solid_high'] = df[['open', 'close']].max(axis=1)
    df['solid_low'] = df[['open', 'close']].min(axis=1)
    df = df.reset_index()
    df_fit = df.tail(days_to_fit)
    sh, ih = fit_line1(df_fit.index, df_fit.solid_high)
    sl, il = fit_line1(df_fit.index, df_fit.solid_low)
    df['fitted_high'] = [x * sh + ih if x in df_fit.index else None for x in df.index]
    df['fitted_low'] = [x * sl + il if x in df_fit.index else None for x in df.index]
    return df


def fit_line1(x, y):
    """Return slope, intercept of best fit line."""
    slope, intercept, r, p, stderr = linregress(x, y)
    return slope, intercept  # could also return stderr


def get_fitted_data(stock, days_of_data, days_to_fit, days_extra_to_draw_line):
    df = load_stock_for_plot(stock, days_of_data)
    days_of_data = min(len(df), days_of_data)
    df['solid_high'] = df[['open', 'close']].max(axis=1)
    df['solid_low'] = df[['open', 'close']].min(axis=1)
    df = df.reset_index()
    df = df.drop('index', 1)
    df['candidate_high'] = False
    df['candidate_low'] = False
    for x in range(1, len(df) - 1):
        df.set_value(x, 'candidate_high', True if (df.iloc[x - 1]['solid_high'] < df.iloc[x]['solid_high']) & (
            (df.iloc[x]['solid_high'] >= df.iloc[x + 1]['solid_high'])) else False)
        df.set_value(x, 'candidate_low', True if (df.iloc[x - 1]['solid_low'] >= df.iloc[x]['solid_low']) & (
            (df.iloc[x]['solid_low'] < df.iloc[x + 1]['solid_low'])) else False)
    df_to_fit = df.tail(days_to_fit)

    if len(df_to_fit.loc[df_to_fit['candidate_high'] == True]['solid_high']) == 0:
        for x in df_to_fit.index:
            df_to_fit.set_value(x, 'candidate_high', True)
            df.set_value(x, 'candidate_high', True)

    if len(df_to_fit.loc[df_to_fit['candidate_low'] == True]['solid_low']) == 0:
        for x in df_to_fit.index:
            df_to_fit.set_value(x, 'candidate_low', True)
            df.set_value(x, 'candidate_low', True)

    cand_high_max = max(df_to_fit.loc[df_to_fit['candidate_high'] == True]['solid_high'])
    last_day_high = df_to_fit.loc[days_of_data - 1]['solid_high']
    df_to_fit.set_value(days_of_data - 1, 'candidate_high', True if last_day_high * 1.3 >= cand_high_max else False)
    df.set_value(days_of_data - 1, 'candidate_high', df_to_fit.loc[days_of_data - 1]['candidate_high'])

    cand_low_min = min(df_to_fit.loc[df_to_fit['candidate_low'] == True]['solid_low'])
    last_day_low = df_to_fit.loc[days_of_data - 1]['solid_low']
    df_to_fit.set_value(days_of_data - 1, 'candidate_low', True if last_day_low * 0.7 <= cand_low_min else False)
    df.set_value(days_of_data - 1, 'candidate_low', df_to_fit.loc[days_of_data - 1]['candidate_low'])

    df_high_selected = df_to_fit.loc[df['candidate_high'] == True]
    df_low_selected = df_to_fit.loc[df['candidate_low'] == True]

    k_high, d_high = fit_line1(df_high_selected.index, df_high_selected.solid_high)
    k_low, d_low = fit_line1(df_low_selected.index, df_low_selected.solid_low)

    df['upper_trend'] = None
    df['bottom_trend'] = None
    for x in range(max(0, len(df) - 1 - days_to_fit - days_extra_to_draw_line), len(df)):
        df.set_value(x, 'upper_trend', k_high * x + d_high)
        df.set_value(x, 'bottom_trend', k_low * x + d_low)

    return df
