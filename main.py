from wordfreq import word_frequency

words_only = []

with open("word_list.txt", "r") as word_list:
    word_list.readline()
    for word in word_list:
        parts = word.strip().split(".")
        words_only.append(parts[1])    

word_freq_list = []
for word in words_only:
    freq = word_frequency(word, 'en', wordlist='best', minimum=0.0)
    word_freq_list.append((word, freq))
print(word_freq_list)