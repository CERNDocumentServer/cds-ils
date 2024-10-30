import os

import pytest
from cds_dojson.marc21.utils import create_record

from cds_ils.importer.errors import UnrecognisedImportMediaType
from cds_ils.importer.providers.safari.safari import model

marcxml = (
    """<collection xmlns="http://www.loc.gov/MARC21/slim">"""
    """<record>{0}</record></collection>"""
)


def check_transformation(marcxml_body, json_body):
    """Check transformation."""
    blob = create_record(marcxml.format(marcxml_body))
    init_fields = {}
    leader_tag = blob.get("leader", [])
    if "am" in leader_tag:
        init_fields.update({"_eitem": {"_type": "e-book"}})
    elif "im" in leader_tag or "jm" in leader_tag:
        init_fields.update({"_eitem": {"_type": "audiobook"}})
    elif "gm" in leader_tag:
        init_fields.update(
            {"document_type": "MULTIMEDIA", "_eitem": {"_type": "video"}}
        )
    else:
        raise UnrecognisedImportMediaType(leader_tag)

    record = {}
    record.update(**model.do(blob, ignore_missing=True, init_fields=init_fields))

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
                    "_type": "e-book",
                    "urls": [
                        {
                            "description": "e-book",
                            "value": "https://learning.oreilly.com"
                            "/library/view/-/9780814415467/?ar",
                        },
                    ],
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
                "languages": ["ENG", "ITA"],
                "provider_recid": "9780814415467",
                "imprint": {
                    "publisher": "TSO (The Stationary Office)",
                    "place": "London",
                },
                "keywords": [
                    {"source": "SAFARI", "value": "Project management"},
                    {"source": "SAFARI", "value": "Gestion de projet"},
                    {"source": "SAFARI", "value": "Project other"},
                ],
                "number_of_pages": "399",
                "publication_year": "2009",
                "subjects": [
                    {"scheme": "LOC", "value": "HD69.P75"},
                    {"scheme": "LOC", "value": "HD69.P86"},
                    {"scheme": "DEWEY", "value": "658.4/04"},
                ],
                "title": "101 Sample Write-Ups for "
                "Documenting Employee Performance Problems",
            },
        )


def test_safari_additional(app):
    """Test additional fields and missing language, default to ENG."""
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
                "alternative_titles": [
                    {
                        "type": "ALTERNATIVE_TITLE",
                        "value": "Harvard Business Review guide to managing "
                        "flexible work",
                    },
                    {"type": "ALTERNATIVE_TITLE", "value": "Managing flexible work"},
                ],
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
                "languages": ["ENG"],
                "imprint": {
                    "publisher": "Harvard Business Review Press",
                    "place": "Boston, Massachusetts",
                },
                "_serial": [{"title": "Harvard business review guides"}],
                "abstract": '"The 9-to-5 office routine no longer exists. '
                "Many employees have the option to\n"
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
                "      and keep people engaged, both in "
                'person and virtually"--',
                "keywords": [
                    {"source": "SAFARI", "value": "Flexible work arrangements"},
                    {"source": "SAFARI", "value": "Virtual work teams"},
                    {"source": "SAFARI", "value": "Virtual work"},
                    {"source": "SAFARI", "value": "Telecommuting"},
                    {"source": "SAFARI", "value": "Success in business"},
                    {"source": "SAFARI", "value": "Industrial management"},
                    {"source": "SAFARI", "value": "Conditions de travail flexibles"},
                    {"source": "SAFARI", "value": "Équipes virtuelles"},
                    {
                        "source": "SAFARI",
                        "value": "Travail virtuel (Mécanique analytique",
                    },
                    {"source": "SAFARI", "value": "Succès dans les affaires"},
                    {"source": "SAFARI", "value": "Gestion d'entreprise"},
                ],
                "_eitem": {
                    "_type": "e-book",
                    "urls": [
                        {
                            "description": "e-book",
                            "value": "https://learning.oreilly.com/library/view/-/9781663718914/?ar",  # noqa
                        }
                    ],
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
            {
                "document_type": "BOOK",
                "provider_recid": "on1311516685",
                "alternative_identifiers": [
                    {"scheme": "SAFARI", "value": "on1311516685"}
                ],
                "agency_code": "OCoLC",
                "identifiers": [
                    {"scheme": "ISBN", "value": "9784873119144", "material": "DIGITAL"},
                    {"scheme": "ISBN", "value": "4873119146", "material": "DIGITAL"},
                ],
                "languages": ["JPN"],
                "subjects": [
                    {"scheme": "LOC", "value": "QA76.9.H85"},
                    {"scheme": "DEWEY", "value": "004.019"},
                ],
                "authors": [
                    {
                        "full_name": "Wendel, Stephen",
                        "roles": ["AUTHOR"],
                        "type": "PERSON",
                    },
                    {
                        "full_name": "Takeyama, Masanao",
                        "roles": ["AUTHOR"],
                        "type": "PERSON",
                    },
                    {
                        "full_name": "Aijima, Masaki",
                        "roles": ["AUTHOR"],
                        "type": "PERSON",
                    },
                ],
                "alternative_titles": [
                    {
                        "value": "shinrigaku to kōdō keizaigaku o purodakuto dezain\n "
                        "               ni katsuyōsuru",
                        "type": "SUBTITLE",
                    },
                    {
                        "value": "Designing for behavior change :",
                        "type": "ALTERNATIVE_TITLE",
                    },
                    {
                        "value": "applying psychology and behavioral economics",
                        "type": "SUBTITLE",
                    },
                ],
                "title": "Kōdō o kaeru dezain",
                "edition": "shohan",
                "publication_year": "2020",
                "imprint": {
                    "publisher": "Orairī Japan",
                    "place": "Tōkyō-to Shinjuku-ku",
                },
                "number_of_pages": "464",
                "abstract": "Abstract",
                "keywords": [
                    {"source": "SAFARI", "value": "Human-computer interaction"},
                    {"source": "SAFARI", "value": "User-centered system design"},
                    {
                        "source": "SAFARI",
                        "value": "Conception participative (Conception de systèmes",
                    },
                ],
                "_eitem": {
                    "_type": "e-book",
                    "urls": [
                        {
                            "description": "e-book",
                            "value": "https://learning.oreilly.com/library/view/-/9784873119144/?ar",
                        }
                    ],
                },
            },  # noqa
        )


def test_safari_audiobook(app):
    """Test audiobook import.
    Leader tag: <leader>00000nim a22000007i 4500</leader>
    """
    dirname = os.path.join(os.path.dirname(__file__), "data")
    with open(os.path.join(dirname, "safari_audiobook.xml"), "r") as fp:
        example = fp.read()
    with app.app_context():
        check_transformation(
            example,
            {
                "_eitem": {
                    "_type": "audiobook",
                    "urls": [
                        {
                            "description": "audiobook",
                            "value": "https://learning.oreilly.com/library/view/-/9781663731913/?ar",
                        }
                    ],
                },
                "abstract": "Make anxiety work for you. Work is stressful: We race to meet deadlines. We extend ourselves to return favors for colleagues. We set ambitious goals for ourselves and our teams. We measure ourselves against metrics, our competitors, and sometimes, our colleagues. Some of us even go beyond tangible metrics to internalize stress and fear of missing the mark-ruminating over presentations that didn't go according to plan, imagining worst-case scenarios, or standing frozen, paralyzed by perfectionism. But hypervigilance, worry, and catastrophizing don't have to hold you back at work. When channeled thoughtfully, anxiety can motivate us to be more resourceful, productive, and creative. It can break down barriers and create new bonds with our colleagues. Managing Your Anxiety will help you distinguish stress from anxiety, learn what anxiety looks like for you, understand it, and respond to it with self-compassion at work. With the latest psychological research and practical advice from leading experts, you'll learn how to recognize how your anxiety manifests itself; manage it in small, day-to-day moments and in more challenging times; experiment and find a mindfulness practice that works for you; and build a support infrastructure to help you manage your anxiety over the long term.",
                "agency_code": "OCoLC",
                "alternative_identifiers": [
                    {"scheme": "SAFARI", "value": "on1417409648"}
                ],
                "authors": [
                    {
                        "full_name": "Marvel, Steve",
                        "roles": ["AUTHOR"],
                        "type": "PERSON",
                    },
                    {
                        "full_name": "Schnaubelt, Teri",
                        "roles": ["AUTHOR"],
                        "type": "PERSON",
                    },
                ],
                "document_type": "BOOK",
                "edition": "1st",
                "identifiers": [
                    {
                        "material": "AUDIOBOOK",
                        "scheme": "ISBN",
                        "value": "9781663731913",
                    },
                    {"material": "AUDIOBOOK", "scheme": "ISBN", "value": "1663731918"},
                ],
                "imprint": {
                    "place": "Place of publication not identified",
                    "publisher": "Ascent Audio",
                },
                "keywords": [
                    {"source": "SAFARI", "value": "Anxiety"},
                    {"source": "SAFARI", "value": "Job stress"},
                    {"source": "SAFARI", "value": "Self-care, Health"},
                    {"source": "SAFARI", "value": "Autothérapie"},
                ],
                "languages": ["ENG"],
                "provider_recid": "on1417409648",
                "publication_year": "2024",
                "subjects": [
                    {"scheme": "LOC", "value": "BF575.A6"},
                    {"scheme": "DEWEY", "value": "152.4/6"},
                ],
                "title": "Managing your anxiety",
            },
        )


def test_safari_audiobook2(app):
    """Test audiobook import.
    Leader tag: <leader>00000njm a22000007i 4500</leader>
    """
    dirname = os.path.join(os.path.dirname(__file__), "data")
    with open(os.path.join(dirname, "safari_audiobook2.xml"), "r") as fp:
        example = fp.read()
    with app.app_context():
        check_transformation(
            example,
            {
                "_eitem": {
                    "_type": "audiobook",
                    "urls": [
                        {
                            "description": "audiobook",
                            "value": "https://learning.oreilly.com/library/view/-/9781663731913/?ar",
                        }
                    ],
                },
                "abstract": "Make anxiety work for you. Work is stressful: We race to meet deadlines. We extend ourselves to return favors for colleagues. We set ambitious goals for ourselves and our teams. We measure ourselves against metrics, our competitors, and sometimes, our colleagues. Some of us even go beyond tangible metrics to internalize stress and fear of missing the mark-ruminating over presentations that didn't go according to plan, imagining worst-case scenarios, or standing frozen, paralyzed by perfectionism. But hypervigilance, worry, and catastrophizing don't have to hold you back at work. When channeled thoughtfully, anxiety can motivate us to be more resourceful, productive, and creative. It can break down barriers and create new bonds with our colleagues. Managing Your Anxiety will help you distinguish stress from anxiety, learn what anxiety looks like for you, understand it, and respond to it with self-compassion at work. With the latest psychological research and practical advice from leading experts, you'll learn how to recognize how your anxiety manifests itself; manage it in small, day-to-day moments and in more challenging times; experiment and find a mindfulness practice that works for you; and build a support infrastructure to help you manage your anxiety over the long term.",
                "agency_code": "OCoLC",
                "alternative_identifiers": [
                    {"scheme": "SAFARI", "value": "on1417409648"}
                ],
                "authors": [
                    {
                        "full_name": "Marvel, Steve",
                        "roles": ["AUTHOR"],
                        "type": "PERSON",
                    },
                    {
                        "full_name": "Schnaubelt, Teri",
                        "roles": ["AUTHOR"],
                        "type": "PERSON",
                    },
                ],
                "document_type": "BOOK",
                "edition": "1st",
                "identifiers": [
                    {
                        "material": "AUDIOBOOK",
                        "scheme": "ISBN",
                        "value": "9781663731913",
                    },
                    {"material": "AUDIOBOOK", "scheme": "ISBN", "value": "1663731918"},
                ],
                "imprint": {
                    "place": "Place of publication not identified",
                    "publisher": "Ascent Audio",
                },
                "keywords": [
                    {"source": "SAFARI", "value": "Anxiety"},
                    {"source": "SAFARI", "value": "Job stress"},
                    {"source": "SAFARI", "value": "Self-care, Health"},
                    {"source": "SAFARI", "value": "Autothérapie"},
                ],
                "languages": ["ENG"],
                "provider_recid": "on1417409648",
                "publication_year": "2024",
                "subjects": [
                    {"scheme": "LOC", "value": "BF575.A6"},
                    {"scheme": "DEWEY", "value": "152.4/6"},
                ],
                "title": "Managing your anxiety",
            },
        )


def test_safari_record_broken_mediatype(app):
    """Test broken mediatype "bla".
    Leader tag: <marc:leader>01538nbla a2200397 a 4500</marc:leader>
    """
    dirname = os.path.join(os.path.dirname(__file__), "data")
    with open(os.path.join(dirname, "safari_record_broken_mediatype.xml"), "r") as fp:
        example = fp.read()

    with app.app_context():
        with pytest.raises(UnrecognisedImportMediaType):
            check_transformation(
                example,
                {},
            )


def test_safari_video(app):
    """Test video import."""
    dirname = os.path.join(os.path.dirname(__file__), "data")
    with open(os.path.join(dirname, "safari_video.xml"), "r") as fp:
        example = fp.read()
    with app.app_context():
        check_transformation(
            example,
            {
                "_eitem": {
                    "_type": "video",
                    "urls": [
                        {
                            "description": "video",
                            "value": "https://learning.oreilly.com/library/view/-/9781804615362/?ar",
                        }
                    ],
                },
                "abstract": "JavaScript is the base for many other languages; if you know "
                "JavaScript, you can work with a lot of other languages and "
                "dependent frameworks easily. This course is based on the newer "
                "features that were released with the ECMAScript specification 6 "
                "and above. So, we will only discuss things from ES6 and above. "
                "In the first section of this course, you will touch base on "
                "JavaScript history, and you will get in place all the required "
                "stuff that you should have in your machine for this course. In "
                "the second section of the course, you will focus on variables "
                "and scope, and you will see the newer patterns to work with "
                "variables. Following that, in the third section, we will discuss "
                "functions and arguments, which is a critical part of this course "
                "because JavaScript treats functions as a first-class citizens, "
                "so knowing what changes have been incorporated into them in "
                "newer versions is also very essential. In the fourth section, "
                "you will learn about operators and how to better use and code "
                "them. Then you will understand the new functionality of error "
                "handling; in an application where errors are not handled "
                "properly, the usability of such an application is nearly "
                "impossible. Then we have a section dedicated to async patterns "
                "and promises where you will see a few of the latest functions in "
                "comparison with similar older functions. By the end of the "
                "course, you will get to know the hacks and tricks to improve "
                "your coding skills. What You Will Learn Learn various JavaScript "
                "hacks Learn various JavaScript concepts Understand the spread "
                "operators in JavaScript Explore optional chaining operators "
                "Explain prototypal chains Understand error handling in "
                "JavaScript Audience This course can be taken by any advanced and "
                "intermediate JavaScript learners. This course expects you to "
                "have a clear understanding of the basics of JavaScript. About "
                "The Author Basics Strong: Basics Strong is a team of technocrats "
                "from IITs who focus on solving problems using technology. They "
                "work on mission-critical projects in AI, machine learning, and "
                "BlockChain as a domain and use Java, Python, JavaScript, and a "
                "lot of tools and technologies. They love to code and program. "
                "The team believes that a strong foundation in the basics of "
                "programming concepts can help you solve any technical problem "
                "and excel in your career. Therefore, they create courses that "
                "help you build your basics and come up with ways to make "
                "complicated concepts easy to learn. All their courses are "
                "carefully crafted to include hands-on examples and comprehensive "
                "working files for practical learning.",
                "agency_code": "OCoLC",
                "alternative_identifiers": [
                    {"scheme": "SAFARI", "value": "on1351466591"}
                ],
                "alternative_titles": [
                    {"type": "SUBTITLE", "value": "modern and advanced JavaScript"}
                ],
                "authors": [
                    {
                        "full_name": "ILS,CDS Else,Someone",
                        "roles": ["AUTHOR"],
                        "type": "PERSON",
                    }
                ],
                "document_type": "MULTIMEDIA",
                "edition": "1st",
                "identifiers": [
                    {
                        "material": "VIDEO",
                        "scheme": "ISBN",
                        "value": "9781804615362",
                    },
                    {
                        "material": "VIDEO",
                        "scheme": "ISBN",
                        "value": "1804615366",
                    },
                ],
                "imprint": {
                    "place": "Place of publication not identified",
                    "publisher": "Packt Publishing",
                },
                "keywords": [
                    {
                        "source": "SAFARI",
                        "value": "JavaScript (Computer program language",
                    }
                ],
                "languages": ["ENG"],
                "provider_recid": "on1351466591",
                "publication_year": "2022",
                "subjects": [
                    {"scheme": "LOC", "value": "QA76.73.J39"},
                    {"scheme": "DEWEY", "value": "005.2/762"},
                ],
                "title": "Quick JavaScript crash course",
            },
        )
