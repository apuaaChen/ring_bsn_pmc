import os

p1p2s = [(0.5, 0.5), (0.7, 0.5), (0.7, 0.8), (0.3, 0.3)]
ns = [8, 16, 32, 64]

for p1p2 in p1p2s:
    p1 = p1p2[0]
    p2 = p1p2[1]
    print("p1=%.1f, p2=%.1f" % (p1, p2))
    for n in ns:
        cmd = "python exp.py --n %d --p1 %.1f --p2 %.1f" % (n, p1, p2)
        print(cmd)
        os.system(cmd)
