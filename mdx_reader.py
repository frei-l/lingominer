from lingominer.mdict_reader.readmdict import MDX
import pprint

mdx = MDX("database/jitendex.mdx")

generator = mdx.items()

for _ in range(10):
    print(next(generator))
