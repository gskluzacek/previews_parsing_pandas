import os
from charset_normalizer import from_fp

def main():
    cof_dir = "../data/original_cof_files"
    out_dir = "../data/utf8_cof_files"
    cof_files = os.listdir(cof_dir)

    encodings = set()
    for cof_file in cof_files:
        if not "09" in cof_file:
            print(f"skipping {cof_file}")
            continue
        with open(f"{cof_dir}/{cof_file}", "rb") as fh:
            r = from_fp(fh)
        encs = []
        enc_main = None
        if r.best():
            encs = r.best().encoding_aliases
            enc_main = r.best().encoding
        print(f"file: {cof_file}, encoding: {enc_main}, encoding aliases: {encs}")
        for enc in encs:
            encodings.add((enc_main, enc))
        if encs:
            with open(f"{out_dir}/{cof_file}", "wb") as fh:
                fh.write(r.best().output())
        else:
            print(f"#### non encoding found for file: {cof_file}")

    print("-"*100)
    for encoding in sorted(list(encodings)):
        print(encoding)


if __name__ == "__main__":
    main()
