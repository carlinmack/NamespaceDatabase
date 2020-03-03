import glob
import os
import subprocess
import time

import click

from tqdm import trange


@click.command()
@click.option(
    "-n", "--number", default=40,
)
@click.option(
    "-o", "--outputfolder",
)
@click.option(
    "-d", "--deletefile", default=False, is_flag=True,
)
def main(number, outputfolder, deletefile):
    files = glob.glob("dumps/*.xml*")

    for file in files:
        filename = file[6:]
        print(filename)
        lines = countLines(file)

        chunksize = lines / number * 0.8

        with open(file) as infile:
            iter = 0
            inpage = False

            for index in trange(number, desc=file):
                partitionname = filename + "." + str(index)
                outfile = os.path.join("partitions", partitionname)

                with open("partitions.txt", "a+") as partitions:
                    partitions.write(partitionname + "\n")

                if not os.path.exists("partitions"):
                    os.mkdir("partitions")

                with open(outfile, "w+") as outfile:
                    for line in infile:
                        iter = iter + 1
                        if line == "  <page>\n":
                            # print("========= ==== ==== === = == ===")
                            inpage = True
                        if inpage:
                            outfile.write(line)
                        if iter > chunksize:
                            if line == "  </page>\n":
                                # print("!!!!!!!!! !!!! !!!! !!! ! !! !!!")
                                iter = 0
                                break

        if deletefile:
            pass
            # delete file


def countLines(f):
    print("counting lines: ", f)
    lines = int(subprocess.check_output(["./wcle.sh", f]))

    return lines


if __name__ == "__main__":
    main()
