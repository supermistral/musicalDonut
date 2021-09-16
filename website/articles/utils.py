def replaceQuotes(text):
    text_list = list(text)
    flagSingle = True
    flagDouble = True
    n = len(text)

    for i in range(n):
        if (
            text[i] == '"' and 
            (i > 0 and text[i-1] != "=") and
            (i < n-1 and text[i+1] != ">")
        ):
            text_list[i] = '«' if flagDouble else "»"
            flagDouble = not flagDouble
        elif (
            text[i] == "'" and 
            (i > 0 and text[i-1] != "=") and
            (i < n-1 and text[i+1] != ">")
        ):
            text_list[i] = '«' if flagSingle else "»"
            flagSingle = not flagSingle
    
    return "".join(text_list)