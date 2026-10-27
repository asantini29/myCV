import contextlib
import io
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generate_sections import (  # noqa: E402
    latex_text,
    main,
    render_contributed,
    render_education,
    render_invited,
    render_outreach,
)

INVITED = {
    "type": "invited",
    "event": "LISA AI Hackathon",
    "title": "Machine Learning in the Global Fit",
    "format": "discussion session",
    "location": "ESTEC, Noordwijk, The Netherlands",
    "date": "July 2026",
}
CONTRIBUTED = {
    "type": "contributed",
    "event": "26th SIGRAV Meeting",
    "title": "A flexible approach",
    "location": "Unimib, Milan, Italy",
    "date": "September 2025",
}
POSTER_2024 = {
    "type": "poster",
    "event": "15th LISA Symposium",
    "title": "Poster one",
    "location": "UCD, Dublin, Ireland",
    "date": "July 2024",
}
POSTER_2026 = {
    "type": "poster",
    "event": "16th LISA Symposium",
    "title": "Poster two",
    "location": "Baltimore (MD), USA",
    "date": "June 2026",
}
OUTREACH = {
    "event": "Long Night of Astronomy",
    "title": "Sounds of silence.",
    "location": "Berlin, Germany",
    "date": "September 2025",
    "language": "English",
    "description": "Speaker (webpage [here](https://a.org/x)).",
}
EDUCATION = {
    "degrees": [
        {
            "degree": "Ph.D. in Physics",
            "institution": "Max Planck Institute for Gravitational Physics",
            "location": "Potsdam, Germany",
            "dates": "2023--present",
            "details": ["**Thesis:** The LISA Global Fit"],
        },
        {
            "degree": "High School Diploma",
            "institution": "Liceo",
            "location": "Lissone (MB), Italy",
            "dates": "2013--2018",
            "details": ["**Final degree grade:** 97/100"],
            "website": False,
        },
    ],
    "internships": [
        {
            "degree": "Research visit",
            "institution": "Observatoire de la Côte d'Azur, 1 month",
            "location": "Nice, France",
            "dates": "May 2026",
        }
    ],
    "courses": [
        {
            "degree": "Data visualization workshop",
            "institution": "Visualize your science",
            "location": "Potsdam, Germany",
            "dates": "September 2026",
        }
    ],
}


class LatexTextTest(unittest.TestCase):
    def test_bold(self):
        self.assertEqual(latex_text("**Thesis:** X"), r"\textbf{Thesis:} X")

    def test_link(self):
        self.assertEqual(
            latex_text("(webpage [here](https://a.org/x))"),
            r"(webpage \href{https://a.org/x}{\underline{here}})",
        )

    def test_link_url_specials(self):
        self.assertEqual(
            latex_text("[t](https://a.org/a%20b#s)"),
            r"\href{https://a.org/a\%20b\#s}{\underline{t}}",
        )

    def test_escapes_outside_math(self):
        self.assertEqual(latex_text("R&D 5% #1"), r"R\&D 5\% \#1")

    def test_math_untouched(self):
        self.assertEqual(
            latex_text(r"$q-\chi_{\rm eff}$ & more"), r"$q-\chi_{\rm eff}$ \& more"
        )

    def test_dashes_and_unicode_untouched(self):
        self.assertEqual(
            latex_text("ETH -- Côte d'Azur, Don’t"), "ETH -- Côte d'Azur, Don’t"
        )


class RenderTest(unittest.TestCase):
    def test_format_suffix(self):
        self.assertIn(
            r"\emph{Machine Learning in the Global Fit} -- discussion session",
            render_invited([INVITED]),
        )

    def test_invited_only_in_conferences(self):
        out = render_invited([INVITED, CONTRIBUTED])
        self.assertIn("LISA AI Hackathon", out)
        self.assertNotIn("SIGRAV", out)

    def test_contributed_and_posters(self):
        out = render_contributed([INVITED, CONTRIBUTED, POSTER_2024])
        self.assertIn(r"\cvsubsection{Contributed Talks}", out)
        self.assertIn(r"\cvsubsection{Contributed Posters}", out)
        self.assertIn("SIGRAV", out)
        self.assertIn("15th LISA Symposium", out)
        self.assertNotIn("LISA AI Hackathon", out)

    def test_missing_location_is_empty_arg(self):
        out = render_invited(
            [{"type": "invited", "event": "E", "title": "T", "date": "July 2026"}]
        )
        self.assertIn("\\cventry\n{E}\n{\\emph{T}}\n{}\n{July 2026}\n{}", out)

    def test_order_preserved(self):
        out = render_contributed([POSTER_2024, POSTER_2026])
        self.assertLess(out.index("Poster one"), out.index("Poster two"))

    def test_outreach_language(self):
        self.assertIn(
            r"\shortstack[r]{September 2025 \\ Language: English}",
            render_outreach([OUTREACH]),
        )

    def test_outreach_description_link(self):
        self.assertIn(
            r"Speaker (webpage \href{https://a.org/x}{\underline{here}}).",
            render_outreach([OUTREACH]),
        )

    def test_education_details(self):
        self.assertIn(
            r"\item {\textbf{Thesis:} The LISA Global Fit}", render_education(EDUCATION)
        )

    def test_education_subsections(self):
        out = render_education(EDUCATION)
        self.assertIn(r"\cvsubsection{Internships}", out)
        self.assertIn("Observatoire de la Côte d'Azur, 1 month", out)
        self.assertIn(r"\cvsubsection{Extracurricular courses and workshops}", out)
        self.assertIn("Data visualization workshop", out)

    def test_website_flag_ignored_by_cv(self):
        self.assertIn("High School Diploma", render_education(EDUCATION))
        hidden = dict(INVITED, website=False)
        self.assertIn("LISA AI Hackathon", render_invited([hidden]))
        self.assertIn("Long Night", render_outreach([dict(OUTREACH, website=False)]))


class MainTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data = os.path.join(self.tmp.name, "data")
        self.out = os.path.join(self.tmp.name, "sections")
        os.makedirs(self.data)
        os.makedirs(self.out)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, text):
        with open(os.path.join(self.data, name), "w", encoding="utf-8") as f:
            f.write(text)

    def write_valid(self):
        self.write(
            "talks.yml",
            "- type: invited\n  event: E\n  title: T\n  date: July 2026\n",
        )
        self.write(
            "outreach.yml",
            "- event: O\n  title: T\n  date: May 2025\n  description: D\n",
        )
        self.write(
            "education.yml",
            "degrees:\n  - degree: PhD\n    institution: MPI\n"
            "    location: Potsdam\n    dates: 2023--present\n"
            "internships: []\ncourses: []\n",
        )

    def test_bad_yaml_exits_nonzero_and_names_file(self):
        self.write_valid()
        self.write("talks.yml", "- title: a: b\n")
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = main(data_dir=self.data, out_dir=self.out)
        self.assertEqual(code, 1)
        self.assertIn("talks.yml", err.getvalue())

    def test_unknown_talk_type_exits_nonzero(self):
        self.write_valid()
        self.write(
            "talks.yml",
            "- type: invted\n  event: E\n  title: T\n  date: July 2026\n",
        )
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = main(data_dir=self.data, out_dir=self.out)
        self.assertEqual(code, 1)
        self.assertIn("invted", err.getvalue())

    def test_writes_four_files_with_header(self):
        self.write_valid()
        self.assertEqual(main(data_dir=self.data, out_dir=self.out), 0)
        names = sorted(os.listdir(self.out))
        self.assertEqual(
            names,
            [
                "conferences-contributed.tex",
                "conferences.tex",
                "education.tex",
                "outreach.tex",
            ],
        )
        for name in names:
            with open(os.path.join(self.out, name), encoding="utf-8") as f:
                self.assertTrue(
                    f.readline().startswith("% Generated by generate_sections.py from data/")
                )

    def test_unchanged_file_not_rewritten(self):
        self.write_valid()
        main(data_dir=self.data, out_dir=self.out)
        path = os.path.join(self.out, "conferences.tex")
        os.utime(path, (0, 0))
        main(data_dir=self.data, out_dir=self.out)
        self.assertEqual(os.stat(path).st_mtime, 0)


if __name__ == "__main__":
    unittest.main()
