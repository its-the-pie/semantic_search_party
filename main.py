from wordfreq import word_frequency
import random 


def get_freq():
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
    return word_freq_list

def scale(word_freq_list):
    freqs = []
    for word, freq in word_freq_list:
        freqs.append(freq)

    max_freq = max(freqs)
    min_freq = min(freqs)
    scaled_freqs = []
    for word, freq in word_freq_list:
        scaled_freq = (freq - min_freq) / (max_freq - min_freq)
        scaled_freqs.append((scaled_freq, word))
    return scaled_freqs

def bins(scaled_freqs, num_levels):
    sorted_words = sorted(scaled_freqs, reverse=True)
    bin_size = len(sorted_words) // num_levels
    bins = {}
    for i in range(num_levels):
        if i == num_levels - 1:
            words_in_bin = sorted_words[i * bin_size:]
        else:
            words_in_bin = sorted_words[i * bin_size : (i + 1) * bin_size]

        word_list = []
        for w in words_in_bin:
            word_list.append(w[1])
        bins[i + 1] = word_list
    return bins

def choose_word(bins, level):
    word = random.choice(bins[level])
    return word



if __name__ == "__main__":  
    print(choose_word(bins(scale(get_freq()), 50), 1))
    
