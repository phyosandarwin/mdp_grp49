#to format algo cmd for stm
def process_strings(strings):
    # Define specific replacements
    special_replacements = {
        'SB': 'B',
        'SF': 'F'
    }

    # Function to process each string
    def process_string(s):
        # Check the first two characters of the string
        prefix = s[:2]  # Get the first two characters

        # Check if prefix is in special replacements
        if prefix in special_replacements:
            return special_replacements[prefix] + s[2:]  # Replace prefix and keep the rest of the string

        # Check if 'P_' is in the string
        if 'P_' not in s:
            # Flip the first two letters if no 'P_' in the string
            if len(s) > 1:
                return s[1] + s[0] + s[3:]
            else:
                return s  # If single character or empty, return as is

        # If 'P_' is present, return the string as is
        return s

    # Process the list of strings
    return [process_string(s) for s in strings]

# # Example usage
# s = 'SF090,RF090,SF120,LF090,SB020,LF090,P___4,SB020,LF090,SB030,RB090,SF030,P___6,SB030,RF090,SF020,LF090,SB010,RB090,LB090,RB090,SF020,P___2,SB040,RF090,P___5,SB020,LF090,SF030,LF090,SF030,RF090,P___3,SB010,LB090,SF010,RF090,P___1'
# strings = s.split(',')
# processed_strings = process_strings(strings)
# print(processed_strings)
