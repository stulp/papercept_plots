import re
import glob
import argparse
import datetime
import dateutil
import os
import numpy as np
import codecs
from matplotlib import pyplot as plt

# fmt: off

year = 2022
deadlines = {
    "start":     datetime.date(year, 3,  9),  # Editor has assigned papers to AEs
    "confirmed": datetime.date(year, 3, 20),  # AE should have >=2 reviewers per paper
    "submitted": datetime.date(year, 4, 20),  # Reviewers should have submitted reviews
    "report":    datetime.date(year, 5,  4),  # AE should have submitted reports
    "endorsed":  datetime.date(year, 5, 18),  # Editor should have endorsed the report
}
# Global variables are evil. But here  I found it handy to have global read-only settings
# at the beginning of the file. This could have been in a separate CSV file. But I want
# the Python script to be self-containing.

# fmt: on


class Paper:
    """Class representing one paper, which is parsed from the HTML file.
    """

    def __init__(self, number, ae, n_reviews, report):
        """
        Constructor.
        
        number -- paper number in papercept
        ae -- Name of the Associate Editor responsible for the paper
        n_reviews -- Counts for the number of review(er)s for this paper. A dict with the keys
        'requested'/'canceled'/'confirmed'/'submitted'
        report -- Whether the AE report was submitted or not.
        """
        self.number = number
        self.ae = ae
        self.n_reviews = n_reviews
        # papercept does not consider submitted reviews to be confirmed
        # But I do, because a submitted review does not mean it was "unconfirmed"
        self.n_reviews["confirmed"] += self.n_reviews["submitted"]
        self.report = report

    @classmethod
    def parse_paper(cls, string_html):
        """
        Initialize a paper by parsing it from a HTML string.
       
        string_html -- The HTML string (str)
        returns an object of class Paper
        """

        # Small inline function for more concise code
        def parse_field(string, regexp):
            match = re.compile(regexp).search(string)
            return match.group(1) if match else None

        papernumber = parse_field(string_html, r'<td class="c">(\d+)&nbsp;</td>')
        ae = parse_field(string_html, r"<td>.*? (.*?) \(\d+\)&nbsp;</td>")

        # Format in the HTML file
        # <font color="#0000FF">0</font>/           requested
        # <span style="color: #green">0</span>/     confirmed
        # <font color="#FF0000">0</font>/           canceled
        # 0)                                        submitted
        # fmt: off
        n_reviews = {}
        n_reviews["requested"] = int(parse_field(string_html, r'<font color="#0000FF">(\d+)'))
        n_reviews["canceled"]  = int(parse_field(string_html, r'<font color="#FF0000">(\d+)'))
        n_reviews["confirmed"] = int(parse_field(string_html, r'green">(\d+)</span'))
        n_reviews["submitted"] = int(parse_field(string_html, r"</font>/(\d+)"))
        # fmt: on

        regexp = r"(?:Under review)|(?:Decision pending)"
        match = re.compile(regexp).search(string_html)
        report = match.group(0) == "Decision pending" if match else False

        return Paper(papernumber, ae, n_reviews, report)


def parse_papers(filename_html):
    """Parse a file, and return the list of papers extracted from it.
    
    filename_html -- Name of file to parse.
    """

    lines = codecs.open(filename_html, "r", "iso-8859-1").readlines()

    papers = []
    cur_paper_string = None
    # Go through lines on-by-one. There are two states
    #   Not currently reading a paper: cur_paper_string = None
    #   Currently reading a paper:     cur_paper_string is a string
    for line in lines:

        if '<td class="cg">' in line:
            # Start reading the lines for a paper
            cur_paper_string = " "

        elif "</tr>" in line and cur_paper_string:
            # Reading the lines for a paper done: parse it
            paper = Paper.parse_paper(cur_paper_string)
            papers.append(paper)
            cur_paper_string = None  # Indicate that reading one paper is done

        elif cur_paper_string:
            # Currently reading a paper, add the next line.
            cur_paper_string += line

    return papers


def parse_date(filename_html):
    """Parse a file, and return the date associated with it.
    
    filename_html -- Name of file to parse.
    """

    match_date = re.search(r"\d{4}-\d{2}-\d{2}", filename_html).group()
    file_date = dateutil.parser.parse(match_date).date()
    return file_date


def my_pie(ax, N, colors, labels=None, size=12, labeldistance=0.7):
    """Plot a pie chart.

    ax -- Axis to plot on
    N -- The wedge sizes
    colors -- Colors for the wedges
    labels -- Labels to annotate the wedges (default: none)    
    size -- Font size of the labels (default: 12)
    labeldistance -- Relative distance of the labels from the center (default: 0.7)
    """

    if not labels:
        # If no labels are provided, the labels are 0,1,2, etc.
        labels = [f"{ii}" for ii in range(len(N))]

    # Add the number of papers per label
    labels = [f"{l}\n({N[ii]})" if l != "" else "" for ii, l in enumerate(labels)]

    # Set labels with associated value 0 to empty string to avoid clutter in the pie chart
    labels = [labels[ii] if N[ii] > 0 else "" for ii in range(len(N))]

    textprops = dict(horizontalalignment="center", verticalalignment="center")
    textprops["size"] = size

    ax.pie(
        N,
        labels=labels,
        labeldistance=labeldistance,
        textprops=textprops,
        colors=colors,
        startangle=90,
    )


def plot_papers(papers, file_date):
    """Plot the data for one file.

    papers -- A list of papers (list) 
    file_date -- Date for which this information is valid
    
    returns the fig on which the data was plotted.
    """
    n_papers = len(papers)

    # If deadline for submitting reviews has passed yet: plot reports also
    submitted_deadline_passed = file_date > deadlines["submitted"]

    # Determine number of columns
    n_cols = 2
    n_rows = 1
    if submitted_deadline_passed:
        n_cols = 4

    # Prepare figure
    ax_size = 4  # cm
    fig = plt.figure(figsize=(n_cols * ax_size, n_rows * ax_size))
    tdelta = file_date - deadlines["start"]
    # Date as title of the figure
    fig.suptitle(f"day: {tdelta.days}   date: {file_date}")

    #########################################################
    # Corporate Design (cd) colors from German Aerospace Center (DLR)
    # Example: cd['green'][0] => dark green
    cd = {}
    cd["gray"] = ["#696768", "#c8d3d9", "#e8ecef"]
    cd["blue"] = ["#007dc5", "#4098d3", "#94bce4"]
    cd["green"] = ["#70925b", "#94ab82", "#bdc9b0"]
    cd["yellow"] = ["#fdb913", "#ffcb66", "#ffdfa4"]
    cd["red"] = ["#d24442", "#de7a6b", "#ebad9f"]


    #########################################################
    # Bar chart over all sum over requested, canceled, confirmed, submitted

    # Compute sum over requested, canceled, confirmed
    # "Changed in version 3.7: Dictionary order is guaranteed to be insertion order."
    keys = list(papers[0].n_reviews.keys())
    sums = {key: sum([paper.n_reviews[key] for paper in papers]) for key in keys}

    # Ensure ordering by making a list and exclude 'submitted' (with :3)
    sums_list = [sums[key] for key in keys[:3]]

    x_ticks = [0, 1, 2]
    ax = fig.add_subplot(n_rows, n_cols, 1)
    cur_colors = [cd["blue"][1], cd["gray"][1], cd["green"][1]]
    patches = plt.bar(x_ticks, sums_list, width=0.8, color=cur_colors)
    keys = list(papers[0].n_reviews.keys())
    plt.xticks(x_ticks, keys[:3])
    plt.ylabel("#reviews")
    #plt.ylim([0, 250])
    ax.set_title("# requests (total)")


    #########################################################
    # Prepare bins and their centers for the below three charts
    max_reviews_per_paper = 4
    centers = list(range(0, max_reviews_per_paper + 1))
    bins = [x - 0.5 for x in range(0, max_reviews_per_paper + 2)]


    #########################################################
    # Pie char of #confirmed reviews vs. #papers
    ax = fig.add_subplot(n_rows, n_cols, 2)

    # submitted reviews are ones that have been confirmed (hopefully): take sum of both
    data_confirmed = [paper.n_reviews["confirmed"] for paper in papers]
    N, bins = np.histogram(data_confirmed, bins)

    deadline_color = "red" if file_date > deadlines["confirmed"] else "blue"
    # 0 or 1 reviewers: red or blue depending on whether overdue
    cur_colors = [cd[deadline_color][0], cd[deadline_color][1]]
    # 2,3,4,>= 5 reviews (more than 3 not recommended)
    cur_colors.extend([cd["green"][2], cd["green"][1], cd["green"][0], cd["green"][0]])

    my_pie(ax, N, cur_colors)
    ax.set_title("#reviewers confirmed\n(per paper)")


    #########################################################
    # The rest of this function is concerned with plotting the number of AE reports
    # Doing so is only really useful if the deadline for submitting reviews has passed
    if not submitted_deadline_passed:
        return fig

    #########################################################
    # Plot histogram of # submitted reviews vs. #papers
    ax = plt.subplot(n_rows, n_cols, 3)
    data_submitted = [paper.n_reviews["submitted"] for paper in papers]
    N, bins = np.histogram(np.array(data_submitted), bins)

    deadline_color = "red" if file_date > deadlines["submitted"] else "blue"
    cur_colors[0] = cd[deadline_color][0]
    cur_colors[1] = cd[deadline_color][1]
    
    my_pie(ax, N, cur_colors)
    ax.set_title("#reviews submitted\n(per paper)")

    #########################################################
    # Plot #reports vs. #papers
    n_insufficient = 0
    for n_reviews_submitted in data_submitted:
        n_insufficient += n_reviews_submitted < 2
    n_reports = sum([1 if paper.report else 0 for paper in papers])
    n_sufficient = n_papers - n_insufficient - n_reports
    data_reports = [n_insufficient, n_sufficient, n_reports]

    ax = plt.subplot(n_rows, n_cols, 4)
    labels = ["Insufficient\n#reviews", "Sufficient\n#reviews", "AE Report\ndone"]
    # Set labels with associated value 0 to empty string to avoid clutter in the pie chart
    labels = [
        labels[ii] if data_reports[ii] > 0 else "" for ii in range(len(data_reports))
    ]

    deadline_color1 = "red" if file_date > deadlines["submitted"] else "blue"
    deadline_color2 = "red" if file_date > deadlines["report"] else "blue"
    cur_colors = [cd[deadline_color1][0], cd[deadline_color2][1], cd["green"][1]]

    my_pie(ax, data_reports, cur_colors, labels, 10, 0.6)
    ax.axis("equal")
    ax.set_title("# AE reports\nsubmitted")

    return fig


def print_overdue_papers(papers, file_date):
    """Print papers which are overdue

    papers -- A list of papers (list) 
    file_date -- Date for which this information is valid
    """

    for phase in ["confirmed", "submitted"]:

        # Output AE names for papers with insufficient number of reviewers
        if file_date > deadlines[phase]:

            overdue_papers = [paper for paper in papers if paper.n_reviews[phase] < 2]

            if overdue_papers:
                print("Insufficient number of " + phase + " reviews:")
                for p in overdue_papers:
                    count = p.n_reviews[phase]
                    print(f"  {count} < 2  {p.number} \t{p.ae}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="Name of the input file or directory")
    parser.add_argument(
        "--output", type=str, default=None, help="Output directory name"
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite png files")
    # parser.add_argument("--show", action="store_true", help="always show the plots")
    args = parser.parse_args()

    if os.path.isfile(args.input):

        # Behavior for single file: show one plot and print overdue paper
        filename_html = args.input  # It's a single file.
        file_date = parse_date(filename_html)
        papers = parse_papers(filename_html)
        print_overdue_papers(papers, file_date)
        plot_papers(papers, file_date)
        plt.show()

    elif os.path.isdir(args.input):

        # It's a directory: process all html files in that directory
        input_dir = args.input
        regexp = os.path.join(input_dir, "*Submissions*.html")
        filenames = sorted(glob.glob(regexp))
        # If no output dir given (i.e. it is None), use input dir
        output_dir = args.output if args.output else input_dir

        # Supress annnoying warning
        plt.rcParams.update({"figure.max_open_warning": 0})

        # Behavior for multiple files: generate one png for each file
        for filename_html in filenames:
            print("'" + filename_html + "' =>", end="\t")
            file_date = parse_date(filename_html)
            # Determine output filename.
            tdelta = file_date - deadlines["start"]
            filename_png = os.path.join(output_dir, "plot%02d.png" % tdelta.days)

            if not args.overwrite and os.path.isfile(filename_png):
                print("skipping '" + filename_png + "', because it already exists.")
            else:
                papers = parse_papers(filename_html)
                fig = plot_papers(papers, file_date)
                print(filename_png)
                fig.savefig(filename_png)

    else:
        print("'" + args.input + "' does not exist. Doing nothing.")
