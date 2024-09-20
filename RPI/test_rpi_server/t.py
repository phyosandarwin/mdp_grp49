from p import process_strings

# Example usage
s = 'SF090,RF090,SF120,LF090,SB020,LF090,P___4,SB020,LF090,SB030,RB090,SF030,P___6,SB030,RF090,SF020,LF090,SB010,RB090,LB090,RB090,SF020,P___2,SB040,RF090,P___5,SB020,LF090,SF030,LF090,SF030,RF090,P___3,SB010,LB090,SF010,RF090,P___1'
strings = s.split(',')
processed_strings = process_strings(strings)
print(processed_strings)