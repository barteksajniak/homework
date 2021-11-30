import argparse
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

parser = argparse.ArgumentParser()
parser.add_argument("-x", default=2, type=int, dest="xval")
parser.add_argument("-y", default=2, type=int, dest="yval")
parser.add_argument("-xy", default=2, type=int, dest="val")
parser.add_argument(dest="inputfile")

args = parser.parse_args()

try:
    image = plt.imread(args.inputfile).astype(float)
    if(args.val!=2):
        image = gaussian_filter(image, sigma=args.val)
    else:
        image = gaussian_filter(image, sigma=(args.xval,args.yval))
    plt.imshow(image)
    plt.show()
except:
    print('Input file does not exist')
