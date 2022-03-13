# Papercept Plots for Editors

One of the perks of being on the Editorial Board of IEEE conferences is that is makes you feel 25 years younger, because papercept's browser-based interface gives one regular flashbacks to the 90s. However, to get a quick visual overview of progress, the interface for Editors is not ideal. The aim of this Python script is to parse and visualize the "Submissions overview" HTML page in papercept.

## Basic usage on one html file.

To visualize the status of the different papers, go to the "Submissions overview" view as an Editor (which lists all the papers), and download that HTML file. Then call the following:

```
python3 papercept_plot.py 'Submissions overview.html'
```

During the first phase of the process (finding reviewers), this plots the following:

plot_2021-03-21.png



It will also list the Associate Editors with overdue papers (e.g. not enough confirmed reviewers, not enough submitted reviews, etc.), for instance:

```
Insufficient number of confirmed reviews:
  1 < 2  167    John
  1 < 2  356    John
  1 < 2  1534   Jane
  0 < 2  1560   Jane
```

During the second phase of the process (submitting reviews and writing reports), the script plots the following:

plot_2021-04-30.png


## Rationale

This script grew each year from a few lines of code in my first year as Editor. My motivation for doing so was:
* Not all Associate Editors are punctual and/or responsive (there is definitely a correlation...). The anonymized graphs above make it clear to the stragglers that they are straggling. It's a way to nudge them into action, rather than having to twist arms or send individualized e-mails.
* Being an Editor for a big conference with many papers can become a bit enumerative so to speak. Tuning the script over the years made it a bit more fun.

Essentially, it is a gamification of the reviewing process.

## Batch mode

For the historically inclined, one may save intermediate results as pngs. To do this, the directory must contain multiple files with the following naming convention:

```
2021-03-13_Submissions_overview.html
2021-03-16_Submissions_overview.html
2021-03-19_Submissions_overview.html
2021-03-20_Submissions_overview.html
2021-03-21_Submissions_overview.html
```

To generate on PNG file for each HTML file, call `papercept_plot` on that directory:

```
python3 papercept_plot.py html/
```

## Inofficial guide for Associate Editors

For what it's worth, here is my strategy for finding reviewers. Please note that this is my personal strategy based on some years of experience as AE, not IEEE policy. In any case, read the official info for AEs before reading this. 

Here are the phases I go through.

* Phase 0 (1 day): Go through the papers, use a summary reject if necessary (due to plagiarism, the paper having only 1 pages, etc.)
* Phase 1 (2 days, ask 2-3 people): PIN-POINTING. I ask people you know, and who might really be interested. I bug them over e-mail to reply quickly. In papercept, you can look for reviewers based on last name.
* Phase 2 (3 days, ask 2-3 more people): WIDENING THE HORIZON. Go through the citations of the paper, and ask people that are cited. You may not know them, but at least the topic will fit (be careful for conflicts of interest at this point; people tend to cite themselves or direct colleagues a lot). Again, find the reviewers by last name in papercept.
* Phase 3 (3 days, ask 2-3 more people): ANYTHING GOES. Use the papercept search functionality to search by keyword. Look for reviewers with only a few, but matching keywords. It is more likely they will be interested in the topic than somebody with 100 keywords selected (Bayes' law).
* Phase 4: HELP! Ask the people you know again. Ask for favors, twist arms, etc. Ask your Editor for help.

The main thing is to avoid situations where you only ask 3 reviewers, wait two weeks, and nothing happens. It's better to ask 8 people, and then thankfully cancel some if more than 3 accept. For example, sometimes, I will ask 3 people from the same group, but cancel the other 2 once the first one has accepted (for reasons of diversity, it's not good to have multiple people form the same group).

With two reviewers for a paper, you risk the chance that their recommendations diverge. This can irritating, because the AE has to break the tie, and this basically means writing another review, or finding a third reviewer last-minute. But I also use three reviewers for one paper sparingly, as I think it is a waste of resources (so many papers to review already!). My strategy: if I think a paper is obviously bad (but not bad enough for a summary reject) or obviously good, I get two reviewers. If I am not so sure, I get three. 

In general, junior researchers will be more diligent and punctual but less secure in their reviews ("Borderline" recommendations). Note that in the end, Editors only allow you to assign "Borderline" in exceptional cases. With ~100 papers, Editors do not have time to look at them and decide whether to accept or reject. Senior researchers tend to give clearer recommendations ("Definite Accept"), but I've also noticed a tendency for seniors to be late more often, or sometimes not submit the review at all.  Oh yes, that top professor whom you were surprised accepted your invitation; well, that professor may not submit their review or reply to your e-mails :-(
 