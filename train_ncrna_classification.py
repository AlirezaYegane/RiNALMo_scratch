import sys

from scripts._bootstrap import bootstrap_repo
bootstrap_repo()

if __name__ == "__main__":
    from scripts.train.train_ncrna_classification import main
    main(sys.argv[1:])
