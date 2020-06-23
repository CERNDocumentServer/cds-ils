import { Footer } from './overriden/components/Footer/Footer';
import {
  RightMenuItem,
  RightMenuItemMobile,
} from './overriden/components/Menu/RightMenuItem';
import { Home } from './overriden/frontsite/Home/Home';
import { Slogan } from './overriden/frontsite/Home/Slogan';

export const overriddenCmps = {
  'Home.Headline.slogan': Slogan,
  'Home.content': Home,
  'Footer.layout': Footer,
  'ILSMenu.RightMenuItems': RightMenuItem,
  'ILSMenu.RightMenuItemsMobile': RightMenuItemMobile,
};
