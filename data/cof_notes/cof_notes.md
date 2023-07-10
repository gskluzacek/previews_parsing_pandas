# cof file notes

## General

### the first header
normally the first header should be: PREVIEWS PUBLICATIONS  
but for Free Comic Book Day (FCBD), it will be (at least some of the times): FREE COMIC BOOK DAY

### Page Numbers

* We are using a page number of 0 (as a sentinel value) to indicate that there was no page number AND that the items came before the first listed page number. 
* A page number -1 is used to indicate a line is informational only (i.e., identification text lines) or does not actually apear in the catalog.
* in later issues, diamond has apparently started to prefix some page numbers with `M` for pages offering merchandise items.

_Note: there are some Heading lines that begin with the word `page` so we needed to add some logic to hanle that._

## FEB 2009

it appears that this file is has an extra tab between the item code and the title fields.

_for now I have just fixed line 5_

Before temporary fix
```text
SPOT	FEB09 0003		PREVIEWS #247 APRIL 2009 CUSTOMER ORDER FORM (Net)	04/01/09	SRP: PI	 = $	
```
After temporary fix
```text
SPOT	FEB09 0003	PREVIEWS #247 APRIL 2009 CUSTOMER ORDER FORM (Net)	04/01/09	SRP: PI	 = $	
```

## APR 2009
the file has the incorrect month of MAR in the BASIC (type 10) identification line (but does have the correct volume & volume issue number).

correcting line from:
```text
PREVIEWS MAR V19 #4
```

to:
```text
PREVIEWS APR V19 #4
```

## MAY 2009
the file has the incorrect month of MAR in the BASIC (type 10) identification line (but does have the correct volume & volume issue number).

correcting line from:
```text
PREVIEWS MAR V19 #5
```

to:
```text
PREVIEWS MAY V19 #5
```

## JUN 2009
the file has the incorrect month of MAR in the BASIC (type 10) identification line (but does have the correct volume & volume issue number).

correcting line from:
```text
PREVIEWS MAR V19 #6
```

to:
```text
PREVIEWS JUN V19 #6
```

## JUL 2009
the file has the incorrect month of MAR in the BASIC (type 10) identification line (but does have the correct volume & volume issue number).

correcting line from:
```text
PREVIEWS MAR V19 #7
```

to:
```text
PREVIEWS JUL V19 #7
```

## SEP 2009
the file has the incorrect month of MAR in the BASIC (type 10) identification line (but does have the correct volume & volume issue number).

correcting line from:
```text
PREVIEWS MAR V19 #9
```

to:
```text
PREVIEWS SEP V19 #9
```

## JAN 2010
the file has the incorrect month of MAR in the BASIC (type 10) identification line (but does have the correct volume & volume issue number).

correcting line from:
```text
PREVIEWS DEC V20 #1
```

to:
```text
PREVIEWS JAN V20 #1
```

## AUG 2010
the file has the incorrect month of MAR in the BASIC (type 10) identification line (but does have the correct volume & volume issue number).

correcting line from:
```text
PREVIEWS JULY V20 #8
```

to:
```text
PREVIEWS AUGUST V20 #8
```

## JAN 2012
the file has the incorrect month of MAR in the BASIC (type 10) identification line (but does have the correct volume & volume issue number).

correcting line from:
```text
PREVIEWS DECEMBER VOL. 22 #1
```

to:
```text
PREVIEWS JANUARY VOL. 22 #1
```

## DEC 2012
for the items listed under the `/ PREVIEWS PUBLICATIONS / FREE COMIC BOOK DAY` heading, there is no preceding page number. When consulting the pdf version of the file, there also was no page number. Since we don't have a hard copy of the Previews Catalog for the month of DEC 2012, we cannot validate whether or not these items actually appeared in the catalog.

Therefore, we are adding the follow PAGE line before the heading lines:
```text
PAGE 0
```

_We are using a page number of 0 (as a sentinal value) to indicate that there was no page number AND that the items came before the first listed page number. Note a page number -1 is used to indicate a line is informational only (i.e., identification text lines) or does not actually apear in the catalog._


## JAN 2013

#### change #1
the file has the incorrect month of MAR in the BASIC (type 10) identification line (but does have the correct volume & volume issue number).

correcting line from:
```text
PREVIEWS DECEMBER VOL. 23 #1
```

to:
```text
PREVIEWS JANUARY VOL. 23 #1
```

#### change #2
the PAGE number line appears after the first 2 headings, so we are moving it from after the heading lines of `/ PREVIEWS PUBLICATIONS / 	
FREE COMIC BOOK DAY`, to before them.

correcting line from _(including the preceding/succeeding lines for context)_:
```text

PREVIEWS PUBLICATIONS					
FREE COMIC BOOK DAY					
PAGE 30					
MERCHANDISE					
SPOT	JAN13 0053	FCBD 2013 ORANGE WRIST BAND (C: 1-0-0)	4/10/2013	MSRP: $1.99	 = $
```

to:
```text

PAGE 30					
PREVIEWS PUBLICATIONS					
FREE COMIC BOOK DAY					
MERCHANDISE					
SPOT	JAN13 0053	FCBD 2013 ORANGE WRIST BAND (C: 1-0-0)	4/10/2013	MSRP: $1.99	 = $
```

## AUG 2013
the PAGE number line appears after the first 1 heading, so we are moving it from after the heading lines of `/ PREVIEWS PUBLICATIONS`, to before it.

correcting line from _(including the preceding/succeeding lines for context)_:
```text

PREVIEWS PUBLICATIONS
PAGE 26
HALLOWEEN COMIC FEST
FULL-SIZE COMICS
KIDS	AUG13 0019	HCF 2013 SKYWARD INTO THE GRIM	10/09/13	SRP: PI	 = $	
```

to:
```text

PAGE 26
PREVIEWS PUBLICATIONS
HALLOWEEN COMIC FEST
FULL-SIZE COMICS
KIDS	AUG13 0019	HCF 2013 SKYWARD INTO THE GRIM	10/09/13	SRP: PI	 = $	
```



## JAN 2014
the file has the incorrect month of MAR in the BASIC (type 10) identification line (but does have the correct volume & volume issue number).

correcting line from:
```text
PREVIEWS DECEMBER VOL. 24 #1
```

to:
```text
PREVIEWS JANUARY VOL. 24 #1
```

## NOV 2014
the first page number line is malformed

correcting line from:
```text
GE 24
```

to:
```text
PAGE 24
```


## May 2020
apparently there is no May 2020 issue of previews. Instead a multi-month previews was issued in Jun 2020.

_For now, I'm just going to treat Jun 2020 as being only for Jun 2020, and assume there is no May 2020 issue._


## Jun 2020
apparently there is no May 2020 issue of previews. Instead a multi-month previews was issued in Jun 2020.

this resulted in the identification line for the Jun issue to be different than anything else encountered up to this point
```text
PREVIEWS MAY/JUNE 2020
ISSUE #380/381 (VOL. 30 #5/6)
```
Not sure if the May content is included in Jun's issue or if there just was no May content?

_For now, I'm just going to treat Jun 2020 as being only for Jun 2020, and assume there is no May 2020 issue._

modified ident lines as:
```text
PREVIEWS JUNE 2020
ISSUE 381 (VOL. 30 #6)
```

## MAR 2021
There appear to be some erroneous page numbers in the format of PAGE OF-{nn}. These are appearing in the Free comic book day (FCBD) section, and I'm not sure what these are for becuase I do not have the original Previews Catalog. Removing them for now.

updated lines from _(additional lines given for contect)_:
```text
PAGE 26
PREVIEWS PUBLICATIONS
FI	MAR21 0001	PREVIEWS #392 MAY 2021 (Net)	04/28/21	MSRP: $3.99	 = $	
PAGE 27
FI	MAR21 0002	MARVEL PREVIEWS VOL 05 #11 MAY 2021 (Net)	04/28/21	MSRP: $1.25	 = $	
FI	MAR21 0003	PREVIEWS #392 MAY 2021 CUSTOMER ORDER FORM (Net)	04/28/21	SRP: PI	 = $	
FI	MAR21 0007	GAME TRADE MAGAZINE #255 (Net)	04/28/21	SRP: PI	 = $	
PAGE OF-10
FREE COMIC BOOK DAY
OA	MAR21 0020	FCBD CINCH BAG (Net) (O/A)	07/14/21	MSRP: $1.99	 = $	
PAGE OF-11
OA	MAR21 0025	FCBD CAR WINDOW CLING (Net) (O/A)	07/14/21	SRP: $0.75	 = $	
OA	MAR21 0026	FCBD BLUE WRIST BAND (Net) (O/A) (C: 1-0-0)	07/14/21	SRP: $1.00	 = $	
OA	MAR21 0029	FCBD LANYARD (Net) (O/A)	07/14/21	SRP: $2.99	 = $	
PAGE 32
PREMIER PUBLISHERS
```

to:
```text
PAGE 26
PREVIEWS PUBLICATIONS
FI	MAR21 0001	PREVIEWS #392 MAY 2021 (Net)	04/28/21	MSRP: $3.99	 = $	
PAGE 27
FI	MAR21 0002	MARVEL PREVIEWS VOL 05 #11 MAY 2021 (Net)	04/28/21	MSRP: $1.25	 = $	
FI	MAR21 0003	PREVIEWS #392 MAY 2021 CUSTOMER ORDER FORM (Net)	04/28/21	SRP: PI	 = $	
FI	MAR21 0007	GAME TRADE MAGAZINE #255 (Net)	04/28/21	SRP: PI	 = $	
FREE COMIC BOOK DAY
OA	MAR21 0020	FCBD CINCH BAG (Net) (O/A)	07/14/21	MSRP: $1.99	 = $	
OA	MAR21 0025	FCBD CAR WINDOW CLING (Net) (O/A)	07/14/21	SRP: $0.75	 = $	
OA	MAR21 0026	FCBD BLUE WRIST BAND (Net) (O/A) (C: 1-0-0)	07/14/21	SRP: $1.00	 = $	
OA	MAR21 0029	FCBD LANYARD (Net) (O/A)	07/14/21	SRP: $2.99	 = $	
PAGE 32
PREMIER PUBLISHERS
```

