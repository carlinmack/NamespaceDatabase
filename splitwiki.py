import click
import glob
import subprocess
from tqdm import trange

import time

@click.command()
@click.option(
    '-n',
    '--number',
    default=10,
)
@click.option(
    '-o',
    '--outputfolder',
)
@click.option(
    '-d',
    '--deletefile',
    default=False,
    is_flag=True,
)

def main(number, outputfolder, deletefile):
    files = glob.glob('*.xml*')

    for file in files:
        lines = countLines(file)

        for index in trange(number, desc=file):
            time.sleep(index / 10)
            # skip to first <page>
            # write (lines / number) - 5% to outputfolder
            # write until </page>
        
        if deletefile:
            pass
            # delete file


def countLines(f):
    print("counting lines: ", f)
    lines = subprocess.check_output(['wc', '-l', f])

    return lines

if __name__ == '__main__':
    main()