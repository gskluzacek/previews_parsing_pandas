# To Do's

# cof files

1. make changes to the program that re-encodes the files to utf8, we should be incrementally encoding newly downloaded files instead of re-doing all files again.
2. how to handle file edits. 
   3. I'm thinking we should maintain a separate folder for the edited version of the cof files. 
   4. But when processing from original --> to utf8 --> to edited, we need to be able to determine (and posible track) which cof files have edits applied to them and make sure not to over write these files.
   5. for an interim solution, I will just copy the un-modified utf8 cof file as MMMYY_txt (change the . to _) and then make the necessary changes to MMMYY.txt
3. when a heading appears twice: 
   4. for example
      4. PREVIEWS PUBLICATIONS      this would be lvl 1 hdg
      5. HALLOWEEN COMICFEST        this would be lvl 2 hdg
      6. HALLOWEEN MINI BUNDLES     this would be lvl 2 hdg
      7. PREVIEWS PUBLICATIONS      this would be lvl ??? hdg ???
   8. what should the 2nd occurance of the PREVIEWS PUBLICATIONS be level 1 or level 2?
      9. looking at the pdf of the order form, it appears that it should be level 2 because the text size of the heading is smaller...
      10. however, from a consistency stand point, this does not make sense. as in months where there is not any sub headings under PREVIEWS PUBLICATIONS the item lines under the header would be attached to the level 1 heading, but in the months where there are both a PREVIEWS PUBLICATIONS level 1 heading and a PREVIEWS PUBLICATIONS level 2 heading, then the items would be under a different level.
      11. from a consistency stand point, all the PREVIEWS PUBLICATIONS items should falll under the level 1 heading or the level 2 head, and not vary from month to month.
      12. I'm wondering in cases of a repeated heading, if would could use the convention of: when a heading is repeated, it does not mean that the repeated heading is a subheading, but rather a "reseting" to the level the heading first occured at.
      13. in the case of the above, this would mean the 2nd PREVIEWS PUBLICATIONS heading would be a level 1 heading.