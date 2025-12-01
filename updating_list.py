with open("word_list.txt", "r") as word_list:
    word_list.readline()

    words_only = []
    for word in word_list:
        parts = word.strip().split(".")
        words_only.append(parts[1])  
    
    clean_list = []
    seen = set()
    for word in words_only:
        if word not in seen:
            clean_list.append(word)
            seen.add(word)

with open("cleaned_word_list.txt", "w") as cleaned_word_list:
    for word in clean_list:
        cleaned_word_list.write(f"{word}\n")
