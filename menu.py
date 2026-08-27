# menu.py — Чёрное окно 1100x500 по центру, дискеты от середины, стрелки
import os, math, logging, threading
import pygame, config, steam_api, launcher
log=logging.getLogger(__name__)
def lerp(a,b,t): return a+(b-a)*t

class GameTile:
    def __init__(self,a,n): self.app_id=a; self.name=n; self.image_path=None
    def load_async(self):
        def w():
            if not self.name or self.name.startswith("Game #"): self.name=steam_api.fetch_name(self.app_id)
            p=steam_api.fetch_cover(self.app_id)
            if p: self.image_path=p
        threading.Thread(target=w,daemon=True).start()

def show_menu(games_raw, flash_path=None):
    if not games_raw:
        return
    tiles=[GameTile(a, n or steam_api.get_cached_name(a) or f"Game #{a}") for a,n in games_raw]
    for t in tiles: t.load_async()
    pygame.init()
    W,H=1100,500
    os.environ['SDL_VIDEO_CENTERED']='1'
    try:
        screen=pygame.display.set_mode((W,H), pygame.NOFRAME)
        pygame.display.set_caption("SteamFlash")
    except pygame.error as e:
        log.error(f"display: {e}")
        return
    clock=pygame.time.Clock()
    BG=(10,10,10)
    FLOPPY_BODY=(38,38,42); SHUTTER=(62,62,68); LABEL=(242,242,245); BORDER=(70,70,75); SEL=(255,255,255)
    font_name=pygame.font.SysFont("Segoe UI",13,bold=True)
    font_small=pygame.font.SysFont("Consolas",9)
    selected=0; scroll=0; target=0; anim=0
    drawer=0; state="opening"; pending=None
    gap=18; fw,fh=240,175
    cols=min(4, len(tiles))
    if W<900: cols=min(cols,2)
    cols=max(1,cols)
    surf_cache={}
    def get_cover(tile):
        k=tile.app_id
        if k in surf_cache: return surf_cache[k]
        p=tile.image_path or steam_api.get_cached_cover_path(tile.app_id)
        if p and os.path.exists(p):
            try:
                img=pygame.image.load(p).convert()
                img=pygame.transform.smoothscale(img,(fw-14, 88))
                surf_cache[k]=img; return img
            except: pass
        s=pygame.Surface((fw-14,88)); s.fill((50,50,55)); surf_cache[k]=s; return s
    running=True; joy_cd=0
    try:
        pygame.joystick.init()
        joys=[pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        for j in joys: j.init()
    except: joys=[]

    while running:
        try:
            dt=clock.tick(config.FPS)/1000.0
        except: break
        anim=lerp(anim,1,dt*11)
        # безопасная проверка флешки
        try:
            if flash_path and not os.path.exists(flash_path) and state=="idle":
                break
        except: pass
        if state=="opening":
            drawer=min(1, drawer+dt*4)
            if drawer>=1: state="idle"
        elif state=="closing":
            drawer=max(0, drawer-dt*5)
            if drawer<=0:
                if pending:
                    try: ok,_=launcher.launch_game(pending)
                    except: ok=False
                    if not ok:
                        state="opening"; drawer=0; pending=None
                        continue
                    try: pygame.time.wait(500)
                    except: pass
                    try:
                        import psutil, time as tm
                        tm.sleep(1)
                        found=any('steam' in (p.info.get('name') or '').lower() for p in psutil.process_iter(['name']))
                        if not found:
                            for _ in range(5):
                                tm.sleep(1)
                                if any('steam' in (p.info.get('name') or '').lower() for p in psutil.process_iter(['name'])):
                                    found=True; break
                        if not found:
                            state="opening"; drawer=0; pending=None; continue
                    except: pass
                    break
                break
        ease=1-pow(1-drawer,3)
        if state=="idle":
            rows=math.ceil(len(tiles)/cols)
            row=selected//cols
            grid_h=rows*(fh+gap)
            vis=H-40
            # от середины: цель — центрировать выбранный ряд
            target = row*(fh+gap) - grid_h/2 + fh/2
            target=max(-grid_h/2, min(target, grid_h/2))
            scroll=lerp(scroll, target, dt*9)

        for e in pygame.event.get():
            if e.type==pygame.QUIT: running=False
            if state!="idle": continue
            if e.type==pygame.MOUSEBUTTONDOWN:
                if e.button==4: selected=max(0,selected-cols); anim=0
                elif e.button==5: selected=min(len(tiles)-1,selected+cols); anim=0
                elif e.button==1:
                    mx,my=e.pos
                    rows=math.ceil(len(tiles)/cols); grid_h=rows*(fh+gap); grid_w=cols*fw+(cols-1)*gap
                    sx=W//2-grid_w//2; sy=H//2 - grid_h//2 - int(scroll) + int((1-ease)*300)
                    for idx in range(len(tiles)):
                        r,c=divmod(idx,cols); x=sx+c*(fw+gap); y=sy+r*(fh+gap)
                        if pygame.Rect(x,y,fw,fh).collidepoint(mx,my):
                            selected=idx; pending=tiles[idx].app_id; state="closing"; break
            if e.type==pygame.MOUSEWHEEL:
                selected=max(0,min(len(tiles)-1, selected + (-1 if e.y>0 else 1)*cols)); anim=0
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_ESCAPE: running=False
                elif e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                    pending=tiles[selected].app_id; state="closing"
                elif e.key in (pygame.K_LEFT, pygame.K_a): selected=max(0,selected-1); anim=0
                elif e.key in (pygame.K_RIGHT, pygame.K_d): selected=min(len(tiles)-1,selected+1); anim=0
                elif e.key in (pygame.K_UP, pygame.K_w): selected=max(0,selected-cols); anim=0
                elif e.key in (pygame.K_DOWN, pygame.K_s): selected=min(len(tiles)-1,selected+cols); anim=0

        if joys and joy_cd<=0 and state=="idle":
            for j in joys:
                try:
                    ax0=j.get_axis(0); ax1=j.get_axis(1)
                    if ax0<-0.6: selected=max(0,selected-1); joy_cd=0.15; anim=0
                    elif ax0>0.6: selected=min(len(tiles)-1,selected+1); joy_cd=0.15; anim=0
                    elif ax1<-0.6: selected=max(0,selected-cols); joy_cd=0.15; anim=0
                    elif ax1>0.6: selected=min(len(tiles)-1,selected+cols); joy_cd=0.15; anim=0
                    else: continue
                    break
                except: pass
        joy_cd-=dt

        # чёрный фон
        screen.fill(BG)
        rows=math.ceil(len(tiles)/cols) if tiles else 1
        grid_h=rows*(fh+gap); grid_w=cols*fw+(cols-1)*gap
        sx=W//2-grid_w//2
        base_y=H//2 - grid_h//2
        y_anim=int((1-ease)*250)
        sy=base_y - int(scroll) + y_anim
        if state=="closing":
            sy=base_y - int(scroll) + int((1-drawer)*400)
        # clip чтобы не лезло за окно
        clip=pygame.Rect(0,0,W,H)
        screen.set_clip(clip)
        for idx,tile in enumerate(tiles):
            r,c=divmod(idx,cols); x=sx+c*(fw+gap); y=sy+r*(fh+gap)
            if y < -fh or y > H: continue
            is_sel=idx==selected
            scale=lerp(1,1.06,anim) if is_sel else 1
            if not tile.image_path:
                p=steam_api.get_cached_cover_path(tile.app_id)
                if p: tile.image_path=p
            w2,h2=int(fw*scale),int(fh*scale); dx,dy=(w2-fw)//2,(h2-fh)//2
            rect=pygame.Rect(x-dx,y-dy,w2,h2)
            pygame.draw.rect(screen,(0,0,0), rect.move(2,3), border_radius=10)
            pygame.draw.rect(screen,FLOPPY_BODY, rect, border_radius=10)
            sh=pygame.Rect(rect.x, rect.y, w2, 24)
            pygame.draw.rect(screen,SHUTTER, sh, border_top_left_radius=10, border_top_right_radius=10)
            pygame.draw.rect(screen,(18,18,20), pygame.Rect(rect.centerx-30, rect.y+6, 60, 11), border_radius=3)
            lab=pygame.Rect(rect.x+7, rect.y+30, w2-14, 30)
            pygame.draw.rect(screen,LABEL, lab, border_radius=4)
            name=tile.name[:24]
            ns=font_name.render(name, True, (18,18,20))
            if ns.get_width()>lab.w-8:
                ns=pygame.font.SysFont("Segoe UI",11,bold=True).render(name, True, (18,18,20))
            screen.blit(ns,(rect.centerx-ns.get_width()//2, lab.centery-ns.get_height()//2))
            cover=get_cover(tile)
            cw2=int((fw-14)*scale); ch2=int(88*scale)
            cs=pygame.transform.smoothscale(cover,(cw2,ch2)) if scale!=1 else cover
            cx2=rect.centerx-cw2//2; cy2=lab.bottom+7
            screen.blit(cs,(cx2,cy2))
            pygame.draw.rect(screen,BORDER, pygame.Rect(cx2,cy2,cw2,ch2), width=1, border_radius=4)
            aid=font_small.render(tile.app_id, True, (110,110,115))
            screen.blit(aid,(rect.centerx-aid.get_width()//2, rect.bottom-11))
            if is_sel:
                pygame.draw.rect(screen,SEL, rect.inflate(6,6), width=2, border_radius=12)
            else:
                pygame.draw.rect(screen,BORDER, rect, width=1, border_radius=10)
            if not is_sel:
                dim=pygame.Surface((w2,h2),pygame.SRCALPHA); dim.fill((0,0,0,90)); screen.blit(dim,rect)
        screen.set_clip(None)
        try:
            pygame.display.flip()
        except pygame.error:
            break
    try: pygame.quit()
    except: pass
