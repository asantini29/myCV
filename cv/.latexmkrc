# awesome-cv.cls, fontawesome.sty and fonts/ are shared and live at the repo
# root, one level up. Let kpathsea find them when building from this folder.
$ENV{'TEXINPUTS'} = '..//:' . ($ENV{'TEXINPUTS'} // '');

# Talks, outreach and education sections are generated from ../data/*.yml
system('python3', '../generate_sections.py') == 0
    or die "generate_sections.py failed; fix the error above\n";
