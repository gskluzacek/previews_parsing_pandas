# Previews Parsing With Pandas
This is attempt to refactor the preview_parsing (python) code so that it uses pandas to do its heavy lifting and potentially may use NLP

# Misc Details

## Previews Website

### cof files

_historical note: the links used to be in the following format a long time ago:_  
http://www.previewsworld.com/support/previews_docs/orderforms/MAR13_COF.txt  
http://www.previewsworld.com/support/previews_docs/orderforms/archive/2013/JAN13_COF.txt  
http://www.previewsworld.com/support/previews_docs/orderforms/archive/2009/JAN09/JAN09_COF.txt

can use this URL to access a customer order form in text format for a specific Month & Year:  
https://previewsworld.com/Catalog/CustomerOrderForm/TXT/JUL23

there is an "archive" page at:  
https://previewsworld.com/Catalog/CustomerOrderForms

this page lists as far back as JAN 2017. Not sure if there are additional files avaiable but just not listed.

PDF versions are also available:  
https://previewsworld.com/Catalog/CustomerOrderForm/PDF/JAN18

we may want to attempt to re-download all files and do a diff on them with the existing ones that we already have.

can download with curl, for example:  
curl https://previewsworld.com/Catalog/CustomerOrderForm/TXT/MAR20 -o MAR20.txt

it looks like we can go all the way back to JAN10, but nothing for 2009

#### parsing of the cof file identification string

input format example:  
PREVIEWS AUGUST VOL. 24 #8

* [0] PREVIEWS		constant
* [1] AUGUST		month - full name
* [2] VOL.			constant
* [3] 24			volume number
* [4] #8			issue number

output format:
* PREVIEWS VOL.  
* left padded with zeros to 3 digits <<volume number>>
* left padded with zeros to 2 digits <<issue number>>
* mo_abbr = substr(<<month>>, 0, 3)
* year == <<volume number>> + 2000 - 10

       ident_str       parses the first non-blank line of the file (PREVIEWS AUGUST VOL. 24 #8)
                       to: PREVIEWS VOL vvv ii mmm-yyyy
                       vvv - 3 digit volume number left padded with 0
                       ii  - 2 digit issue number left padded with 0
                       mmm - 3 character month
                       yyyy - 4 digit year (vol nbr + 2000 - 10)

#### line parsing (old php details)

       line is split into fields
           - pv_type           // initialize to UNKNOWN; values: H1, H2, H3, Hn, ITEM, BLANK, PAGE, IDENT, NOTFOUND
           - pv_value      0   // can be blank, in which case it should be set to null
           - sol_code      1   // if the sol_code is set, then the pv_type is ITEM mmmyy nnnn (remove the space)
                               // there can be 1 or 2 tabs between the sol_code & sol_text
                               // so we need to check if the 3rd element [index of 2] is blank, if yes
                               // then we need adjust all remaining columns by 1 to the right
           - sol_text      2+  //
           - sol_page          // this is set to the value of the last line of pv_type = PAGE
           - release_dt    3+  // can be blank, so need to check before creating date obj: mm/dd/yy
           - unit_price    4+  // the price has a price type, colon, space, dollar sign, and an amount with a
                               // decimal point and 2 digits after the decimal point
           - pi_ind            // this field may have a value of SRP: PI, in which case, set pi_ind to Y
                               // and unit_price is set to NULL, else set pi_ind to NULL
                               // if unit price cannot be parsed, then set pi_ind to E (error)
           -                   // the price type is (currently) discarded
           -                   // the remaining 2 fields are ' = $' and ''
           - pv_source         // set to the heading's path; heading separated by ' / '
           -                   // other values for pv_type
                               // sol_code is the empty string AND
                               // pv_value is the empty string         pv_type --> BLANK
                               // first 4 chars are PAGE               pv_type --> PAGE
                               // if regex matches                     pv_type --> IDENT
                                  /^PREVIEWS (JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC).* V(OL){0,1}\.{0,1} {0,1}\d\d #\d{1,2}$/
                               // if not ITEM, BLANK, PAGE or IDENT then the pv_type should be a heading type

#### pv_type (old php details)

    PREVIEWS LINE TYPES (pv_type)
             [  sol_code is the 2nd field <ndx-1>  ]
             [  pv_value is the 1st field <ndx-0>  ]
    
    ITEM      if the sol_code is populated, its an ITEM
    BLANK     sol_code & pv_vale are both blank
    PAGE      sol_code is blank and pv_value is: PAGE xxx
    IDENT     if the sol_code is blank and the value matches the
             regular expression for the identification line, then it is a identification line
    H3        if none of the above and if lvl 2 is set - check for lvl 3
    H2        if none of the above and if lvl 1 or 2 is set - check for lvl 2
    H1        if none of the above - check for lvl 2
    NOTFOUND  if none of the above then not found


### Cancellation Codes 
* 1 - Lateness
* 2 - Will Resolicit
* 3 - Cancelled by PREVIEWS
* 4 - Cancelled by Publisher
* 5 - Out of Stock
* 6 - Sold Out
* 7 - Publisher increments too high
* 8 - Resolicited in a prior Previews
* 9 - Series/Product line cancelled
* 10 - Supplier Out of Business

### Caution codes:
for more details see: http://www.diamondcomics.com/Home/1/1/3/108?articleID=25151

Caution codes are a 5 character text string consisting of 3 number separated by dashes  
the format of caution codes are as follows:

`C: I-C-S`

where 
* `I` - is the caution code corresponding to International Rights
* `C` - is the caution code corresponding to Content Changes
* `S` - is the caution code corresponding to Ship Date Changes

For example:  
`C: 1-0-2`

#### International Rights (I-Rights)
the item is restricted into what countries it can be sold.
* 0 = No International Rights restriction
* 1 = International Rights are restricted

#### Content Changes
the content may change after solicitation.
* 0 = No Content disclaimer
* 1 = Content disclaimer enforced

#### Ship Date Changes
the final shipping date may differ or change from the scheduled ship date.
* 0 = Product will ship according to the standard shipping schedule (within 90 days of the Previews cover date month)
* 1 = Product may ship an additional 30 days **beyond** the _scheduled_ ship date
* 2 = Product may ship an additional 60 days **beyond** the _scheduled_ ship date
* 3 = Product may ship an additional 90 days **beyond** the _scheduled_ ship date
* 4 = Product may ship at any time **beyond** the _scheduled_ ship date


# Tools and Utilities
* gen_download_script.py
  * this generates curl commands to download the cof files from the previews website. The commands can be saved into a shell script and then executed from the terminal
* download_cof_files.sh
  * this is one of the generated shell scripts containing curl commands to download cof files from the previews web site
* log_file_encodings.py
  * this script will read **ALL** files in the original_cof_files directory and re-encode them as utf-8 and write, **ALL** files read, to the utf8_cof_files directory. it will also create a log of the original encodings.

# Database Details

## General Thoughts
* For this iteration of the previews parsing, I'd like to go with a Postgres Database.
* We should probably closely consider how we want ot handle case and accent sensitivity. And evaluate the options that Postgres has available for its implementation of the UTF8 character set.
* the most recent iteration (python) of previews parsing used a MySQL database 
  * with UTF8 (variable byte length encoding with a max of 4 bytest per char) 
  * and a collating sequence that was both accent and case sensitvie. 
  * In hindsight, I'm not sure this is the best choice? 
  * Do we need the ability to distinguish Fantastic Four from FANTASTIC FOUR? when performing queries, Or Pena from Peña?
  * For display purposes, I'd like to be able to display the actual case of the strings along with any accents present.
  * For end-user/general search capabilities I **don't think** case and accents should be taken into consideration.
  * For sorting of output, I'd like to see accents ignored (but preserved in the database text strings).
  * However, for data cleaning of text strings to be stored in the database, I think we should be able to determine various use cases: such as, if something is completely uppercase, it should be converted to Title case, or if a character is missing an accent.
  * for the purposes of indexes (i.e., uniqueness), I think that Pena should be considered different from Peña. 
* for the table that contains the text of the cof files (previews_lines) should we consider have one column for the origianl line as read from the file and another column for any edits applied to the text? Or maybe even a 3rd column that represents some kind of custom formatted line?

# Data directory

## original_cof_files
directory where the unmodified cof files are saved to when downloading them from the previews website.

_note: the MAY20.txt file is not available on the previews website as of 2023-06-23. I have tried to contact support via email._

## utf8_cof_files
directory where all cof files have been re-encoded as utf-8

_do we need to have a third directory (edited_cof_file), where we copy all the cof files to, where the utf8_cof_files would be the utf-8 encoded cof file that are un-edited and the edited_cof_file would contain all cof files with any potential edits applied (fixing of: malformed or incorrect data for example). That way we can do a diff between the utf8 and edited versions of the file?_ 

## cof_char_set_encodings
contains text files that list out what the probably text encodings of each cof file is.  
all cof files have been transcoded to utf-8 encoding (see `utf8_cof_files`)

```python
from charset_normalizer import from_fp

test_file = "data/original_cof_files/APR21.txt"
with open(test_file, "rb") as fh:
    r = from_fp(fh)

print(rb.encoding_aliases)
# outputs: ['1250', 'windows_1250']
```

compare output to those of the standard python list of encodings:  
https://docs.python.org/3/library/codecs.html#standard-encodings

| codec   | aliases                                                    | languages                  |
|---------|:-----------------------------------------------------------|----------------------------|
| ascii   | 646, us-ascii                                              | English                    |
| latin_1 | iso-8859-1, iso8859-1, <br/>8859, cp819, latin, latin1, L1 | Western Europe             |
| cp1250  | windows-1250                                               | Central and Eastern Europe |
| utf_8   | U8, UTF, utf8, cp65001                                     | all languages              |


