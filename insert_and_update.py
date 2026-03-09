from lotto import lotto
from parser import parser
import datetime
import sys

l = lotto()

def getYear(date):
    return int(date[0:4])

def getWeek(date):
    year = int(date[0:4])
    month = int(date[5:7])
    day = int(date[8:10])
    return str(datetime.date(year, month, day).isocalendar()[1]) + '-1'

if len(sys.argv) == 2 and sys.argv[1] == 'cron':
    p = parser()
    date = p.getDate()
    if date is None:
        print('Warning: no date, exiting!')
        sys.exit(0)
    year = getYear(date)
    week = getWeek(date)
    n = p.getNumbers()
    e = p.getExtraNumbers()
    if n is None or e is None:
        print('Warning: no numbers, exiting!')
        sys.exit(0)
    l.insertLottoResult(date, week, n, e)
elif len(sys.argv) == 10:
    date = sys.argv[1]
    year = getYear(date)
    week = getWeek(date)
    n = []
    n.append(sys.argv[2])
    n.append(sys.argv[3])
    n.append(sys.argv[4])
    n.append(sys.argv[5])
    n.append(sys.argv[6])
    n.append(sys.argv[7])
    n.append(sys.argv[8])
    e = []
    e.append(sys.argv[9])

    l.insertLottoResult(date, week, n, e)
else:
    print(f'Usage: python {sys.argv[0]} yyyy-mm-dd n1 n2 n3 n4 n5 n6 n7 e1')
    sys.exit(0)


if l.getLastInsertId() == 0:
    print('Warning: no row was inserted, exiting!')
    sys.exit(-1)

#
# generated rows stats
#
l.updateGeneratedRowsStats()

#
# generate new rows
#
l.generateRows()

#
# current year top 10 stats
#
l.updateTopTen(year)

#
# previous year top 10 stats
#
year -= 1
l.updateTopTen(year)

#
# all-time top 10 stats
#
l.updateTopTen()

#
# number combination stats
#
l.updateCombinations()
