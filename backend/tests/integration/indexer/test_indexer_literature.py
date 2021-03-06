# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# inspirehep is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

import json

import pytest
from deepdiff import DeepDiff
from freezegun import freeze_time
from helpers.utils import create_record, create_s3_bucket, es_search
from invenio_search import current_search

from inspirehep.search.api import LiteratureSearch


@freeze_time("1994-12-19")
def test_index_literature_record(inspire_app, datadir):
    author_data = json.loads((datadir / "1032336.json").read_text())
    author = create_record("aut", data=author_data)

    data = json.loads((datadir / "1630825.json").read_text())
    record = create_record("lit", data=data)

    expected_count = 1
    expected_metadata = json.loads((datadir / "es_1630825.json").read_text())
    expected_metadata_ui_display = json.loads(expected_metadata.pop("_ui_display"))
    expected_metadata_latex_us_display = expected_metadata.pop("_latex_us_display")
    expected_metadata_latex_eu_display = expected_metadata.pop("_latex_eu_display")
    expected_metadata_bibtex_display = expected_metadata.pop("_bibtex_display")
    expected_facet_author_name = expected_metadata.pop("facet_author_name")
    expected_metadata.pop("authors")

    response = es_search("records-hep")

    result = response["hits"]["hits"][0]["_source"]
    result_ui_display = json.loads(result.pop("_ui_display"))
    result_latex_us_display = result.pop("_latex_us_display")
    result_latex_eu_display = result.pop("_latex_eu_display")
    result_bibtex_display = result.pop("_bibtex_display")
    result_authors = result.pop("authors")
    result_facet_author_name = result.pop("facet_author_name")
    del result["_created"]
    del result["_updated"]
    assert response["hits"]["total"]["value"] == expected_count
    assert not DeepDiff(result, expected_metadata, ignore_order=True)
    assert result_ui_display == expected_metadata_ui_display
    assert result_latex_us_display == expected_metadata_latex_us_display
    assert result_latex_eu_display == expected_metadata_latex_eu_display
    assert result_bibtex_display == expected_metadata_bibtex_display
    assert len(record.get("authors")) == len(result_facet_author_name)
    assert sorted(result_facet_author_name) == sorted(expected_facet_author_name)


def test_regression_index_literature_record_with_related_records(inspire_app, datadir):
    data = json.loads((datadir / "1503270.json").read_text())
    record = create_record("lit", data=data)

    response = es_search("records-hep")

    result = response["hits"]["hits"][0]["_source"]

    assert data["related_records"] == result["related_records"]


def test_indexer_deletes_record_from_es(inspire_app, datadir):
    data = json.loads((datadir / "1630825.json").read_text())
    record = create_record("lit", data=data)
    record.delete()
    record.index(delay=False)
    current_search.flush_and_refresh("records-hep")

    expected_total = 0

    response = es_search("records-hep")
    hits_total = response["hits"]["total"]["value"]

    assert hits_total == expected_total


@pytest.mark.vcr()
def test_indexer_creates_proper_fulltext_links_in_ui_display_files_enabled(
    inspire_app, s3
):
    create_s3_bucket("1")
    create_s3_bucket("f")
    expected_fulltext_links = ["arXiv", "KEK scanned document", "fulltext"]

    data = {
        "external_system_identifiers": [
            {"schema": "OSTI", "value": "7224300"},
            {"schema": "ADS", "value": "1994PhRvD..50.4491S"},
            {"schema": "KEKSCAN", "value": "94-07-219"},
            {"schema": "SPIRES", "value": "SPIRES-2926342"},
        ],
        "arxiv_eprints": [{"categories": ["hep-ph"], "value": "hep-ph/9404247"}],
        "documents": [
            {
                "source": "arxiv",
                "fulltext": True,
                "hidden": True,
                "key": "arXiv:nucl-th_9310030.pdf",
                "url": "https://arxiv.org/pdf/1910.11662.pdf",
            },
            {
                "source": "arxiv",
                "key": "arXiv:nucl-th_9310031.pdf",
                "url": "http://inspirehep.net/record/863300/files/fermilab-pub-10-255-e.pdf",
            },
        ],
    }
    record = create_record("lit", data=data)
    response = es_search("records-hep")

    result = response["hits"]["hits"][0]["_source"]
    result_ui_display = json.loads(result.pop("_ui_display"))
    for link in result_ui_display["fulltext_links"]:
        assert link["value"]
        assert link["description"] in expected_fulltext_links


def test_indexer_creates_proper_fulltext_links_in_ui_display_files_disabled(
    inspire_app, disable_files
):
    expected_fulltext_links = [
        {"description": "arXiv", "value": "https://arxiv.org/pdf/hep-ph/9404247"},
        {
            "description": "KEK scanned document",
            "value": "https://lib-extopc.kek.jp/preprints/PDF/1994/9407/9407219.pdf",
        },
    ]

    data = {
        "external_system_identifiers": [
            {"schema": "OSTI", "value": "7224300"},
            {"schema": "ADS", "value": "1994PhRvD..50.4491S"},
            {"schema": "KEKSCAN", "value": "94-07-219"},
            {"schema": "SPIRES", "value": "SPIRES-2926342"},
        ],
        "arxiv_eprints": [{"categories": ["hep-ph"], "value": "hep-ph/9404247"}],
        "documents": [
            {
                "source": "arxiv",
                "fulltext": True,
                "key": "arXiv:nucl-th_9310030.pdf",
                "url": "http://localhost:8000/some_url.pdf",
            },
            {
                "source": "arxiv",
                "key": "arXiv:nucl-th_9310031.pdf",
                "url": "http://localhost:8000/some_url2.pdf",
            },
        ],
    }
    create_record("lit", data=data)
    response = es_search("records-hep")

    result = response["hits"]["hits"][0]["_source"]
    result_ui_display = json.loads(result.pop("_ui_display"))

    assert result_ui_display["fulltext_links"] == expected_fulltext_links


def test_indexer_not_fulltext_links_in_ui_display_when_no_fulltext_links(inspire_app):

    data = {
        "external_system_identifiers": [
            {"schema": "OSTI", "value": "7224300"},
            {"schema": "ADS", "value": "1994PhRvD..50.4491S"},
            {"schema": "SPIRES", "value": "SPIRES-2926342"},
        ],
        "documents": [
            {
                "source": "arxiv",
                "key": "arXiv:nucl-th_9310031.pdf",
                "url": "http://localhost:8000/some_url2.pdf",
            }
        ],
    }
    create_record("lit", data=data)
    response = es_search("records-hep")

    result = response["hits"]["hits"][0]["_source"]
    result_ui_display = json.loads(result.pop("_ui_display"))

    assert "fulltext_links" not in result_ui_display


def test_indexer_removes_supervisors_from_authors_for_ui_display_field(inspire_app):
    authors = [
        {"full_name": "Frank Castle"},
        {"full_name": "Jimmy", "inspire_roles": ["supervisor"]},
    ]
    data = {"authors": authors}
    create_record("lit", data=data)
    response = es_search("records-hep")

    expected_author_full_name = "Frank Castle"
    result = response["hits"]["hits"][0]["_source"]
    result_ui_display = json.loads(result.pop("_ui_display"))
    result_authors = result["authors"]
    assert len(result_ui_display["authors"]) == 1
    assert result_ui_display["authors"][0]["full_name"] == expected_author_full_name
    assert len(result_authors) == 1
    assert result_authors[0]["full_name"] == expected_author_full_name


def test_indexer_separates_supervisors_from_authors(inspire_app):
    authors = [
        {"full_name": "Frank Castle"},
        {"full_name": "Jimmy", "inspire_roles": ["supervisor"]},
    ]
    data = {"authors": authors}
    create_record("lit", data=data)
    response = es_search("records-hep")

    expected_author_full_name = "Frank Castle"
    expected_supervisor = "Jimmy"
    result = response["hits"]["hits"][0]["_source"]
    result_authors = result["authors"]
    assert len(result_authors) == 1
    assert result_authors[0]["full_name"] == expected_author_full_name
    result_supervisors = result["supervisors"]
    assert len(result_supervisors) == 1
    assert result_supervisors[0]["full_name"] == expected_supervisor


def test_indexer_populates_referenced_authors_bais(inspire_app):
    data_authors = {
        "authors": [
            {
                "full_name": "Jean-Luc Picard",
                "ids": [{"schema": "INSPIRE BAI", "value": "Jean.L.Picard.1"}],
            },
            {
                "full_name": "John Doe",
                "ids": [{"schema": "INSPIRE BAI", "value": "J.Doe.1"}],
            },
        ]
    }
    cited_record_1 = create_record("lit", data=data_authors)
    data_authors = {
        "authors": [
            {
                "full_name": "Jean-Luc Picard",
                "ids": [{"schema": "INSPIRE BAI", "value": "Jean.L.Picard.1"}],
            },
            {
                "full_name": "Steven Johnson",
                "ids": [{"schema": "INSPIRE BAI", "value": "S.Johnson.1"}],
            },
        ]
    }
    cited_record_2 = create_record("lit", data=data_authors)
    citing_record = create_record(
        "lit",
        literature_citations=[
            cited_record_1["control_number"],
            cited_record_2["control_number"],
        ],
    )
    expected_rec3_referenced_authors_bais = [
        "J.Doe.1",
        "Jean.L.Picard.1",
        "S.Johnson.1",
    ]
    rec1_es = LiteratureSearch.get_record_data_from_es(cited_record_1)
    rec2_es = LiteratureSearch.get_record_data_from_es(cited_record_2)
    rec3_es = LiteratureSearch.get_record_data_from_es(citing_record)
    assert "referenced_authors_bais" not in rec1_es
    assert "referenced_authors_bais" not in rec2_es
    assert (
        sorted(rec3_es["referenced_authors_bais"])
        == expected_rec3_referenced_authors_bais
    )
