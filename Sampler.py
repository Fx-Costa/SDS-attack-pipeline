import pandas as pd
import os.path


def sample(filename, n, m, columns):
    # Export path
    path = "Samples/" + str(n) + "_"

    # Full frame
    df = pd.read_csv(filename)
    df.index.name = "ID"
    max_m = len(df.columns)

    # Dropping columns based on input
    if m > 0 and columns == []:
        df = df.drop(df.iloc[:, m:max_m], axis=1)
        path = path + str(m)
    elif m > 0:
        df = df[columns]
        path = path + str(len(columns))
    else:
        path = path + "all"

    # Sampling n times (random)
    return df.sample(n), path


def write_to_csv(dataframe, filepath, acc):
    if os.path.isfile(filepath + ".csv"):
        identifier = "-" + str(acc)
        print(identifier)
        if identifier in filepath:
            filepath.replace(str(acc), str(acc + 1))
        else:
            filepath = filepath + "-" + str(acc)
        write_to_csv(dataframe, filepath, acc + 1)
    else:
        filepath = filepath + ".csv"
        print("Writing to: " + filepath)
        dataframe.to_csv(filepath)


def write_to_syn_config(df):
    return df


def parse_input(n, m, cols):
    # Parse input into workable types
    split = []
    if cols != "":
        split = cols.split(",")
        if len(split) < int(m):
            print("Ignoring incomplete input: cols")
            split = None
    if m == "":
        m = -1
    return int(n), int(m), split


def main():
    print("Awaiting input... n - number of samples")
    n = input()
    print("Awaiting (optional) input... m - number of columns (defaults to all)")
    m = input()
    print("Awaiting (optional) input... cols - comma separated column names (no space)")
    cols = input()

    n, m, cols = parse_input(n, m, cols)
    df, path = sample("../NATIONAL.csv", n, m, cols)


if __name__ == '__main__':
    main()

