def longRepeat(aString): 
    topDawg = 0
    for character in aString:
        if character != " ":
            currentLetter = aString.count(character)
            if  currentLetter > topDawg: 
                topDawg = currentLetter 
    
    print(topDawg)

longRepeat(input("Please enter a string:  "))