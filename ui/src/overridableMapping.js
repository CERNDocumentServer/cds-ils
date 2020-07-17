import { Footer } from './overridden/components/Footer/Footer';
import {
  Logo,
  LogoMobile,
  RightMenuItem,
  RightMenuItemMobile,
} from './overridden/components/Menu';
import {
  HomeContent,
  HomeHeadline,
} from './overridden/frontsite/Home/HomeContent';
import { Slogan } from './overridden/frontsite/Home/Slogan';
import { DeliveryIcon } from './overridden/backoffice/DeliveryIcon/DeliveryIcon';

export const overriddenCmps = {
  'Home.Headline': HomeHeadline,
  'Home.Headline.slogan': Slogan,
  'Home.content': HomeContent,
  ILSFooter: Footer,
  'ILSMenu.Logo': Logo,
  'ILSMenu.LogoMobile': LogoMobile,
  'ILSMenu.RightMenuItems': RightMenuItem,
  'ILSMenu.RightMenuItemsMobile': RightMenuItemMobile,
  'LoanListEntry.DeliveryIcon': DeliveryIcon,
  'LoanMetadata.DeliveryIcon': DeliveryIcon,
  'RequestForPatronMessage.DeliveryIcon': DeliveryIcon,
};
