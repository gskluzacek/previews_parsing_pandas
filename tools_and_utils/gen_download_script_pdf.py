# use this script to generate a shell script that will download the cof files from the Previews website
# as of 2023/06/23 it looks like files as far back as JAN 2010 are available

# example curl statement
# curl https://previewsworld.com/Catalog/CustomerOrderForm/TXT/MAR20 -o MAR20.txt

# to use this program, set the stop month and year, as well as the last year in the year range
# run the program then copy and paste the output into a file name download_cof.sh
# then run the shell script from the command line.

def main():
    # url = "https://previewsworld.com/Catalog/CustomerOrderForm/TXT/"
    url = "https://www.previewsworld.com/Catalog/CustomerOrderForm/PDF/"

    months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    years = [year for year in range(10, 24)]

    stop_month = "AUG"
    stop_year = 23

    files = []
    for year in years:
        for month in months:
            if year == stop_year and month == stop_month:
                break
            print(f"curl {url}{month}{year} -o {month}{year}.pdf")
        if year == stop_year and month == stop_month:
            break
        print("")
        print("")


if __name__ == "__main__":
    main()
