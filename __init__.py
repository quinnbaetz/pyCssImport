import os, sys, re
#import cow
#Usage python2.5 scss.py file.scss dir/to/put/css/file

#add path to scss in PYTHONPATH, must be relative
def remove_comments(text):
    """ remove c-style comments.
        text: blob of text with comments (can include newlines)
        returns: text with comments removed
    """
    pattern = r"""
                            ##  --------- COMMENT ---------
           /\*              ##  Start of /* ... */ comment
           [^*]*\*+         ##  Non-* followed by 1-or-more *'s
           (                ##
             [^/*][^*]*\*+  ##
           )*               ##  0-or-more things which don't start with /
                            ##    but do end with '*'
           /                ##  End of /* ... */ comment
         |                  ##  -OR-  various things which aren't comments:
           (                ## 
                            ##  ------ " ... " STRING ------
             "              ##  Start of " ... " string
             (              ##
               \\.          ##  Escaped char
             |              ##  -OR-
               [^"\\]       ##  Non "\ characters
             )*             ##
             "              ##  End of " ... " string
           |                ##  -OR-
                            ##
                            ##  ------ ' ... ' STRING ------
             '              ##  Start of ' ... ' string
             (              ##
               \\.          ##  Escaped char
             |              ##  -OR-
               [^'\\]       ##  Non '\ characters
             )*             ##
             '              ##  End of ' ... ' string
           |                ##  -OR-
                            ##
                            ##  ------ ANYTHING ELSE -------
             .              ##  Anything other char
             [^/"'\\]*      ##  Chars which doesn't start a comment, string
           )                ##    or escape
    """
    regex = re.compile(pattern, re.VERBOSE|re.MULTILINE|re.DOTALL)
    noncomments = [m.group(2) for m in regex.finditer(text) if m.group(2)]

    halfway = "".join(noncomments)

    #remove single line comments
    #TODO: this will remove the ends of strings for example "this is // a string" will become "this is 
    regex = re.compile("(//.+)")
    return regex.sub("", halfway)
   # return "\n".join(noncomments)

def compile(subpath, path="./"):
    css = ""

    #open file

    filePtr = open(os.path.join(path, subpath), "r");
    origSource = filePtr.read();
    
    #remove comments
    source = remove_comments(origSource)
    
    #recurse on imports
    pat =  '@import\ +[\'\"](.+)[\'\"];?'
    regex = re.compile(pat)
    for match in regex.finditer(source):
        css += "\n/*" + match.group(1)+"*/\n\n"
        css += compile(os.path.join(os.path.dirname(subpath), match.group(1)), path)
    
    #remove import statements
    regex = re.compile(pat)
    resolvedSource = regex.sub("", origSource)

    #replace relative urls
    regex = re.compile('(url\([\'\"]?([^/].+)[\'\"]?\))')
    
    def fixUrl(matchObj):
        newUrl =  "url('"+os.path.join(os.path.dirname(subpath),matchObj.group(2))+"')"
        #newUrl = "\n/* "+matchObj.group() + "--->" + newUrl+"*/\n" + newUrl
        return newUrl
    css = css + regex.sub(fixUrl, resolvedSource)

    #close file
    filePtr.close()

    return css


#open the files
if __name__ == "__main__":
    print compile(os.path.basename(sys.argv[1]),os.path.dirname(sys.argv[1]))


