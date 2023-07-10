import os
import re
from datetime import datetime

from collections import namedtuple
from anytree import AnyNode, PreOrderIter
from anytree.search import findall

from sqlalchemy import create_engine
import pandas as pd
import numpy as np

pd.options.display.max_columns = None
pd.options.display.max_colwidth = None
pd.options.display.width = None


cof_files_dir = "/Users/gregskluzacek/Documents/Comics/previews_parsing/pv_parsing_with_pandas/data/utf8_cof_files"

CofFile = namedtuple("CofFile", ["fn_period", "fn_name", "fn_path"])
PreviewHdr = namedtuple("PreviewHdr", [
    'Index',
    'fn_period',
    'fn_name',
    'fn_path',
    'fn_mo',
    'fn_yr',
    'fn_volume',
    'fn_vol_issue',
    'fn_issue',
    'fn_ident',
    'proc_sts'
])
PvHdrTxt = namedtuple("PvHdrTxt", [
    "pvh_id",
    "ident_line",
    'ident_type',
    "txt_ident",
    "txt_mo",
    "txt_yr",
    "txt_volume",
    "txt_vol_issue",
    "txt_issue",
    "txt_period",
    "txt_name"],
    defaults=[None]*8
)
PvHdrLdLines = namedtuple("PvHdrLdLines", ["Index", "fn_period", "fn_ident", "fn_path", "fn_name"])
PvLines = namedtuple("PvLines", ["pvl_id", "pvh_id", "pvl_seq", "line_text"])
PathNode = namedtuple("PatyhNode", ["Index", "pvhh_id", "parent_pvhh_id", "hrch_level", "heading_nm"])

# #   pvh_id,
#                               DEFAULT (will be the next value of a sequence),
#     ident_typ,
#           'ident_type':       {2 | 3 | 4 | 10 | 20 | 30 | 40)
#     ident_line,
#           'ident_line':       line_nbr() {10} || line_nbr(+1) {2 | 20} || line_nbr() {3 | 30}  || line_nbr(++ && *=-1) {4} || line_nbr(++) {40}
#     txt_ident,
#           'txt_ident':        None {2 | 3 | 4} || line {10 | 20 | 40} || line_1 + ' | ' + line_2 {30}
#     txt_mo,
#           'txt_mo':           None {2 | 3 | 4} || reg-ex-match (JAN thru DEC) {10 | 20 | 30 | 40)
#     txt_yr,
#           'txt_yr':           None {2 | 3 | 4 | 10 | 20} || reg-ex-match (NNNN) {30} || reg-ex-match (NN) {40}
#     txt_volume,
#           'txt_volume':       None {2 | 3 | 4 | 40} || reg-ex-match (NN) {10 | 20 | 30)
#     txt_vol_issue,
#           'txt_vol_issue':    None {2 | 3 | 4 | 40} || reg-ex-match (Nn) {10 | 20 | 30)
#     txt_issue,
#           'txt_issue':        None {2 | 3 | 4 | 10 | 20 | 40} || reg-ex-match (NNN) {30}
#     txt_period,
#           'txt_period':       None {2 | 3 | 4 | 10 | 20 | 40} || derived <datetime OBJ> {30}
#     txt_name,
#           'txt_name':         None {2 | 3 | 4 | 10 | 20 | 40} || derived <str OBJ> {30}
# #   fn_ident,
#           'fn_ident':         fn_ident,
# #   fn_mo,
#           'fn_mo':            fn_mo_str,
# #   fn_yr,
#           'fn_yr':            fn_yr_nbr,
# #   fn_volume,
#          'fn_volume':         fn_vol_nbr,
# #   fn_vol_issue,
#          'fn_vol_issue':      fn_vol_iss_nbr,
# #   fn_issue,
#          'fn_issue':          fn_iss_nbr,
# #   fn_period,
#           'fn_period':        fn_dt_obj,
# #   fn_name,
#          'fn_name':           fn_names[fn_dt_obj],
#     proc_sts,
#                               'LOGGED',
# #   fn_path
#          'fn_path':           fn_path


def basic_ident_line(pvh_id, line_nbr, match, txt_ident):
    # noinspection PyArgumentList
    return PvHdrTxt(
        pvh_id=pvh_id,
        ident_line=line_nbr,
        ident_type=10,
        txt_ident=txt_ident,
        txt_mo=match.group(1),
        txt_volume=match.group(2),
        txt_vol_issue=match.group(3)
    )


def terse_ident_line_with_ind_line(pvh_id, line_nbr, match, txt_ident):
    if match:
        # noinspection PyArgumentList
        return PvHdrTxt(
            pvh_id=pvh_id,
            ident_line=line_nbr,
            ident_type=20,
            txt_ident=txt_ident,
            txt_mo=match.group(1),
            txt_volume=match.group(2),
            txt_vol_issue=match.group(3)
        )
    else:
        # noinspection PyArgumentList
        return PvHdrTxt(
            pvh_id=pvh_id,
            ident_line=-line_nbr,
            ident_type=2
        )


def advanced_ident_line(pvh_id, line_nbr, match_1, match_2, txt_ident_1, txt_ident_2):
    if match_2:
        txt_mo_str = match_1.group(1).upper()
        txt_yr_nbr = match_1.group(2)
        return PvHdrTxt(
            pvh_id=pvh_id,
            ident_line=line_nbr,
            ident_type=30,
            txt_ident=txt_ident_1 + ' | ' + txt_ident_2,
            txt_mo=txt_mo_str,
            txt_yr=txt_yr_nbr,
            txt_volume=match_2.group(2),
            txt_vol_issue=match_2.group(3),
            txt_issue=match_2.group(1),
            txt_period=datetime.strptime(f'{txt_yr_nbr}-{txt_mo_str}-01', '%Y-%b-%d'),
            txt_name=f'{txt_mo_str}{int(txt_yr_nbr) - 2000}.txt'
        )
    else:
        # noinspection PyArgumentList
        return PvHdrTxt(
            pvh_id=pvh_id,
            ident_line=-line_nbr,
            ident_type=3
        )


def parse_ident_from_item_line(pvh_id, line_nbr, match, txt_ident):
    txt_mo_str = match.group(1).upper()
    txt_yr_nbr = match.group(2)
    txt_yr_nbr_cc = f"20{txt_yr_nbr}"
    # noinspection PyArgumentList
    return PvHdrTxt(
        pvh_id=pvh_id,
        ident_line=line_nbr,
        ident_type=40,
        txt_ident=txt_ident,
        txt_mo=txt_mo_str,
        txt_yr=txt_yr_nbr_cc,
        txt_period=datetime.strptime(f'{txt_yr_nbr_cc}-{txt_mo_str}-01', '%Y-%b-%d'),
        txt_name=f'{txt_mo_str}{txt_yr_nbr}.txt'
    )


def missing_ident_line(pvh_id, line_nbr):
    # noinspection PyArgumentList
    return PvHdrTxt(
        pvh_id=pvh_id,
        ident_line=-line_nbr,
        ident_type=4
    )


# TODO: update function def to pass in the directory where the cof_files are stored, instead of using `cof_files_dir`
def get_cof_file_listing_from_file_sys():
    pv_hdrs = []
    # read the file listing from the directory containing the cof files and process files with a  `.txt` extension
    with os.scandir(cof_files_dir) as entries:
        for entry in entries:
            if entry.is_file() and '.txt' in entry.name:
                try:
                    # strip the file extension off the filename and add 01 to format a date in ddmmmyy format
                    # then attempt to parse the string into a date object, which may fail if not valid date is given
                    # finally append a tuple with the dt_obj, file name and file path the pv_hdrs list
                    filename_ddmmyy = f"01{entry.name[:-4]}"
                    filename_dt_obj = datetime.strptime(filename_ddmmyy, "%d%b%y")
                    pv_hdrs.append((filename_dt_obj, entry.name, os.path.dirname(entry.path)))
                except ValueError:
                    raise ValueError(
                        f"Error parsing date from cof filename: {entry.name}. "
                        f"Invalid month: {filename_ddmmyy[2:5]} or invalid year: {filename_ddmmyy[5:]}"
                    )
    # we need to process the files in the proper date order, so sort the list of tuples before retuning it
    pv_hdrs.sort()

    # TODO: set the correct data types when creating the DataFrame
    previews_hdr = pd.DataFrame(
        data=pv_hdrs,
        columns=["fn_period", "fn_name", "fn_path"],
        index=pd.RangeIndex(start=1, stop=len(pv_hdrs) + 1, name="pvh_id")
    )
    return previews_hdr


def derive_fn_fields(previews_hdr):
    # TODO: set the correct data types when creating the DataFrame
    # derive the fields based on the period date (which itself is derived from the file name)
    previews_hdr["fn_mo"] = previews_hdr.fn_period.dt.strftime('%b').str.upper()  # str
    previews_hdr["fn_yr"] = previews_hdr.fn_period.dt.year  # int ???
    previews_hdr["fn_volume"] = previews_hdr.fn_yr - 1990  # int ???
    previews_hdr["fn_vol_issue"] = previews_hdr.fn_period.dt.month  # int ???
    previews_hdr["fn_issue"] = (previews_hdr.fn_volume - 1) * 12 + previews_hdr.fn_vol_issue + 27  # int ???
    previews_hdr["fn_ident"] = (  # str
            "PREVIEWS " + previews_hdr.fn_mo.astype(str) + "-" + previews_hdr.fn_yr.astype(str) +
            " ISSUE #" + previews_hdr.fn_issue.astype(str) +
            " (VOL " + previews_hdr.fn_volume.astype(str) + " #" + previews_hdr.fn_vol_issue.astype(str) + ")"
    )
    previews_hdr["proc_sts"] = "LOGGED"  # str


def create_cof_file_listing_df():
    # read the file list for the cof files directory and create the initial dataframe
    previews_hdr = get_cof_file_listing_from_file_sys()
    # add derived fn fields to the previews_hdr dataframe
    derive_fn_fields(previews_hdr)

    # TODO: pass in the path and file name to save the DataFrame to...
    previews_hdr.to_csv(
        path_or_buf="../data/output/previews_hdr_fn.csv",
        sep=",",
        na_rep="",
        header=True,
        index=True,
        date_format=None,
    )
    # print(previews_hdr)
    # print(previews_hdr.dtypes)

    return previews_hdr


def parse_cof_files_for_txt_fields(previews_hdr):
    # TODO: encapsulate the logic in this method into a Class so you can break up the inner for loop into
    #  multiple methods
    # TYPES: 10 -- BASIC
    regex1 = r'^PREVIEWS (JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC).* V(?:OL)?\.? ?(\d\d) #(\d\d?)$'
    cregex1 = re.compile(regex1)
    # TYPES: 20 or 2 -- TERSE
    regex3 = r'^(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC).* V(?:OL)?\.? ?(\d\d) #(\d\d?)$'
    cregex3 = re.compile(regex3)
    # TYPES: 30 or 3 -- ADVANCED
    regex4 = r'^PREVIEWS (JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC).* (\d\d\d\d)$'
    cregex4 = re.compile(regex4)
    regex5 = r'^ISSUE #(\d\d\d) \(VOL\. (\d\d) #(\d\d?)\)$'
    cregex5 = re.compile(regex5)
    # TYPES: 40 or 4 -- FROM LINE ITEM
    regex6 = r"^(?:[^\t]*)?\t(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)(\d\d) \d\d\d\d\tPREVIEWS #\d\d\d (?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC).* \d\d\d\d CUSTOMER ORDER FORM ?(?:\(Net\))?\t[^\t]*\t[^\t]*\t[^\t]*\t?$"
    cregex6 = re.compile(regex6)
    pv_hdr_txt_list = []
    row: PreviewHdr
    # for each cof file, determine the `ident_type` and parse out the txt fields from the individual cof files' text
    for row in previews_hdr.itertuples(name="PreviewHdr"):
        # print(row.Index, row.fn_name)
        with open(f"{row.fn_path}/{row.fn_name}", 'r') as fh:
            for i, line in enumerate(fh, 1):
                line = line.rstrip("\n")

                # check if we've hit the PREVIEWS PUBLICATIONS header, this is usually the last ditch effort on
                # parsing some minimal info from the CUSTOMER ORDER FORM line item in the issue.
                # TYPES: 40 or 4 -- FROM LINE ITEM
                if line == 'PREVIEWS PUBLICATIONS':
                    # start at the PREVIEWS PUBLICATIONS heading and loop until we reach the PREMIER PUBLISHERS
                    # heading (missing) or find a line that matches the CUSTOMER ORDER FORM reg-ex
                    while True:
                        i, line = i + 1, fh.readline().rstrip("\n")
                        if line == "PREMIER PUBLISHERS" or i > 10001:
                            pv_hdr_txt = missing_ident_line(row.Index, i)
                            break
                        m = cregex6.fullmatch(line)
                        if m:
                            pv_hdr_txt = parse_ident_from_item_line(row.Index, i, m, line)
                            break
                    break

                # check if the line matches the ``ident line label`` which indicates the next line is an
                # abbreviated IDENT line
                # TYPES: 20 or 2 -- TERSE
                if line == 'PREVIEWS ORDER FORM':
                    # get the next line
                    i, line = i + 1, fh.readline().rstrip("\n")
                    # attempt to get the regex match object on the TERSE IDENT line
                    m = cregex3.fullmatch(line)
                    pv_hdr_txt = terse_ident_line_with_ind_line(row.Index, i, m, line)
                    break

                # check if the regex for the BASIC IDENT line is a match
                # TYPES: 10 -- BASIC
                m = cregex1.fullmatch(line)
                if m:
                    pv_hdr_txt = basic_ident_line(row.Index, i, m, line)
                    break

                # check if the regex for the first (of two) ADVANCED IDENT lines is a match
                # TYPES: 30 or 3 -- ADVANCED
                m = cregex4.fullmatch(line)
                if m:
                    # the 1st part matched, now get & check the next line for a match
                    i, line2 = i + 1, fh.readline().rstrip("\n")
                    # check if the second (of two) ADVANCED IDENT lines is a match
                    m1 = cregex5.fullmatch(line2)
                    pv_hdr_txt = advanced_ident_line(row.Index, i, m, m1, line, line2)
                    break

        # print(row.fn_name, pv_hdr_txt)
        pv_hdr_txt_list.append(pv_hdr_txt)
    return pv_hdr_txt_list


def extract_header_txt_fields(previews_hdr):
    pv_hdr_txt_list = parse_cof_files_for_txt_fields(previews_hdr)

    # TODO: set the correct data types when creating the DataFrame
    # create a dataframe from the parsed text
    pv_hdr_txt = pd.DataFrame(
        data=pv_hdr_txt_list,
        columns=[
            "pvh_id",
            "ident_line",
            'ident_type',
            "txt_ident",
            "txt_mo",
            "txt_yr",
            "txt_volume",
            "txt_vol_issue",
            "txt_issue",
            "txt_period",
            "txt_name"
        ],
    )
    # setting the index to `pvh_id` so we can concatenate with the main previews header dataframe
    pv_hdr_txt.set_index("pvh_id", drop=True, inplace=True)
    # print(pv_hdr_txt)
    # print(pv_hdr_txt.dtypes)

    # TODO: pass in the path and file name to save the DataFrame to...
    pv_hdr_txt.to_csv(
        path_or_buf="../data/output/previews_hdr_txt.csv",
        sep=",",
        na_rep="",
        header=True,
        index=True,
        date_format=None,
    )
    return pv_hdr_txt


def create_previews_hdr_table(previews_hdr, pv_hdr_txt):
    # TODO: should we just join instead of concat?
    df = pd.concat([previews_hdr, pv_hdr_txt], axis=1)

    df.astype({
        "fn_period": "datetime64[ns]",
        "fn_name": "str",
        "fn_path": "str",
        "fn_mo": "str",
        "fn_yr": "Int64",
        "fn_volume": "Int64",
        "fn_vol_issue": "Int64",
        "fn_issue": "Int64",
        "fn_ident": "str",
        "proc_sts": "str",
        "ident_line": "Int64",
        "ident_type": "Int64",
        "txt_ident": "str",
        "txt_mo": "str",
        "txt_yr": "Int64",
        "txt_volume": "Int64",
        "txt_vol_issue": "Int64",
        "txt_issue": "Int64",
        "txt_period": "datetime64[ns]",
        "txt_name": "str",
    })

    # print(df)
    # print(df.dtypes)

    # TODO: pass in the path and file name to save the DataFrame to...
    df.to_csv(
        path_or_buf="../data/output/previews_hdr.csv",
        sep=",",
        na_rep="",
        header=True,
        index=True,
        date_format=None,
    )
    # TODO: change to use a postgres database
    engine = create_engine('sqlite:///test_sqlite.db', echo=False)
    df.to_sql("previews_hdr", con=engine, if_exists="replace")


def load_previews_hdr():
    # create the main fn portion of the preview header data
    previews_hdr = create_cof_file_listing_df()
    # process the cof files to create the txt portion of the preview header data
    pv_hdr_txt = extract_header_txt_fields(previews_hdr)
    # concatenate and write data to the database
    create_previews_hdr_table(previews_hdr, pv_hdr_txt)


def load_lines():
    engine = create_engine('sqlite:///test_sqlite.db', echo=False)

    # TODO: once we have established the repeated process, we will need to stop dropping tables
    #  and figure out a way to do this incrementally. THOUGH, if the processing of the heading
    #  hierarchy is dependent on successfully processing all preceding months before processing
    #  additional months, then maybe we need to stop processing at the point where an issue is
    #  detected so as not to waste time sorting out successive months when there is an error in
    #  one or more preceding months.
    sql = 'DROP TABLE IF EXISTS previews_lines;'
    engine.execute(sql)

    # read the preview_hdr records into a DataFrame where the line containing the cof
    # file identifier has been successfully located within the given cof file
    sql_stmt = """select 
        pvh_id, fn_period, fn_ident, fn_path, fn_name 
        from previews_hdr 
        where proc_sts = 'LOGGED' and ident_line > 0 
        order by fn_period"""
    previews_hdr = pd.read_sql_query(sql_stmt, con=engine, index_col="pvh_id", parse_dates=["fn_period"])

    row: PvHdrLdLines
    total_row_count = 0     # keep track of the total number or cof file lines that we've read across all cof files

    # for each header record
    for row in previews_hdr.itertuples(name="PreviewHdr"):
        # for the given header record, load the lines from the file into a DataFrame
        with open(f"{row.fn_path}/{row.fn_name}") as fh:
            pv_lines = pd.DataFrame(fh, columns=["line_text"])

        # strip newline from all lines
        pv_lines["line_text"] = pv_lines.line_text.str.rstrip("\n")

        # 1) set pvl_seq (line number) to 1 thru the number of records (pvl_seq is unique to each file)
        # 2) set the pvh_id foreign key to point back to the corresponding previews_hdr record's PK
        pv_lines["pvl_seq"] = range(1, len(pv_lines) + 1)
        pv_lines["pvh_id"] = row.Index

        # update the previews_lines dataframe's index (pvl_id) so that it unique across all cof files
        # we do this by adding the total number of cof file lines read to this point (not including the
        # current file) to the pvl_seq of each record. We must then set the name of the index to match
        # the column name on the table
        pv_lines.index = pv_lines.pvl_seq + total_row_count
        pv_lines.index.name = "pvl_id"

        # write the dataframe to the preview lines header
        pv_lines.to_sql("previews_lines", con=engine, if_exists="append")

        # increment the total row count by the number of rows that were in the current file
        total_row_count += len(pv_lines)


def set_pv_lines_type():
    # TODO: implement logic to separate out lines for `Instructions` and `Notes` from Heading lines
    engine = create_engine('sqlite:///test_sqlite.db', echo=False)

    # list of IDENT-line line numbers by pvh_id (file)
    sql_stmt_pvh_ident = """select 
        pvh_id, ident_line 
        from previews_hdr 
        where proc_sts = 'LOGGED' and ident_line > 0 
        order by fn_period"""
    previews_hdr_ident = pd.read_sql_query(sql_stmt_pvh_ident, con=engine, index_col="pvh_id")

    # list of line numbers by pvh_id (file) where any line with a line number greater than this line number is `JUNK`
    # the like condition will keep all things we need and exclude blank lines and garbage lines (i.e., random
    # integers or other characters where the data is not tab delimited)
    sql_stmt_pvl_max = """select
        t1.pvh_id, max(t1.pvl_seq) as last_item_seq
        from previews_lines t1
        join previews_hdr t2
        on t2.pvh_id = t1.pvh_id
        where t1.line_text like '%\t%\t%' and t2.proc_sts = 'LOGGED' and t2.ident_line > 0
        group by t1.pvh_id"""
    previews_lines_max = pd.read_sql_query(sql_stmt_pvl_max, con=engine, index_col="pvh_id")

    # get a DataFrame with ALL lines (that have been logged and have a proper identifying line numer, i.e., not types  2,3,4)
    sql_stmt_pvl_src = """select
        t1.pvh_id, t1.pvl_id, t1.pvl_seq, t1.line_text
        from previews_lines t1
        join previews_hdr t2
        on t2.pvh_id = t1.pvh_id
        where t2.proc_sts = 'LOGGED' and t2.ident_line > 0
        """
    previews_lines_src = pd.read_sql_query(sql_stmt_pvl_src, con=engine, index_col="pvh_id")

    # creating a DataFrame, where we are progressively building up the values for the `pv_type` column

    # 1. combine the 3 dataframes read in from the tables by using their common index of pvh_id
    # 2. default the pv_type to HDG (heading) for all lines
    # 3. if a given row's line number is > the corresponding last `good` line number for its pvh_id (file) mark it as JUNK
    # 4. if a given row is the empty string mark it as BLANK
    # 5. if a given row starts with the word PAGE and only has an optional `M-` and contains up to 3 digits, mark it as a PAGE
    # 6. if a given row's line number matches the corresponding IDENT's line number, mark it as IDENT
    # 7. if a given row has at least (???) 3 tab delimited columns, mark it a an ITEM
    # note: there will be no IDENT pv_type for ident_type 40 because it is derived from the Customer Order Form's item's ITEM TEXT (solicitation code)
    df_joined = previews_lines_src.join([previews_hdr_ident, previews_lines_max])

    # df_joined["pv_type"] = "HDG"
    # df_joined.loc[df_joined.pvl_seq > df_joined.last_item_seq, "pv_type"] = "JUNK"
    # df_joined.loc[df_joined.line_text.str.strip() == "", "pv_type"] = "BLANK"
    # df_joined.loc[df_joined.line_text.str.strip().str.contains(r"^PAGE (?:M-)?\d{1,3}\s*$"), "pv_type"] = "PAGE"
    # df_joined.loc[df_joined.pvl_seq == df_joined.ident_line, "pv_type"] = "IDENT"
    # df_joined.loc[df_joined.line_text.str.strip("\t").str.contains(r"[^\t]*\t[^\t]*\t[^\t]*"), "pv_type"] = "ITEM"

    df_joined["pv_type"] = np.where(df_joined.pvl_seq > df_joined.last_item_seq, "JUNK",
        np.where(df_joined.line_text.str.strip() == "", "BLANK",
        np.where(df_joined.line_text.str.strip().str.contains(r"^PAGE (?:M-)?\d{1,3}\s*$"), "PAGE",
        np.where(df_joined.pvl_seq == df_joined.ident_line, "IDENT",
        np.where(df_joined.line_text.str.strip("\t").str.contains(r"[^\t]*\t[^\t]*\t[^\t]*"), "ITEM",
        np.where(df_joined.line_text.str.strip().str.contains(r"^\(NOTE: .*\)$"), "NOTE",
        "HDG"
    ))))))

    # change the index from pvh_id to pvl_id before writing out to a table
    df_joined.reset_index(inplace=True)
    df_joined.set_index("pvl_id", inplace=True)

    df_joined["line_text"] = np.where(
        (df_joined.pv_type == "PAGE") | (df_joined.pv_type == "HDG"), df_joined["line_text"].str.strip(), df_joined["line_text"]
    )
    df_joined["page_nbr"] = df_joined["line_text"].str.extract(r"^PAGE (?:M-)?(\d{1,3})$")
    tmp = df_joined.loc[~df_joined.page_nbr.isna()]["page_nbr"].astype("int64")
    df_joined.update(tmp)
    df_joined["pg_nbr_typ"] = np.where(
        (df_joined.pv_type == "PAGE") & (df_joined["line_text"].str.contains(r"^PAGE M-\d{1,3}$")), "M", "S"
    )

    df_joined.to_sql("pv_line_type", con=engine, if_exists="replace")


def set_page_numbers():
    engine = create_engine('sqlite:///test_sqlite.db', echo=False)

    # list of PAGE lines with their corresponding line numbers
    sql_stmt_pages = """select
        pvh_id, pvl_seq as pvl_seq_first, page_nbr, pg_nbr_typ
        from pv_line_type
        where pv_type = 'PAGE'
        order by pvl_seq"""
    pv_line_pages = pd.read_sql_query(sql_stmt_pages, con=engine, index_col="pvh_id")

    # TODO: break PAGE number text into its 2 parts page_nbr_prefix and page_nbr

    # list of pvh_id (files) and the last line number in it
    sql_stmt_max = """select
        pvh_id, max(pvl_seq) as max_line
        from previews_lines
        group by pvh_id"""
    pv_line_max = pd.read_sql_query(sql_stmt_max, con=engine, index_col="pvh_id")

    # combine the dataframes for the above tables by using their common index of pvh_id
    #   pvh_id
    #   pvl_seq_first
    #   pvl_seq_last (added in the 2nd line of code below)
    #   max_line
    #   page_nbr_text (change to be page_nbr_prefix and page_nbr)
    pv_line_join = pv_line_pages.join(pv_line_max)
    # the following implements the SQL LEAD function (wrapped in a ifnull function) of:
    # ifnull( lead( t1.pvl_seq ) over( partition by t1.pvh_id order by t1.pvl_seq) - 1, t2.max_line ) )
    pv_line_join["pvl_seq_last"] = (pv_line_join.groupby("pvh_id")["pvl_seq_first"].shift(-1) - 1).fillna(pv_line_join["max_line"]).astype("int64")

    # get ALL lines
    sql_stmt_lines = """select 
    pvh_id, pvl_id, pvl_seq, pv_type, line_text 
    from pv_line_type 
    order by pvh_id, pvl_seq
    """
    pv_lines = pd.read_sql_query(sql_stmt_lines, con=engine, index_col="pvh_id")

    # TODO: wondering if there is a way that is faster and uses less memory for the next 2 lines of code

    # The next 2 lines implement a non-equi join

    # combine the dataframe for the above table with the previously joined dataframe by using their common index of pvh_id
    # NOTE: This join will take a long time (compared to the other joins) and explode the number of rows SUBSTANTIALLY
    #   pvh_id
    #   pvl_id
    #   pvl_seq
    #   pv_type
    #   line_text
    #   pvl_seq_first
    #   page_nbr_text (change to be page_nbr_prefix and page_nbr)
    #   max_line
    #   pvl_seq_last
    pv_tmp = pv_lines.join(pv_line_join)

    # filter out all rows where a given row's line number is not between (inclusive) the first and last pvl seq numbers
    # each of the remaining rows, will have the page number text of that corresponds to the range of lines that fall on a given page
    pv_tmp2 = pv_tmp[(pv_tmp["pvl_seq"] >= pv_tmp["pvl_seq_first"]) & (pv_tmp["pvl_seq"] <= pv_tmp["pvl_seq_last"])]

    # reset indexes so we can retain the pvh_id as a column
    pv_lines.reset_index(inplace=True)
    pv_tmp2.reset_index(inplace=True)

    # change the index to pvl_id before the final join
    pv_lines.set_index("pvl_id", inplace=True)
    pv_tmp2.set_index("pvl_id", inplace=True)

    # Drop columns that would be duplicates or that are no longer needed when we do the final join
    pv_tmp3 = pv_tmp2.drop(columns=["pvh_id", "pvl_seq", "pv_type", "line_text", "pvl_seq_first", "pvl_seq_last", "max_line"])

    # combine the dataframe containing the page numbers with the ALL lines dataframe by using their common index of pvl_id
    # note: not all rows will be assigned line numbers (rows before the first page number line - mostly IDENT  & BLANK lines)
    #   pvh_id
    #   pvl_id
    #   pvl_seq
    #   pv_type
    #   line_text
    #   page_nbr_text (change to be page_nbr_prefix and page_nbr)
    pv_lines_fnl = pv_lines.join(pv_tmp3)

    # any rows without line numbers set to -1
    pv_lines_fnl["page_nbr"] = pv_lines_fnl["page_nbr"].fillna(-1)
    pv_lines_fnl["page_nbr"] = pv_lines_fnl["page_nbr"].astype("int64")
    pv_lines_fnl["pg_nbr_typ"] = pv_lines_fnl["pg_nbr_typ"].fillna("N")
    pv_lines_fnl.to_sql("pv_lines_fnl", con=engine, if_exists="replace")


def create_previews_hdg_hrch_empty_table():
    engine = create_engine('sqlite:///test_sqlite.db', echo=False)

    dtypes_dict = {
        "pvhh_tid": "int64",
        "pvl_id": "int64",
        "pvhh_id": "int64",
        "parent_pvhh_id": "int64",
        "hrch_level": "int64",
        "heading_nm": "str",
        "detail_items_ind": "bool",
        "valid_from": "datetime64[ns]",
        "valid_to": "datetime64[ns]"
    }
    previews_hdg_hrch = pd.DataFrame(columns=list(dtypes_dict.keys())).astype(dtypes_dict)
    previews_hdg_hrch.set_index("pvhh_tid", inplace=True)
    previews_hdg_hrch.to_sql("previews_hdg_hrch", con=engine, if_exists="replace")


def build_heading_paths(pvh_id):
    engine = create_engine('sqlite:///test_sqlite.db', echo=False)

    # get the fn_period for the given pvh_id. this is needed when querying the previews_hdg_hrch table
    sql_stmt = """select fn_period from previews_hdr where pvh_id = :pvh_id;"""
    fn_period_df = pd.read_sql_query(sql_stmt, params={"pvh_id": pvh_id}, con=engine)
    fn_period = fn_period_df.at[0, "fn_period"]

    # get all the previews_hdg_hrch valid for the given fn_period
    sql_stmt = """select 
    pvhh_id, parent_pvhh_id, hrch_level, heading_nm 
    from previews_hdg_hrch 
    where :fn_period between valid_from and valid_to;"""
    hdg_paths_df = pd.read_sql_query(sql_stmt, params={"fn_period": fn_period}, con=engine)

    # build the heading hierarchy node tree
    root_node = AnyNode(pvhh_id=0, heading_nm="")   # dummy root node for searching purposes only
    row: PathNode
    for row in hdg_paths_df.itertuples(name="PathNode"):
        # determine the parent heading
        if np.isnan(row.parent_pvhh_id):
            # the parent_pvhh_id will be set to null for level 1 headings, which do not have any parent heading
            # so link them to the dummy root node
            parent_node = root_node
        else:
            # find the parent heading for the current node by searching for the node with the corresponding pvhh_id
            find_results = findall(root_node, filter_=lambda node: node.pvhh_id == row.parent_pvhh_id)
            parent_node = find_results[0]   # there should only be 1 matching search result

        # create a new node in the hierarchy for the current node with the given parent node
        AnyNode(
            pvhh_id=row.pvhh_id,
            parent_pvhh_id=row.parent_pvhh_id,
            hrch_level=row.hrch_level,
            heading_nm=row.heading_nm,
            index=row.Index,
            parent=parent_node
        )

    # create a dataframe containing the absolute path for each heading in the hierarchy
    paths = ["/".join([pn.heading_nm for pn in node.path]) for node in PreOrderIter(root_node) if not node.is_root]
    index = [node.index for node in PreOrderIter(root_node) if not node.is_root]
    paths_df = pd.DataFrame(data=paths, columns=["path"], index=index)
    hdg_hrch = hdg_paths_df.join(paths_df)

    return hdg_hrch

def resolve_heading_hierarchy(pvh_id):
    hdg_hrch_paths = build_heading_paths(pvh_id)

    engine = create_engine('sqlite:///test_sqlite.db', echo=False)

    sql_stmt = """ select
    pvl_id, line_text
    from pv_lines
    where pv_type = 'HDG'
    and pvh_id = :pvh_id
    order by pvl_seq;
    """
    hdg_lines = pd.read_sql_query(sql_stmt, params={"pvh_id": pvh_id}, con=engine)

    curr_path = []
    matches = []
    for row in hdg_lines.itertuples():
        paths_to_search_for = ["/" + row.line_text]
        for i, _ in enumerate(curr_path, 1):
            paths_to_search_for.append("/" + "/".join(curr_path[:i] + [row.line_text]))

        hh_match = hdg_hrch_paths[hdg_hrch_paths.path.isin(paths_to_search_for)].sort_values(by=["hrch_level"], ascending=False)
        if hh_match.empty:
            continue

        path = hh_match.iloc[0]
        matches.append((row.Index, row.pvl_id, path.pvhh_id))
        curr_path = path["path"].split("/")[1:]


if __name__ == "__main__":
    from timeit import timeit
    # print(timeit("load_previews_hdr();load_lines();set_pv_lines_type();set_page_numbers()", number=1, globals=globals()))
    # print(timeit("load_previews_hdr()", number=1, globals=globals()))
    # print(timeit("load_lines()", number=1, globals=globals()))
    # print(timeit("set_pv_lines_type()", number=1, globals=globals()))
    # print(timeit("set_page_numbers()", number=1, globals=globals()))
    # load_previews_hdr()
    # load_lines()
    set_pv_lines_type()
    set_page_numbers()
