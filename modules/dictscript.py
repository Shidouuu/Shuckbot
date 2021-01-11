import random

with open(r'C:\users\guitar god\documents\python\shuckbot\shuckbot-testing\modules\words_alpha.txt') as words_file:
    word_list = words_file.read().splitlines()


by_length = {}
for word in word_list:
    by_length.setdefault(len(word), []).append(word)

# start with the desired length, and see if there are words this long in the
# dictionary, but don’t presume that all possible lengths exist:
wordlength = 5

# we picked a length, but it could be 0, -1 or -2, so start with an empty word
# and then pick a random word from the list with words of the right length.
word = random.choice(by_length[wordlength])

print(word)