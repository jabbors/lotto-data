from lotto import lotto

l = lotto()

dateNumbers = [1, 5, 10, 15, 20, 30, 31]
noDateNumbers = [1, 5, 10, 15, 20, 30, 32]
evenNumbers = [2, 4, 6, 8, 10, 12, 14]
oddNumbers = [3, 5, 7, 9, 11, 13, 15]
mixedNumbers = [2, 5, 6, 9, 10, 13, 14]

assert l.onlyDates(dateNumbers) == True, "input with numbers smaller than 31 should be True"
assert l.onlyDates(noDateNumbers) == False, "input with one number greater than 31 should be False"
assert l.onlyEvenNumbers(evenNumbers) == True, "input with only even numbers should be True"
assert l.onlyEvenNumbers(oddNumbers) == False, "input with only odd numbers should be False"
assert l.onlyEvenNumbers(mixedNumbers) == False, "input with mixed numbers should be False"
assert l.onlyOddNumbers(oddNumbers) == True, "input with only odd numbers should be True"
assert l.onlyOddNumbers(evenNumbers) == False, "input with only even numbers should be False"
assert l.onlyOddNumbers(mixedNumbers) == False, "input with mixed numbers should be False"

generatedRow = l.generateRow()
assert l.onlyDates(generatedRow) == False
assert l.onlyEvenNumbers(generatedRow) == False
assert l.onlyOddNumbers(generatedRow) == False
