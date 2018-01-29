import os

import schedule
import time
# DEPENDENCY( schedule)

def daily_analysis():
    os.system('./daily.sh')


if __name__ == '__main__':
    schedule.every().day.at("03:00").do(daily_analysis)
    while True:

        schedule.run_pending()
        time.sleep(1)