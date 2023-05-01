
import hashlib
import logging
from fpdf import FPDF
from typing import  Optional
import os


from tkinter import *
import webbrowser

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer

from sumy.utils import get_stop_words
import arxiv


def hacky_hash( some_string):
    hash = hashlib.md5(some_string.encode("utf-8")).hexdigest()
    return hash

def get_paper_metadata(filename):
    return paper_lookup[filename]

def summarize(string, num_sentence=3):
    """
    Summarize a sentence with sumy
    """
    lang = 'english'
    tknz = Tokenizer(lang)
    stemmer = Stemmer(lang)
    summarizer = Summarizer(stemmer)

    parser = PlaintextParser(string, tknz)
    parser.stop_word = get_stop_words(lang)
    summ_string = ''
    for sentence in summarizer(parser.document, num_sentence):
        summ_string += str(sentence) + ' '
    return summ_string

def format_arxiv(article, do_summarize=True):
    """
    Format an arxiv article info into a response string
    Optionally summarize the abstract with sumy
    """
    msg = 'Title: %s\n' % article.title
    authors = [a.name for a in article.authors]
    msg += 'Authors: %s\n' % ', '.join(authors)
    abstract = ' '.join(article.summary.split('\n'))
    if do_summarize:
        abstract = summarize(abstract)
    msg += '\nAbstract (auto-summarized): ' + abstract + '\n\n'
    msg += 'PDF: %s' % article.pdf_url
    return msg

def load_data(search_query: str, papers_dir: Optional[str] = "..\papers", max_results: Optional[int] = 50,search_criterion: Optional[int] = 0):
    """Search for a topic on Arxiv, download the PDFs of the top results locally, then read them.

    Args:
        search_query (str): A topic to search for (e.g. "Artificial Intelligence").
        papers_dir (Optional[str]): Locally directory to store the papers
        max_results (Optional[int]): Maximum number of papers to fetch.

    """
    # find papers
    #            import arxiv
    if search_criterion == 0:
        sort_criterion = arxiv.SortCriterion.Relevance

    if search_criterion == 1:
        sort_criterion = arxiv.SortCriterion.LastUpdatedDate

    if search_criterion == 2:
        sort_criterion = arxiv.SortCriterion.SubmittedDate

    arxiv_search = arxiv.Search(
        query=search_query,
        id_list=[],
        max_results=max_results,
        sort_by=sort_criterion,
    )
    search_results = list(arxiv_search.results())
    #        logging.debug(f"> Successfully fetched {len(search_results)} papers")

    # create directory
    papers_dir = os.getcwd()   #"C:/Users/Elias/PycharmProjects/ArxivApp/paper"
    papers_dir = papers_dir+"\paper"

    if not os.path.exists(papers_dir):
        os.makedirs(papers_dir)

    else:
        # Delete downloaded papers
        try:
            for f in os.listdir(papers_dir):
                os.remove(os.path.join(papers_dir, f))
                logging.debug(f"> Deleted file: {f}")
            os.rmdir(papers_dir)
            logging.debug(f"> Deleted directory: {papers_dir}")
            os.makedirs(papers_dir)
        except OSError:
            print("Unable to delete files or directory")

    paper_lookup = {}
    for paper in search_results:
        # Hash filename to avoid bad charaters in file path
        filename = f"{hacky_hash(paper.title)}.pdf"

        #            print(os.path.join(papers_dir, filename))
        # filename = f"{paper.title}.pdf"
        paper_lookup[os.path.join(papers_dir, filename)] = {
            "Title of this paper": paper.title,
            "Authors": (", ").join([a.name for a in paper.authors]),
            "Date published": paper.published.strftime("%m/%d/%Y"),
            "URL": paper.entry_id,
            "summary": paper.summary.encode("utf-8"),
        }

        paper.download_pdf(dirpath=papers_dir, filename=filename)










    # save FPDF() class into
    # a variable pdf
    pdf = FPDF()

    # Add a page
    pdf.add_page()

    # set style and size of font
    # that you want in the pdf
    pdf.set_font("Arial", size=15)

    # insert the texts in pdf
    for paper in search_results:
       # print(summarize(paper.summary, num_sentence=3))
        abstract = paper.summary
        abstract = summarize(abstract)
        link = paper.pdf_url
        authors = (", ").join([a.name for a in paper.authors])
        authors = authors.encode("utf-8")
        pub_paper = paper.published.strftime("%m/%d/%Y")
        d = f"Title: {paper.title}\n\nAuthors:{authors}\n\nDate:{pub_paper}\n\nAbstract: {abstract}\nLink:{link}\n\n"
        pdf.multi_cell(0, 10, txt= d, border = 0)
 #       pdf.add_page()



    # save the pdf with name .pdf
    pdf.output(papers_dir+"/abstracts.pdf")







# GUI
root = Tk()
root.title("Arxiv Text and Abstracts Query in PDF format")
root.geometry('600x200')


FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"



# Send function
def send():
    global index
    txt.insert(END, "\n")
    send = "You: " + e.get()
    txt.insert(END, "\n" + send)

    user = e.get().lower()

    response = str(index.query(user))
    txt.insert(END, "\n")

######	response = response.replace('.', '\n')
    string = response.strip()
    txt.insert(END, f'\nBot:{string}')

    e.delete(0, END)

def load_query():
     query = str(entry_query.get())
     max_query = int(entry_files.get())

     dummy = radio_query.get()
     if dummy == 'Relevance':
         search_query_int = 0

     if dummy == "LastUpdated":
         search_query_int = 1

     if dummy == "SubmittedDate":
         search_query_int = 2



def produce_files():
    query =  str(entry_query.get())
    max_query = int(entry_files.get())



    # set up the type of query
    dummy = str(radio_query.get())
    if dummy == 'Relevance':
        search_query_int = 0

    if dummy == "LastUpdated":
        search_query_int = 1

    if dummy == "SubmittedDate":
        search_query_int = 2


    load_data(search_query=query,
              max_results=max_query, search_criterion = search_query_int)


def open_browser(e):
    webbrowser.open_new("http://arxiv.org")




my_frame = Frame(root)
my_frame.pack()

label_query = Label(my_frame, text="Query:",font=FONT)
label_query.grid(row=0,column=0,padx=(60,0))

entry_query = Entry(my_frame,font=FONT)
entry_query.grid(row=0,column=1)


my_frame2 = Frame(root)
my_frame2.pack()
load_button_produce = Button(my_frame2, text='Load for Produce files',font=FONT, command= produce_files )
load_button_produce.pack(side=RIGHT)

label_files =  Label(my_frame, text="No Files:",font=FONT)
label_files.grid(row=1,column=0,padx=(60,0))

entry_files = Entry(my_frame,font=FONT)
entry_files.grid(row=1,column=1)

MODE = [
    ("Relevance", "Relevance"),
    ("LastUpdated", "LastUpdated"),
    ("SubmittedDate", "SubmittedDate")
]
radio_query= StringVar()
radio_query.set("Relevance")

search_criterion =  Label(my_frame, text="Search Criterion:",font=FONT)
search_criterion.grid(row=2,column=0)

i = 1
global radios
radios = [];
for text, mode in MODE:
    i = i + 1
    radio = Radiobutton(my_frame, text=text,font=FONT_BOLD,  variable=radio_query, value=mode)
    radio.grid(row=i, column=1,sticky=W)
    radios.append(radio)


my_frame1 = Frame(root)
my_frame1.pack(pady=(0,0))


# Set up Menu
my_menu = Menu(root)
root.configure(menu=my_menu)

options_menu = Menu(my_menu, tearoff=False)
my_menu.add_cascade(label="Arxiv Papers", menu=options_menu)
options_menu.add_command(label= "Arxiv Browser ", command=lambda: open_browser(1) )



root.mainloop()
