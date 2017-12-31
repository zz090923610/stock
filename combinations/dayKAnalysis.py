import sys

from analysis.script_executor.merge_data import DataMerger
from analysis.script_executor.parser import engine
from analysis.script_executor.statistics import ConditionalStatisticsHdl
from analysis.script_executor.summary import summary_all, calc_score, calc_score_vol_ratio
from tools.fetch_day_level_quotes_china import *
from tools.internal_func_entry import update_symbol_list

if __name__ == '__main__':
    # update_symbol_list()
    # a = DayLevelQuoteUpdaterTushare()
    # TODO specify better start date
    # a.get_data_all_stock(start='2001-01-01', end=sys.argv[1])
    engine('./scripts/inflow.txt')
    engine('./scripts/ma.txt')
    engine('./scripts/candle_stick_shape_analysis.txt')
    summary_all(sys.argv[1], '~/' + sys.argv[1] + ".csv")

    #engine('./scripts/short_period_buypoint.txt')
    #b = DataMerger("ma candle_stick_shape_analysis spb", "merged", "date")
    #b.collect_symbols()
    #b.merge_all()
    #c = ConditionalStatisticsHdl(
    #    "QUICK_BUYPOINT|CROSS QUICK_BUYPOINT|TSHAPE QUICK_BUYPOINT|REVERSETSHAPE QUICK_BUYPOINT|JUMPHIGHOPEN QUICK_BUYPOINT|JUMPLOWOPEN QUICK_BUYPOINT|MORNINGCROSS QUICK_BUYPOINT|MORNINGSTAR QUICK_BUYPOINT|FRIENDLYFIRE QUICK_BUYPOINT|HOPEOFDAWN QUICK_BUYPOINT|RAISINGSUN QUICK_BUYPOINT|REVERSEHAMMER QUICK_BUYPOINT|HAMMER QUICK_BUYPOINT|FLATFLOOR QUICK_BUYPOINT|CONTINUETHREEJUMPYIN QUICK_BUYPOINT|TRIPLEREDARMY QUICK_BUYPOINT|UPWARDTWOSTARS QUICK_BUYPOINT|JUMPUPWARD QUICK_BUYPOINT|JUMPUPWARDYANG QUICK_BUYPOINT|JUMPDOWNWARDTHREESTARS QUICK_BUYPOINT|TRIPLEUPWARDS QUICK_BUYPOINT|TWOREDONEBLACK QUICK_BUYPOINT|TWILICROSS QUICK_BUYPOINT|TWILISTAR QUICK_BUYPOINT|FRIENDLYPUSHBACK QUICK_BUYPOINT|INCOMINGCLOUDS QUICK_BUYPOINT|HEAVYRAIN QUICK_BUYPOINT|SHOOTINGSTAR QUICK_BUYPOINT|HANGWIRE QUICK_BUYPOINT|FLATROOF QUICK_BUYPOINT|DOUBLECROWS QUICK_BUYPOINT|TRIPLECROWS QUICK_BUYPOINT|HEADSFEETYIN QUICK_BUYPOINT|HEADSFEETYANG QUICK_BUYPOINT|DOWNWARDCOVER QUICK_BUYPOINT|TRIPLEBLKARMY QUICK_BUYPOINT|MILDDOWNWARDS QUICK_BUYPOINT|RUSHINGAWAY QUICK_BUYPOINT|DOWNWARDTRIPLESTARS QUICK_BUYPOINT|DOWNWARDTRIPLESWANS QUICK_BUYPOINT|TRIPLEDOWNWARDSYANG QUICK_BUYPOINT|JUMPHIGHTRIPLEYANG QUICK_BUYPOINT|UPWARDRESISTENCE QUICK_BUYPOINT|UPWARDPAUSE QUICK_BUYPOINT|LAMPYANG QUICK_BUYPOINT|BLKREDBLK QUICK_BUYPOINT|LONGCROSS QUICK_BUYPOINT|PROPELLER QUICK_BUYPOINT|EOFUPWARD QUICK_BUYPOINT|EOFDOWNWARD QUICK_BUYPOINT|PREGNANTYANG QUICK_BUYPOINT|PREGNANTYIN QUICK_BUYPOINT|MAALIGNUPWARD QUICK_BUYPOINT|MAALIGNDOWNWARD QUICK_BUYPOINT|GOLDCROSS510 QUICK_BUYPOINT|GOLDCROSS520 QUICK_BUYPOINT|GOLDCROSS1020 QUICK_BUYPOINT|LOSECROSS510 QUICK_BUYPOINT|LOSECROSS520 QUICK_BUYPOINT|LOSECROSS1020 QUICK_BUYPOINT|GOLDVALLEY QUICK_BUYPOINT|LOSEVALLEY QUICK_BUYPOINT|DRAGONOUT QUICK_BUYPOINT|LOSEEVERYTHING",
    #    "merged")
    #c.statistic()

    #d = ConditionalStatisticsHdl(
    #    "QUICK_SELLPOINT|CROSS QUICK_SELLPOINT|TSHAPE QUICK_SELLPOINT|REVERSETSHAPE QUICK_SELLPOINT|JUMPHIGHOPEN QUICK_SELLPOINT|JUMPLOWOPEN QUICK_SELLPOINT|MORNINGCROSS QUICK_SELLPOINT|MORNINGSTAR QUICK_SELLPOINT|FRIENDLYFIRE QUICK_SELLPOINT|HOPEOFDAWN QUICK_SELLPOINT|RAISINGSUN QUICK_SELLPOINT|REVERSEHAMMER QUICK_SELLPOINT|HAMMER QUICK_SELLPOINT|FLATFLOOR QUICK_SELLPOINT|CONTINUETHREEJUMPYIN QUICK_SELLPOINT|TRIPLEREDARMY QUICK_SELLPOINT|UPWARDTWOSTARS QUICK_SELLPOINT|JUMPUPWARD QUICK_SELLPOINT|JUMPUPWARDYANG QUICK_SELLPOINT|JUMPDOWNWARDTHREESTARS QUICK_SELLPOINT|TRIPLEUPWARDS QUICK_SELLPOINT|TWOREDONEBLACK QUICK_SELLPOINT|TWILICROSS QUICK_SELLPOINT|TWILISTAR QUICK_SELLPOINT|FRIENDLYPUSHBACK QUICK_SELLPOINT|INCOMINGCLOUDS QUICK_SELLPOINT|HEAVYRAIN QUICK_SELLPOINT|SHOOTINGSTAR QUICK_SELLPOINT|HANGWIRE QUICK_SELLPOINT|FLATROOF QUICK_SELLPOINT|DOUBLECROWS QUICK_SELLPOINT|TRIPLECROWS QUICK_SELLPOINT|HEADSFEETYIN QUICK_SELLPOINT|HEADSFEETYANG QUICK_SELLPOINT|DOWNWARDCOVER QUICK_SELLPOINT|TRIPLEBLKARMY QUICK_SELLPOINT|MILDDOWNWARDS QUICK_SELLPOINT|RUSHINGAWAY QUICK_SELLPOINT|DOWNWARDTRIPLESTARS QUICK_SELLPOINT|DOWNWARDTRIPLESWANS QUICK_SELLPOINT|TRIPLEDOWNWARDSYANG QUICK_SELLPOINT|JUMPHIGHTRIPLEYANG QUICK_SELLPOINT|UPWARDRESISTENCE QUICK_SELLPOINT|UPWARDPAUSE QUICK_SELLPOINT|LAMPYANG QUICK_SELLPOINT|BLKREDBLK QUICK_SELLPOINT|LONGCROSS QUICK_SELLPOINT|PROPELLER QUICK_SELLPOINT|EOFUPWARD QUICK_SELLPOINT|EOFDOWNWARD QUICK_SELLPOINT|PREGNANTYANG QUICK_SELLPOINT|PREGNANTYIN QUICK_SELLPOINT|MAALIGNUPWARD QUICK_SELLPOINT|MAALIGNDOWNWARD QUICK_SELLPOINT|GOLDCROSS510 QUICK_SELLPOINT|GOLDCROSS520 QUICK_SELLPOINT|GOLDCROSS1020 QUICK_SELLPOINT|LOSECROSS510 QUICK_SELLPOINT|LOSECROSS520 QUICK_SELLPOINT|LOSECROSS1020 QUICK_SELLPOINT|GOLDVALLEY QUICK_SELLPOINT|LOSEVALLEY QUICK_SELLPOINT|DRAGONOUT QUICK_SELLPOINT|LOSEEVERYTHING",
    #    "merged")
    #d.statistic()

    # calc_score(sys.argv[1], '~/' + sys.argv[1] + "_score_turnover.csv")
    # calc_score_vol_ratio(sys.argv[1], '~/' + sys.argv[1] + "_score_vol_ratio.csv")
    # dates = ['2017-11-01', '2017-11-02', '2017-11-03', '2017-11-06', '2017-11-07', '2017-11-08', '2017-11-09', '2017-11-10', '2017-11-13', '2017-11-14', '2017-11-15', '2017-11-16', '2017-11-17', '2017-11-20', '2017-11-21', '2017-11-22', '2017-11-23', '2017-11-24', '2017-11-27', '2017-11-28', '2017-11-29', '2017-11-30', '2017-12-01', '2017-12-04', '2017-12-05', '2017-12-06', '2017-12-07', '2017-12-08', '2017-12-11', '2017-12-12', '2017-12-13', '2017-12-14', '2017-12-15', '2017-12-18', '2017-12-19', '2017-12-20', '2017-12-21', '2017-12-22', '2017-12-25', '2017-12-26', '2017-12-27', '2017-12-28']
    # for d in dates:
    #     print(d)
    #     calc_score(d, '~/' + d + "_score.csv")