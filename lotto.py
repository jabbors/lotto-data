import os
import os.path
import random
import sqlite3
import http.client, urllib

class lotto:
    def __init__(self):
        self.conn = None
        self.databaseValid = False
        db = os.path.dirname(os.path.realpath(__file__))+'/lotto.db'
        if os.path.isfile(db):
            self.conn = sqlite3.connect(db)
            self.cursor = self.conn.cursor()
            if self.checkDatabaseTables():
                self.databaseValid = True

    def __del__(self):
        if self.conn:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()

    def checkDatabaseTables(self):
        if self.tableExists('lotto_numbers') == False:
            return False
        if self.tableExists('lotto_topten') == False:
            return False
        if self.tableExists('lotto_combinations') == False:
            return False
        if self.tableExists('lotto_generated') == False:
            return False
        if self.tableExists('lotto_genstat') == False:
            return False
        return True

    def tableExists(self, tableName):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tableName,))
        result = self.cursor.fetchone()
        if len(result) != 1:
            print(f'Error: database table {tableName} does not exist')
            return False
        return True

    def getLastInsertId(self):
        self.cursor.execute("SELECT LAST_INSERT_ROWID()")
        result = self.cursor.fetchone()
        if result == None:
            return 0
        return result[0]

    def toIntegers(self, lista):
        listb = []
        for a in lista:
            if isinstance(a, str):
                listb.append(int(a))
            else:
                listb.append(a)
        return listb

    def rowExists(self, date, week, numbers, extra):
        if self.databaseValid == False:
            return None

        self.cursor.execute("SELECT * FROM lotto_numbers WHERE date = ? and round = ?", (date, week))
        rows = self.cursor.fetchall()
        if len(rows) > 0:
            print(f'Warning: row already exists for date {date} and round {week}')
            return True
        return False

    def insertLottoResult(self, date, week, numbers, extra):
        print('Info: inserting row', date, week, numbers, extra)
        if self.databaseValid == False:
            return
        if len(numbers) != 7:
            return
        if len(extra) != 1:
            return

        numbers = self.toIntegers(numbers)
        extra = self.toIntegers(extra)

        if self.rowExists(date, week, numbers, extra):
            return

        data = (date, week, numbers[0], numbers[1], numbers[2], numbers[3], numbers[4], numbers[5], numbers[6], extra[0])
        self.cursor.execute("INSERT INTO lotto_numbers (date,round,n1,n2,n3,n4,n5,n6,n7,e1) VALUES (?,?,?,?,?,?,?,?,?,?)", data)
        self.notifySuccessfulImport(date, week, numbers, extra)

    def notifySuccessfulImport(self, date, week, numbers, extra):
        if self.getLastInsertId() == 0:
            return
        if os.getenv('PUSHOVER_APP_TOKEN') is None:
            print('Warning: PUSHOVER_APP_TOKEN not defined, ignoring pushing notification!')
            return
        if os.getenv('PUSHOVER_USER_KEY') is None:
            print('Warning: PUSHOVER_USER_KEY not defined, ignoring pushing notification!')
            return
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
        urllib.parse.urlencode({
            "token": os.getenv('PUSHOVER_APP_TOKEN'),
            "user": os.getenv('PUSHOVER_USER_KEY'),
            "title": "New lotto row imported for %s" % (date),
            "message": "%s: %s + %s" % (week, ",".join([str(int) for int in numbers]), ",".join([str(int) for int in extra])),
        }), { "Content-type": "application/x-www-form-urlencoded" })
        conn.getresponse()


    '''
	methods for updating top-ten stats
	'''

    def updateTopTen(self, year=None):
        if self.databaseValid == False:
            return

        if year == None:
            print(f'Info: updating top 10 stats...')
            for i in range(1, 41):
                query = "UPDATE lotto_topten SET i%d = (SELECT SUM(i%d) FROM lotto_topten WHERE year != 0) WHERE year = 0" % (i,i)
                self.cursor.execute(query)
            return

        print(f'Info: updating {year} top 10 stats...')
        # check if row for year exists
        self.cursor.execute("SELECT * FROM lotto_topten WHERE year = ?", (year,))
        rows = self.cursor.fetchall()
        if len(rows) == 0:
            # insert new empty row for year
            self.cursor.execute("INSERT INTO lotto_topten (year) VALUES (?)", (year,))

        start = str(year) + '-01-01'
        end = str(year) + '-12-31'
        for i in range(1, 41):
            query = "UPDATE lotto_topten SET i%d = (SELECT COUNT(*) FROM lotto_numbers WHERE date >= '%s' AND date <= '%s' AND (n1 = %d OR n2 = %d OR n3 = %d OR n4 = %d OR n5 = %d OR n6 = %d OR n7 = %d OR e1 = %d OR e2 = %d OR e3 = %d OR e4 = %d)) WHERE year = %d" % (i, start, end, i, i, i, i, i, i, i, i, i, i, i, year)
            self.cursor.execute(query)

    '''
	methods for updating combinations stats
	'''

    def xuniqueCombinations(self, items, n):
        """ returns a list of unique combinations """
        if n == 0:
            yield []
        else:
            for i in range(len(items)):
                for cc in self.xuniqueCombinations(items[i + 1:], n - 1):
                    yield [items[i]] + cc

    def calculateCombinationFrequency(self, ucs):
        frequencyMap = {}
        for us in ucs:
            key = ','.join(str(x) for x in us)
            if key in frequencyMap:
                frequency = frequencyMap[key]
                frequencyMap[key] = frequency + 1
            else:
                frequencyMap[key] = 1
        return frequencyMap

    def insertCombinations(self, size, frequencyMap):
        for key in frequencyMap:
            n = key.split(',')
            if len(n) != size:
                continue
            match size:
                case 7:
                    query = "INSERT INTO lotto_combinations (size,frequency,n1,n2,n3,n4,n5,n6,n7) VALUES(?,?,?,?,?,?,?,?,?)"
                case 6:
                    query = "INSERT INTO lotto_combinations (size,frequency,n1,n2,n3,n4,n5,n6) VALUES(?,?,?,?,?,?,?,?)"
                case 5:
                    query = "INSERT INTO lotto_combinations (size,frequency,n1,n2,n3,n4,n5) VALUES(?,?,?,?,?,?,?)"
                case 4:
                    query = "INSERT INTO lotto_combinations (size,frequency,n1,n2,n3,n4) VALUES(?,?,?,?,?,?)"
                case 3:
                    query = "INSERT INTO lotto_combinations (size,frequency,n1,n2,n3) VALUES(?,?,?,?,?)"
            data = [size, frequencyMap[key]] + n
            self.cursor.execute(query, data)

    def updateCombinations(self):
        if self.databaseValid == False:
            return

        print('Info: updating number combination stats...')
        # clear table
        self.cursor.execute("DELETE FROM lotto_combinations")

        # get lotto results
        self.cursor.execute("SELECT n1,n2,n3,n4,n5,n6,n7 FROM lotto_numbers WHERE date >= '1987-01-01'")
        rows = self.cursor.fetchall()

        """
		combinations of 7 numbers
		"""
        size = 7
        ucs = []
        print('Info: updating combinations for 7 numbers')
        # loop through each row and create unique combinations of each row
        for row in rows:
            numbers = [row[0], row[1], row[2], row[3], row[4], row[5], row[6]]
            for uc in self.xuniqueCombinations(numbers, size):
                ucs.append(uc)

        # calculate frequency
        frequencies = self.calculateCombinationFrequency(ucs)
        # update database
        self.insertCombinations(size, frequencies)

        """
		combinations of 6 numbers
		"""
        print('Info: updating combinations for 6 numbers')
        size = 6
        ucs = []
        # loop through each row and create unique combinations of each row
        for row in rows:
            numbers = [row[0], row[1], row[2], row[3], row[4], row[5], row[6]]
            for uc in self.xuniqueCombinations(numbers, size):
                ucs.append(uc)

        # calculate frequency
        frequencies = self.calculateCombinationFrequency(ucs)
        # update database
        self.insertCombinations(size, frequencies)

        """
		combinations of 5 numbers
		"""
        print('Info: updating combinations for 5 numbers')
        size = 5
        ucs = []
        # loop through each row and create unique combinations of each row
        for row in rows:
            numbers = [row[0], row[1], row[2], row[3], row[4], row[5], row[6]]
            for uc in self.xuniqueCombinations(numbers, size):
                ucs.append(uc)

        # calculate frequency
        frequencies = self.calculateCombinationFrequency(ucs)
        # update database
        self.insertCombinations(size, frequencies)

        """
		combinations of 4 numbers
		"""
        print('Info: updating combinations for 4 numbers')
        size = 4
        ucs = []
        # loop through each row and create unique combinations of each row
        for row in rows:
            numbers = [row[0], row[1], row[2], row[3], row[4], row[5], row[6]]
            for uc in self.xuniqueCombinations(numbers, size):
                ucs.append(uc)

        # calculate frequency
        frequencies = self.calculateCombinationFrequency(ucs)
        # update database
        self.insertCombinations(size, frequencies)

        """
		combinations of 3 numbers
		"""
        print('Info: updating combinations for 3 numbers')
        size = 3
        ucs = []
        # loop through each row and create unique combinations of each row
        for row in rows:
            numbers = [row[0], row[1], row[2], row[3], row[4], row[5], row[6]]
            for uc in self.xuniqueCombinations(numbers, size):
                ucs.append(uc)

        # calculate frequency
        frequencies = self.calculateCombinationFrequency(ucs)
        # update database
        self.insertCombinations(size, frequencies)

    '''
	methods for generating new numbers
	'''

    def matchNumbers(self, a, b):
        """ returns the length of the intersection of two lists """
        return len(list(set(a) & set(b)))

    def isWinning(self, numbers, results):
        """ returns true if numbers has been a winning row """
        for result in results:
            dbnumbers = [result[0], result[1], result[2],
                         result[3], result[4], result[5], result[6]]
            if self.matchNumbers(numbers, dbnumbers) > 4:
                return True
        return False

    def inGenerated(self, numbers, rows):
        """ returns true if numbers already have been generated """
        if numbers in rows:
            return True
        return False

    def onlyDates(self, numbers):
        """ returns false if at least on number is greater than 31 """
        l = [n for n in numbers if n > 31]
        if len(l) > 0:
            return False
        return True

    def onlyEvenNumbers(self, numbers):
        """ returns true if all numbers are even """
        l = [n for n in numbers if n % 2 == 0]
        if len(l) != len(numbers):
            return False
        return True

    def onlyOddNumbers(self, numbers):
        """ returns true if all numbers are odd """
        l = [n for n in numbers if n % 2 == 1]
        if len(l) != len(numbers):
            return False
        return True

    def generateRow(self):
        """ returns a sorted list containg 7 unique random numbers between 1 and 40 of mixed parity where at least one number is greater that 31 """
        rows = []
        while len(rows) < 1:
            numbers = []
            while len(numbers) < 7:
                n = random.randint(1, 40)
                if n not in numbers:
                    numbers.append(n)
            if self.onlyDates(numbers):
                continue
            if self.onlyEvenNumbers(numbers):
                continue
            if self.onlyOddNumbers(numbers):
                continue
            numbers.sort()
            rows.append(numbers)
        return rows[0]

    def generateRows(self):
        print('Info: generating new rows...')
        if self.databaseValid == False:
            return

        # clear table
        self.cursor.execute("DELETE FROM lotto_generated")

        # get lotto results
        self.cursor.execute("SELECT n1,n2,n3,n4,n5,n6,n7 FROM lotto_numbers WHERE date >= '1987-01-01'")
        results = self.cursor.fetchall()

        # generate 1000 rows
        rows = []
        printed = False
        while len(rows) < 1000:
            row = self.generateRow()
            if not self.isWinning(row, results) and not self.inGenerated(row, rows):
                rows.append(row)
                printed = False
            if len(rows) > 0 and len(rows) % 100 == 0:
                if not printed:
                    printed = True
                    print(f'Info: {len(rows)} rows generated')

        # insert rows
        index = 1
        for row in rows:
            data = [index] + row
            self.cursor.execute("INSERT INTO lotto_generated (id,n1,n2,n3,n4,n5,n6,n7) VALUES(?,?,?,?,?,?,?,?)", data)
            index += 1

    '''
	methods for updating generated rows stats
	'''

    def updateGeneratedRowsStats(self):
        print('Info: updating generated rows stats...')
        # get id for latest inserted lotto row
        rowId = self.getLastInsertId()

        # get numbers for latest loot row
        self.cursor.execute("SELECT n1,n2,n3,n4,n5,n6,n7,e1,e2,e3 FROM lotto_numbers WHERE id = ?", (rowId,))
        result = self.cursor.fetchone()

        # get generated rows
        self.cursor.execute("SELECT n1,n2,n3,n4,n5,n6,n7 FROM lotto_generated")
        rows = self.cursor.fetchall()

        stats = [0 for i in range(0, 17)]
        '''
		list containing quantities of matching categories, i.e.
		stats[0] represents the quantity where zero matches are found
		stats[3] represents the quantity where three matches are found

		categories are:
			0 => zero
			1 => one
			2 => two
			3 => three
			4 => four
			5 => five
			6 => six
			7 => six plus one
			8 => seven
			9 => three plus one
			10 => three plus two
			11 => three plus three
			12 => four plus one
			13 => four plus two
			14 => four plus three
			15 => five plus one
			16 => five plus two
		'''

        for row in rows:
            match_n = self.matchNumbers(result[0:7], row)
            match_e = self.matchNumbers(result[7:9], row)
            if (match_n == 7):
                stats[8] += 1
            elif (match_n == 6 and match_e >= 1):
                stats[7] += 1
            elif (match_n == 6):
                stats[6] += 1
            elif (match_n == 5 and match_e == 2):
                stats[16] += 1
            elif (match_n == 5 and match_e == 1):
                stats[15] += 1
            elif (match_n == 5):
                stats[5] += 1
            elif (match_n == 4 and match_e == 2):
                stats[13] += 1
            elif (match_n == 4 and match_e == 1):
                stats[12] += 1
            elif (match_n == 4):
                stats[4] += 1
            elif (match_n == 3 and match_e == 2):
                stats[10] += 1
            elif (match_n == 3 and match_e == 1):
                stats[9] += 1
            elif (match_n == 3):
                stats[3] += 1
            elif (match_n == 2):
                stats[2] += 1
            elif (match_n == 1):
                stats[1] += 1
            elif (match_n == 0):
                stats[0] += 1

        data = (rowId, stats[0], stats[1], stats[2], stats[3], stats[4], stats[5], stats[6], stats[7], stats[8], stats[9], stats[10], stats[12], stats[13], stats[15], stats[16])
        self.cursor.execute("INSERT INTO lotto_genstat (lotto_numbers_id,c0,c1,c2,c3,c4,c5,c6,c6p1,c7,c3p1,c3p2,c4p1,c4p2,c5p1,c5p2) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", data)
