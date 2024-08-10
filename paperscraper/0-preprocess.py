# External packages
import re

# Internal modules
import config


# This Regular Find+Replace replaces instances of &amp; between <ee></ee> tags with a SPECIAL TAG `%26`. This tag will be replaced back to `&` in the code later on.
regex_find = r'(<ee>.*)&amp;(.*</ee>)'
regex_replace = r'\1%26\2'

with open(config.path_input_raw, "r") as raw_dblp:
    with open(config.path_input, "w") as processed_dblp:
        for line in raw_dblp:

            # Iterations are needed because re.sub replaces just 1 instance at a time
            intermediate_result = ""
            while line != intermediate_result:
                intermediate_result = line
                line = re.sub(regex_find, regex_replace, line)

            processed_dblp.write(line)

# output_str = "<ee>http://www.graphicsinterface.org/proceedings/2001/129?a=1&amp;b=2&amp;c=3&amp;</ee>"
# input_str = ""
# while output_str != input_str:
#     input_str = output_str
#     output_str = re.sub(regex_find, regex_replace, output_str)
