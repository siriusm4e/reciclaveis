import { type ReactNode } from 'react';

import { BottomNav } from './BottomNav';
import { MobileFrame } from './MobileFrame';

interface Props {
  children: ReactNode;
  showNav?: boolean;
}

/** Layout mobile com BottomNav + safe-area, ocupando o frame de 390px no desktop. */
export function AppLayout({ children, showNav = true }: Props) {
  return (
    <MobileFrame>
      <main className="flex-1 overflow-y-auto pb-24">{children}</main>
      {showNav && <BottomNav />}
    </MobileFrame>
  );
}
