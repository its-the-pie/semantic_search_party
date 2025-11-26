from wordfreq import word_frequency
import random 
import spacy  
import en_core_web_md

def get_freq():
    words_only = []
    with open("cleaned_word_list.txt", "r") as word_list:
        word_list.readline()
        for line in word_list:
            word = line.strip()
            words_only.append(word)    

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

def difficulty_score(scaled_freqs):
    max_len = 0
    for freq, word in scaled_freqs:
        if len(word) > max_len:
            max_len = len(word)

    scores = []
    for freq, word in scaled_freqs:
        difficulty = (1 - freq) + (len(word) / max_len)
        scores.append((difficulty, word))
    return scores

def make_bins(scores, num_levels):
    sorted_words = sorted(scores)
    bin_size = len(sorted_words) // num_levels
    bin_dict = {}
    for i in range(num_levels):
        if i == num_levels - 1:
            words_in_bin = sorted_words[i * bin_size:]
        else:
            words_in_bin = sorted_words[i * bin_size : (i + 1) * bin_size]

        word_list = []
        for w in words_in_bin:
            word_list.append(w[1])
        bin_dict[i + 1] = word_list
    return bin_dict

def choose_word(bin_dict, level):
    word = random.choice(bin_dict[level])
    return word

def semantic_similarity(doc1, guess, nlp):
    doc2 = nlp(guess)
    num = doc1.similarity(doc2)
    return num

def play_round(secret_word, nlp):
    doc1 = nlp(secret_word)
    score = 0
    already_guessed = set()

    while True: 
        guess = input("Make a guess: ").lower()
        if guess in already_guessed:
            print("Already guessed")
        else: 
            already_guessed.add(guess)
            score += 1

            if guess == secret_word.lower():
                print(f"Correct! Number of guesses: {score}") 
                return True
            else:
                similarity = semantic_similarity(doc1, guess, nlp)
                if similarity > 0.9999 and guess != secret_word.lower():
                    print("Almost there! That was practically a perfect match!")
                else:        
                    print(f"Similarity: {similarity:.2f}") 
                   
def play_level(level, bins, nlp):
    secret_word = choose_word(bins, level)
    print(secret_word)
    result = play_round(secret_word, nlp)
    return result 

def play_game(num_levels, bins, nlp):
    level = 1
    while level <= num_levels:
        if play_level(level, bins, nlp):
            level += 1    

if __name__ == "__main__":  
    nlp = en_core_web_md.load()
    num_levels = 50
    word_list = get_freq()
    bins = make_bins(difficulty_score(scale(word_list)), num_levels)

    play = True
    while play:
        play_game(num_levels, bins, nlp)

        restart = input("Would you like to play again? (enter y or n):")
        if restart != "y":
            play = False
            print("Bye! Thanks for playing Semantic Search Party")