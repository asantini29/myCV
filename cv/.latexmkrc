# awesome-cv.cls, fontawesome.sty and fonts/ are shared and live at the repo
# root, one level up. Let kpathsea find them when building from this folder.
$ENV{'TEXINPUTS'} = '..//:' . ($ENV{'TEXINPUTS'} // '');
