import { parametrize } from "react-overridable";
import { LiteratureSearch } from "@inveniosoftware/react-invenio-app-ils";
import { StandardListView } from "../DocumentSearch/StandardListView";
import { StandardCardView } from "../DocumentSearch/StandardCardView";
import { SearchMessageContent } from "./SearchMessageContent";
import { SearchResultExtra } from "./SearchResultExtra";
import { SearchResultHeader } from "./SearchResultHeader";

export const overriddenSearchAppCmps = parametrize(LiteratureSearch, {
  overriddenSearchAppCmps: {
    "DocumentListEntry.BeforeAuthors": StandardListView,
    "DocumentCard.AfterAuthors": StandardCardView,
    "SearchMessage.content": SearchMessageContent,
    "SearchResults.NoResults.extra": SearchResultExtra,
    "LiteratureSearch.results.header": SearchResultHeader,
  },
});
