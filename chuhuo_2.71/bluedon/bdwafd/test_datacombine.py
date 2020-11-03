from helperforabanalyse import dict_combine
a={'www.test1.com_172.16.2.52': {'traffic': 80507, 'number': 371}}


b={'www.test1.com_172.16.2.52': {'traffic': 15407, 'number': 71}}

print a

print b


e=dict_combine(a, b)

print e
