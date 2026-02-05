import urllib.request
import json
import re

# Configuration
INSPIRE_QUERY = "author:Alessandro.Santini.2"
API_URL = "https://inspirehep.net/api/literature"
OUTPUT_FILE = "cv-sections/publications.tex"
MY_NAME_BOLD = r"\textbf{Santini, A.}"

def get_publications(query):
    """
    Fetch publications from InspireHEP using query.
    """
    params = {
        'sort': 'mostrecent',
        'size': '100',
        'q': query
    }
    query_string = urllib.parse.urlencode(params)
    url = f"{API_URL}?{query_string}"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data.get('hits', {}).get('hits', [])
    except urllib.error.URLError as e:
        print(f"Error fetching data: {e}")
        return []

def format_author_name(author_record):
    """
    Format author name as 'Surname, I. J.'
    """
    full_name = author_record.get('full_name', '')
    if ',' in full_name:
        parts = full_name.split(',')
        surname = parts[0].strip()
        given_names = parts[1].strip()
        
        initials = ""
        if given_names:
            # Split by space or dot to get all names
            names = re.split(r'[ .]+', given_names)
            initials_list = [n[0] + "." for n in names if n]
            initials = " ".join(initials_list)
            
        return f"{surname}, {initials}" if initials else surname
    return full_name

def is_me(author_formatted):
    """
    Check if the author is the user.
    """
    # Matches Santini, A. or Santini, A. B. etc.
    return "Santini, A" in author_formatted

def format_authors_list(authors_data):
    """
    Format the list of authors for the CV.
    Bold the user's name.
    """
    formatted_authors = []
    
    for author in authors_data:
        name = format_author_name(author)
        # Check if it's me (loose check for initials)
        if "Santini, A" in name: 
            # Force exact format user wants: Santini, A. (regardless of full name in record if user prefers A.)
            # Wait, user's existing file had "Santini, A." even if he is "Alessandro".
            # My format_author_name might produce "Santini, A."
            # But what if I have "Santini, A. J."? 
            # The existing file only has "Santini, A.". I will enforce "Santini, A." for the user myself.
            formatted_authors.append(MY_NAME_BOLD)
        else:
            formatted_authors.append(name)
    
    if not formatted_authors:
        return ""

    if len(authors_data) > 8: 
        try:
            my_index = -1
            for i, n in enumerate(formatted_authors):
                if MY_NAME_BOLD in n:
                    my_index = i
                    break
            
            if my_index == 0:
                return f"{formatted_authors[0]} et al."
            elif my_index > 0:
                 return f"{formatted_authors[0]} et al (including {MY_NAME_BOLD})"
            else:
                 return f"{formatted_authors[0]} et al."
        except IndexError:
             return f"{formatted_authors[0]} et al."
    
    return "; ".join(formatted_authors)

def get_best_title(titles):
    """
    Select the best title, prioritizing LaTeX/arXiv sources and avoiding HTML/MathML.
    """
    if not titles:
        return "No Title"
    
    # Priority: source='arXiv'
    for t in titles:
        if t.get('source') == 'arXiv':
            return t.get('title')
            
    # Fallback: check for $ symbols which imply math
    for t in titles:
        if '$' in t.get('title'):
            return t.get('title')
            
    # Fallback: first one that doesn't have <math>
    for t in titles:
        if '<math' not in t.get('title'):
            return t.get('title')
            
    # Final fallback: just take the first one
    return titles[0].get('title')

def format_entry(paper):
    """
    Format a single paper entry into LaTeX.
    """
    metadata = paper.get('metadata', {})
    
    # Title
    titles = metadata.get('titles', [])
    title = get_best_title(titles)

    # Authors
    authors = metadata.get('authors', [])
    author_str = format_authors_list(authors)
    
    # ArXiv info
    url = ""
    arxiv_eprints = metadata.get('arxiv_eprints', [])
    if arxiv_eprints:
        arxiv_id = arxiv_eprints[0].get('value')
        url = f"https://arxiv.org/abs/{arxiv_id}"
    else:
        # Fallback to DOI or Inspire link if no ArXiv
        dois = metadata.get('dois', [])
        if dois:
            url = f"https://doi.org/{dois[0].get('value')}"
        else:
            url = f"https://inspirehep.net/literature/{paper.get('id')}"

    # Journal Ref
    pub_info = metadata.get('publication_info', [])
    journal_ref = ", ArXiv preprint"
    
    if pub_info:
        info = pub_info[0]
        journal = info.get('journal_title')
        volume = info.get('journal_volume')
        
        if journal:
            journal_ref = f", {journal}"
            if volume:
                journal_ref += f" {volume}"
            if info.get('artid'):
                journal_ref += f", {info.get('artid')}"
            elif info.get('page_start'):
                journal_ref += f", {info.get('page_start')}"
    
    # LaTeX Entry
    entry =  "\t\\item{\n"
    entry += f"\t{author_str}\\\\\n"
    entry += f"\t\\pubsetstyle{{\\href{{{url}}}{{``{title}''}}}}\\skillsetstyle{{{journal_ref}}}\n"
    entry += "\t}\n"
    
    return entry

def main():
    print(f"Fetching publications for query: {INSPIRE_QUERY}")
    papers = get_publications(INSPIRE_QUERY)
    print(f"Found {len(papers)} publications.")
    
    latex_content = "\\cvsection{Publication record}\n\n\n\\begin{enumerate}\n\t%------------------------\n"
    
    for paper in papers:
        latex_content += format_entry(paper)
        
    latex_content += "\t%------------------------\n\\end{enumerate}\n"
    
    print(f"Writing to {OUTPUT_FILE}")
    with open(OUTPUT_FILE, "w") as f:
        f.write(latex_content)
    print("Done.")

if __name__ == "__main__":
    main()
