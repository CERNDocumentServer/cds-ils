import {
  PatronMetadata,
  PatronMetadataActionMenuItem,
} from "./overridden/backoffice/PatronMetadata/PatronMetadata";
import { Footer } from "./overridden/components/Footer/Footer";
import {
  Logo,
  LogoMobile,
  RightMenuItem,
  RightMenuItemMobile,
} from "./overridden/components/Menu";
import { DocumentRequestFormFields } from "./overridden/frontsite/DocumentRequest/DocumentRequestForm";
import { DocumentRequestFormHeader } from "./overridden/frontsite/DocumentRequest/DocumentRequestFormHeader";
import { NotAvailable } from "./overridden/frontsite/Document/DocumentDetails/DocumentCirculation/NotAvailable";
import { StandardNumber } from "./overridden/frontsite/Document/DocumentDetails/DocumentPanel/StandardNumber";
import {
  HomeContent,
  HomeHeadline,
  HomeButtons,
} from "./overridden/frontsite/Home/HomeContent";
import { LegacyRecordRoute } from "./overridden/frontsite/Routes/LegacyRoute";
import { Slogan } from "./overridden/frontsite/Home/Slogan";
import {
  SideBarMenuItem,
  SideBarCatalogueItem,
} from "./overridden/backoffice/Sidebar/SideBarMenuItem";
import { ImporterRoute } from "./overridden/routes/ImporterRoute";
import { overriddenSearchAppCmps } from "./overridden/frontsite/LiteratureSearch/LiteratureSearch";
import { StandardCardView } from "./overridden/frontsite/DocumentSearch/StandardCardView";
import { LiteratureKeyword } from "./overridden/frontsite/Document/DocumentDetails/DocumentCirculation/LiteratureKeyword";
import { Identifiers } from "./overridden/frontsite/Document/DocumentDetails/DocumentMetadataTabs/Identifiers";
import { DocumentConference } from "./overridden/frontsite/Document/DocumentDetails/DocumentMetadataTabs/DocumentConference";
import { DocumentItemsHeader } from "./overridden/frontsite/Document/DocumentDetails/DocumentItemsHeader";
import { DocumentItemBodyTable } from "./overridden/frontsite/Document/DocumentDetails/DocumentItemBody";
import { DocumentCirculationExtras } from "./overridden/frontsite/Document/DocumentDetails/DocumentCirculationExtras";
import { OpeningHoursDetails } from "./overridden/frontsite/OpeningHours/OpeningHoursDetails";
import { PaymentInformationGrid } from "./overridden/backoffice/PaymentInformation/PaymentInformation";
import { OrderDetailsLine } from "./overridden/backoffice/Acquisition/OrderDetails";
import { ItemCirculationShelf } from "./overridden/backoffice/Items/ItemCirculationShelf";
import { DocumentItemsLayout } from "./overridden/backoffice/Document/DocumentDetails/DocumentItems";

export const overriddenCmps = {
  "Backoffice.PatronDetails.Metadata": PatronMetadata,
  "Backoffice.PatronDetails.Metadata.ActionMenuItem": PatronMetadataActionMenuItem,
  "Home.Headline": HomeHeadline,
  "Home.Headline.slogan": Slogan,
  "Home.Headline.extra": HomeButtons,
  "Home.content": HomeContent,
  "ILSFooter": Footer,
  "ILSMenu.Logo": Logo,
  "ILSMenu.LogoMobile": LogoMobile,
  "ILSMenu.RightMenuItems": RightMenuItem,
  "ILSMenu.RightMenuItemsMobile": RightMenuItemMobile,
  "LoanAvailability.NotAvailable": NotAvailable,
  "FrontSite.CustomRoute": LegacyRecordRoute,
  "DocumentRequestForm": DocumentRequestFormFields,
  "DocumentRequestForm.header": DocumentRequestFormHeader,
  "DocumentPanel.AfterAuthors": StandardNumber,
  "DocumentPanelMobile.AfterAuthors": StandardNumber,
  "DocumentCard.AfterAuthors": StandardCardView,
  "LiteratureSearch": overriddenSearchAppCmps,
  "BackOfficeRoutesSwitch.CustomRoute": ImporterRoute,
  "Backoffice.Sidebar.CustomMenuItem": SideBarMenuItem,
  "Backoffice.Sidebar.Menu.Catalogue": SideBarCatalogueItem,
  "LiteratureKeywords.layout": LiteratureKeyword,
  "DocumentMetadataTabs.Identifiers": Identifiers,
  "DocumentConference.layout": DocumentConference,
  "DocumentDetails.DocumentItems.header": DocumentItemsHeader,
  "DocumentDetails.DocumentItemTableBody": DocumentItemBodyTable,
  "OpeningHours.details": OpeningHoursDetails,
  "Backoffice.PaymentInformation": PaymentInformationGrid,
  "Acquisition.OrderLine": OrderDetailsLine,
  "DocumentCirculation.Extras": DocumentCirculationExtras,
  "ItemCirculation.backoffice.shelf": ItemCirculationShelf,
  "DocumentDetails.DocumentItems": DocumentItemsLayout,
};
