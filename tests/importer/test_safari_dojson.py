import os

from cds_dojson.marc21.utils import create_record

from cds_ils.importer.providers.safari.safari import model

marcxml = (
    """<collection xmlns="http://www.loc.gov/MARC21/slim">"""
    """<record>{0}</record></collection>"""
)


def check_transformation(marcxml_body, json_body):
    """Check transformation."""
    blob = create_record(marcxml.format(marcxml_body))
    record = {}
    record.update(**model.do(blob, ignore_missing=True))

    expected = {}
    expected.update(**json_body)
    assert record == expected


def test_safari_transformation(app):
    """Test safari record json translation."""

    dirname = os.path.join(os.path.dirname(__file__), "data")
    with open(os.path.join(dirname, "safari_record.xml"), "r") as fp:
        example = fp.read()

    with app.app_context():
        check_transformation(
            example,
            {
                "document_type": "BOOK",
                "_eitem": {
                    "urls": [
                        {
                            "description": "e-book",
                            "value": "https://learning.oreilly.com"
                                     "/library/view/-/9780814415467/?ar",
                        },
                    ]
                },
                "_serial": [
                    {
                        "title": "For dummies",
                        "volume": "1",
                    }
                ],
                "abstract": "A complete tool kit for handling "
                            "disciplinary problems in a "
                            "fair, responsible, and legally defensible way.",
                "agency_code": "OCoLC",
                "alternative_identifiers": [
                    {"scheme": "SAFARI", "value": "9780814415467"}
                ],
                "alternative_titles": [
                    {
                        "type": "SUBTITLE",
                        "value": "A Guide to Progressive Discipline and " "Termination",
                    }
                ],
                "authors": [
                    {
                        "full_name": "Falcone, Paul",
                        "roles": ["AUTHOR"],
                        "type": "PERSON",
                    },
                    {
                        "full_name": "Murray, Andy",
                        "roles": ["AUTHOR"],
                        "type": "PERSON",
                    },
                    {
                        "full_name": "Bennett, Nigel",
                        "roles": ["AUTHOR"],
                        "type": "PERSON",
                    },
                ],
                "edition": "2nd",
                "identifiers": [
                    {
                        "material": "PRINT_VERSION",
                        "scheme": "ISBN",
                        "value": "9780814415467",
                    },
                    {
                        "material": "DIGITAL",
                        "scheme": "ISBN",
                        "value": "9781801073141",
                    },
                    {
                        "material": "DIGITAL",
                        "scheme": "ISBN",
                        "value": "9780814415474",
                    },
                ],
                "languages": ["ENG"],
                "provider_recid": "9780814415467",
                "imprint": {
                    "publisher": "TSO (The Stationary Office)",
                    "place": "London",
                },
                "keywords": [
                    {"source": "SAFARI", "value": "Project management"},
                    {'source': 'SAFARI',
                     'value': 'Gestion de projet'},
                    {'source': 'SAFARI',
                     'value': 'Project other'},

                ],
                "number_of_pages": "399",
                "publication_year": "2009",
                "subjects": [
                    {"scheme": "LOC", "value": "HD69.P75"},
                    {"scheme": "DEWEY", "value": "658.4/04"},
                ],
                "title": "101 Sample Write-Ups for "
                         "Documenting Employee Performance Problems",
            },
        )


def test_safari_additional(app):
    """Test additional fields."""
    dirname = os.path.join(os.path.dirname(__file__), "data")
    with open(os.path.join(dirname, "safari_record2.xml"), "r") as fp:
        example = fp.read()

    with app.app_context():
        check_transformation(
            example,
            {
                "document_type": "BOOK",
                "provider_recid": "on1291562831",
                "alternative_identifiers": [
                    {"scheme": "SAFARI", "value": "on1291562831"}
                ],
                'alternative_titles': [
                    {'type': 'ALTERNATIVE_TITLE',
                     'value': 'Harvard Business Review guide to managing '
                              'flexible work'},
                    {'type': 'ALTERNATIVE_TITLE',
                     'value': 'Managing flexible work'}],

                "agency_code": "OCoLC",
                "identifiers": [
                    {"scheme": "ISBN", "value": "9781647823337", "material": "DIGITAL"},
                    {
                        "scheme": "ISBN",
                        "value": "1647823331",
                        "material": "PRINT_VERSION",
                    },
                    {
                        "scheme": "ISBN",
                        "value": "9781647823320",
                        "material": "PAPERBACK",
                    },
                ],
                "subjects": [
                    {"scheme": "LOC", "value": "HD5109"},
                    {"scheme": "DEWEY", "value": "331.25/72"},
                ],
                "title": "HBR guide to managing flexible work",
                "publication_year": "2022",
                "imprint": {
                    "publisher": "Harvard Business Review Press",
                    "place": "Boston, Massachusetts",
                },
                "_serial": [{"title": "Harvard business review guides"}],
                "abstract": '"The 9-to-5 office routine no longer exists. '
                            'Many employees have the option to\n'
                            "                work anywhere, any "
                            "time. But how do you find "
                            "the flexible arrangement "
                            "that's right for you? And how do\n               "
                            " you manage a team when they're all "
                            "working in different places and on different schedules? "
                            "The HBR Guide\n                "
                            "to Managing Flexible Work has the answers. "
                            "Filled with tips, advice, and examples, this "
                            "book helps\n                individual contributors "
                            "and managers alike assess the "
                            "trade-offs that come with flexible "
                            "work options,\n               "
                            " advocate for the arrangement that works for them, "
                            "and remain productive and "
                            "connected to team members at\n               "
                            " the same time. You'll learn to: "
                            "identify key job responsibilities and when and "
                            "where each one can be\n       "
                            "         done, establish the best arrangements for "
                            "yourself and your team, "
                            "create the conditions for success,\n                "
                            "stay connected and visible, "
                            "no matter when or where you work, win support for "
                            "your projects and ideas,\n          "
                            '      and keep people engaged, both in '
                            'person and virtually"--',
                "keywords": [
                    {"source": "SAFARI", "value": "Flexible work arrangements"},
                    {"source": "SAFARI", "value": "Virtual work teams"},
                    {"source": "SAFARI", "value": "Virtual work"},
                    {"source": "SAFARI", "value": "Telecommuting"},
                    {"source": "SAFARI", "value": "Success in business"},
                    {"source": "SAFARI", "value": "Industrial management"},
                    {'source': 'SAFARI',
                     'value': 'Conditions de travail flexibles'},
                    {'source': 'SAFARI',
                     'value': 'Équipes virtuelles'},
                    {'source': 'SAFARI',
                     'value': 'Travail virtuel (Mécanique analytique'},
                    {'source': 'SAFARI',
                     'value': 'Succès dans les affaires'},
                    {'source': 'SAFARI',
                     'value': "Gestion d'entreprise"},
                ],

                "_eitem": {
                    "urls": [
                        {
                            "description": "e-book",
                            "value": "https://learning.oreilly.com/library/view/-/9781663718914/?ar",  # noqa
                        }
                    ]
                },
                "table_of_content": [
                    "Getting Started:",
                    "A Primer on True Flexibility: Prioritize company and "
                    "employee needs equally /",
                    "What Mix of WFH and Office Time Is Right for You?: Make "
                    "decisions based on your\n"
                    "                productivity levels /",
                    "Set a Hybrid Schedule That Works for You: When are you "
                    "most motivated? /",
                    "Making the Ask:",
                    "How to Negotiate a Remote Arrangement with Your Boss: "
                    "Approach the conversation with\n"
                    "                an open mindset /",
                    "Adventures in Alternative Work Arrangements: Tips for "
                    "parents-that apply to everyone\n"
                    "                /",
                    "Asking Your Boss For a 4-Day Workweek: You don't have "
                    "to work a certain number of\n"
                    "                hours to be productive /",
                    "Getting Work Done:",
                    "How to Get More Done in Less Time: Be intentional with "
                    "the time you have /",
                    "Staying Focused When You're Working From Home: Set "
                    "boundaries-and stick to them /",
                    "Being Mindful in an Online Working World: Block out the "
                    "noise of your virtual\n"
                    "                reality /",
                    "How to Leave Work at Work: Whether you're leaving the "
                    "office or working from home\n"
                    "                /",
                    "Staying Connected:",
                    "Did You Get My Slack/Email/Text?: Establish your team's "
                    "communication norms /",
                    "Staying Visible When Your Team Is In the Office-and "
                    "You're Not: Stand out as a\n"
                    "                valued contributor no matter how many "
                    "hours you work /",
                    "Working on a Team Spread Across Time Zones: What to do "
                    "when your team is online at\n"
                    "                different times /",
                    "How to Stay Connected to Your Work Friends: Principles "
                    "for when time and proximity\n"
                    "                are not on your side /",
                    "New to the Team? Here's How to Build Trust (Remotely): "
                    "Advice for creating\n"
                    "                connections whenever or wherever you "
                    "work /",
                    "Making the Most of Meetings:",
                    "What It Takes to Run a Great Hybrid Meeting: Eight best "
                    "practices /",
                    "When Do We Actually Need to Meet in Person?: Decide "
                    "what you need to get out of\n"
                    "                meeting face-to-face /",
                    "How to Nail a Hybrid Presentation: Involve the remote "
                    "participants /",
                    "Managing Your Flexible Team:",
                    "Setting Flexible Schedules with Your Team-Fairly: Let "
                    "your team pick a schedule that\n"
                    "                suits their needs /",
                    "The Downside of Flex Time: Protect your team from an "
                    '"always on" culture\n'
                    "                /",
                    "What Psychological Safety Looks Like in a Hybrid "
                    "Workplace: Five steps to create an\n"
                    "                inclusive environment /",
                    "Giving Feedback When You're Not Face-to-Face: Be "
                    "sympathetic, but firm /",
                    "Tips for Managing an Underperformer: Whether you're at "
                    "home, in the office, or half\n"
                    "                the world away /",
                ],
            },
        )


def test_safari_additional2(app):
    """Test additional fields."""
    dirname = os.path.join(os.path.dirname(__file__), "data")
    with open(os.path.join(dirname, "safari_record3.xml"), "r") as fp:
        example = fp.read()
    with app.app_context():
        check_transformation(
            example,
            {'document_type': 'BOOK',
             'provider_recid': 'on1311516685',
             'alternative_identifiers': [
                 {'scheme': 'SAFARI', 'value': 'on1311516685'}],
             'agency_code': 'OCoLC', 'identifiers': [
                {'scheme': 'ISBN', 'value': '9784873119144', 'material': 'DIGITAL'},
                {'scheme': 'ISBN', 'value': '4873119146', 'material': 'DIGITAL'}],
             'languages': ['JPN'],
             'subjects': [{'scheme': 'LOC', 'value': 'QA76.9.H85'},
                          {'scheme': 'DEWEY', 'value': '004.019'}],
             'authors': [{'full_name': 'Wendel, Stephen', 'roles': ['AUTHOR'],
                          'type': 'PERSON'}, {'full_name': 'Takeyama, Masanao',
                                              'roles': ['AUTHOR'],
                                              'type': 'PERSON'},
                         {'full_name': 'Aijima, Masaki', 'roles': ['AUTHOR'],
                          'type': 'PERSON'}], 'alternative_titles': [{
                'value': 'shinrigaku to kōdō keizaigaku o purodakuto dezain\n '
                         '               ni katsuyōsuru',
                'type': 'SUBTITLE'},
                {
                    'value': 'Designing for behavior change :',
                    'type': 'ALTERNATIVE_TITLE'},
                {
                    'value': 'applying psychology and behavioral economics',
                    'type': 'SUBTITLE'}],
             'title': 'Kōdō o kaeru dezain', 'edition': 'shohan',
             'publication_year': '2020',
             'imprint': {'publisher': 'Orairī Japan',
                         'place': 'Tōkyō-to Shinjuku-ku'},
             'number_of_pages': '464',
             'abstract': "Abstract",
             'keywords': [
                 {'source': 'SAFARI', 'value': 'Human-computer interaction'},
                 {'source': 'SAFARI', 'value': 'User-centered system design'},
                 {'source': 'SAFARI',
                  'value': 'Conception participative (Conception de systèmes'}],
             '_eitem':
                 {'urls':
                      [{'description': 'e-book',
                        'value':
                            'https://learning.oreilly.com/library/view/-/9784873119144/?ar'}]}}  # noqa
        )
