import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", default='input.txt', dest="input")
parser.add_argument("-n", "--num", default=5, type=int, dest="num")
parser.add_argument("-o", "--output", default='output.txt', dest="output")

args = parser.parse_args()

print('Input file: ',args.input)
print('Number of lines: ',str(args.num))
print('Output file: ',args.output)
print('')

try:
    with open(args.input, 'r') as read, open(args.output, 'w') as write:
        for i in range(args.num):
            write.write(read.readline())
    print('Rewrite '+str(args.num)+' lines')
except:
    print('Input file does not exist')

