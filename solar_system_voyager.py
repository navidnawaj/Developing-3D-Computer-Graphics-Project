from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time

# ============================================================
# SECTION 1: WINDOW & CONSTANTS
# ============================================================
W_WIDTH, W_HEIGHT = 1200, 800

# ============================================================
# SECTION 2: PLANET DATABASE
# ============================================================
SUN_RADIUS = 40

PLANETS = [
    {'name':'Mercury','radius':5,'color':(0.7,0.7,0.7),'orbit_radius':90,
     'orbit_speed':4.15,'orbit_angle':0,'tilt':0.03,'self_rot':0,'self_rot_spd':0.017,
     'info':{'dist':'57.9M km','period':'88 days','moons_count':0},
     'moons':[],'has_rings':False},
    {'name':'Venus','radius':9,'color':(0.9,0.8,0.5),'orbit_radius':130,
     'orbit_speed':1.62,'orbit_angle':45,'tilt':177.4,'self_rot':0,'self_rot_spd':0.004,
     'info':{'dist':'108.2M km','period':'225 days','moons_count':0},
     'moons':[],'has_rings':False},
    {'name':'Earth','radius':10,'color':(0.2,0.5,0.9),'orbit_radius':180,
     'orbit_speed':1.0,'orbit_angle':90,'tilt':23.4,'self_rot':0,'self_rot_spd':1.0,
     'info':{'dist':'149.6M km','period':'365 days','moons_count':1},
     'moons':[{'name':'Moon','radius':3,'color':(0.8,0.8,0.8),'orbit_radius':20,
               'orbit_speed':13.0,'orbit_angle':0}],
     'has_rings':False},
    {'name':'Mars','radius':7,'color':(0.8,0.3,0.1),'orbit_radius':240,
     'orbit_speed':0.53,'orbit_angle':200,'tilt':25.2,'self_rot':0,'self_rot_spd':0.97,
     'info':{'dist':'227.9M km','period':'687 days','moons_count':2},
     'moons':[],'has_rings':False},
    {'name':'Jupiter','radius':25,'color':(0.8,0.6,0.4),'orbit_radius':350,
     'orbit_speed':0.084,'orbit_angle':150,'tilt':3.1,'self_rot':0,'self_rot_spd':2.4,
     'info':{'dist':'778.5M km','period':'4333 days','moons_count':95},
     'moons':[
         {'name':'Io','radius':3,'color':(0.9,0.8,0.3),'orbit_radius':35,'orbit_speed':17.0,'orbit_angle':0},
         {'name':'Europa','radius':2.5,'color':(0.8,0.75,0.7),'orbit_radius':42,'orbit_speed':8.5,'orbit_angle':90},
         {'name':'Ganymede','radius':4,'color':(0.6,0.55,0.5),'orbit_radius':52,'orbit_speed':4.2,'orbit_angle':180},
         {'name':'Callisto','radius':3.5,'color':(0.4,0.35,0.3),'orbit_radius':62,'orbit_speed':2.0,'orbit_angle':270},
     ],'has_rings':False},
    {'name':'Saturn','radius':22,'color':(0.9,0.8,0.5),'orbit_radius':470,
     'orbit_speed':0.034,'orbit_angle':280,'tilt':26.7,'self_rot':0,'self_rot_spd':2.2,
     'info':{'dist':'1.43B km','period':'10759 days','moons_count':146},
     'moons':[],'has_rings':True},
    {'name':'Uranus','radius':16,'color':(0.5,0.8,0.9),'orbit_radius':580,
     'orbit_speed':0.012,'orbit_angle':30,'tilt':97.8,'self_rot':0,'self_rot_spd':1.4,
     'info':{'dist':'2.87B km','period':'30687 days','moons_count':28},
     'moons':[],'has_rings':False},
    {'name':'Neptune','radius':15,'color':(0.2,0.3,0.8),'orbit_radius':700,
     'orbit_speed':0.006,'orbit_angle':120,'tilt':28.3,'self_rot':0,'self_rot_spd':1.5,
     'info':{'dist':'4.5B km','period':'60190 days','moons_count':16},
     'moons':[],'has_rings':False},
]

# ============================================================
# SECTION 3: GLOBAL STATE
# ============================================================
cam_mode = 'overview'
ov_angle_h = 45.0
ov_angle_v = 35.0
ov_distance = 900.0

focused_planet = -1
track_angle_h = 0.0
track_angle_v = 30.0
track_distance = 100.0

free_pos = [0.0, -500.0, 300.0]
free_yaw = 90.0
free_pitch = -20.0

time_scale = 1.0
paused = False
last_time = 0.0

show_orbits = True
scale_mult = 1.0
show_labels = True

last_mx = 0
last_my = 0
dragging_planet = -1
mouse_left_down = False

stars = []
asteroids = []
quadric = None

comet_angle = 0.0
voyager_angle = 0.0
ufo_angle = 0.0

# ============================================================
# SECTION 4: INIT
# ============================================================
def init_universe():
    global stars, asteroids, quadric, last_time
    quadric = gluNewQuadric()
    last_time = time.time()
    random.seed(42)
    for p in PLANETS:
        p['orbit_angle'] = random.uniform(0, 360)
        for m in p['moons']:
            m['orbit_angle'] = random.uniform(0, 360)

    for _ in range(2000):
        th = random.uniform(0, 2*math.pi)
        ph = random.uniform(-math.pi/2, math.pi/2)
        r = 2500
        stars.append((r*math.cos(ph)*math.cos(th), r*math.cos(ph)*math.sin(th),
                       r*math.sin(ph), random.uniform(0.5,1.0)))

    for _ in range(1200):
        a = random.uniform(0, 2*math.pi)
        d = random.uniform(275, 340)
        asteroids.append((d*math.cos(a), d*math.sin(a),
                          random.uniform(-12,12), random.uniform(1.0,2.5)))

# ============================================================
# SECTION 5: UTILITIES
# ============================================================
def get_planet_pos(idx):
    p = PLANETS[idx]
    a = math.radians(p['orbit_angle'])
    return (p['orbit_radius']*math.cos(a), p['orbit_radius']*math.sin(a), 0)

def dist3d(a, b):
    return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))

def get_cam_pos():
    if cam_mode == 'overview':
        rh, rv = math.radians(ov_angle_h), math.radians(ov_angle_v)
        return (ov_distance*math.cos(rv)*math.cos(rh),
                ov_distance*math.cos(rv)*math.sin(rh),
                ov_distance*math.sin(rv))
    elif cam_mode == 'track' and focused_planet >= 0:
        px, py, pz = get_planet_pos(focused_planet)
        rh, rv = math.radians(track_angle_h), math.radians(track_angle_v)
        return (px + track_distance*math.cos(rv)*math.cos(rh),
                py + track_distance*math.cos(rv)*math.sin(rh),
                pz + track_distance*math.sin(rv))
    else:
        return tuple(free_pos)

# ============================================================
# SECTION 6: DRAWING
# ============================================================
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, W_WIDTH, 0, W_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_small_text(x, y, text):
    draw_text(x, y, text, GLUT_BITMAP_HELVETICA_12)

def draw_starfield():
    glPointSize(2)
    glBegin(GL_POINTS)
    for s in stars:
        glColor3f(s[3], s[3], s[3]*0.9)
        glVertex3f(s[0], s[1], s[2])
    glEnd()

def draw_sun():
    # Outer glow
    glColor3f(1.0, 0.4, 0.0)
    gluSphere(quadric, SUN_RADIUS*1.15, 20, 20)
    # Main body
    glColor3f(1.0, 0.9, 0.0)
    gluSphere(quadric, SUN_RADIUS, 20, 20)

def draw_orbit_path(radius):
    glColor3f(0.25, 0.25, 0.4)
    glBegin(GL_LINE_LOOP)
    for i in range(200):
        a = 2.0*math.pi*i/200
        glVertex3f(radius*math.cos(a), radius*math.sin(a), 0)
    glEnd()

def draw_saturn_rings(pr):
    r1 = pr*1.4*scale_mult
    r2 = pr*2.3*scale_mult
    segments = 60
    for ring in range(3):
        inner = r1 + ring*(r2-r1)/3
        outer = r1 + (ring+1)*(r2-r1)/3
        c = 0.85 - ring*0.1
        glColor3f(c, c*0.85, c*0.6)
        glBegin(GL_QUAD_STRIP)
        for i in range(segments+1):
            a = 2.0*math.pi*i/segments
            glVertex3f(inner*math.cos(a), inner*math.sin(a), 0)
            glVertex3f(outer*math.cos(a), outer*math.sin(a), 0)
        glEnd()

def draw_planet(idx):
    p = PLANETS[idx]
    glPushMatrix()
    glRotatef(p['orbit_angle'], 0, 0, 1)
    glTranslatef(p['orbit_radius'], 0, 0)
    glPushMatrix()
    glRotatef(p['tilt'], 1, 0, 0)
    glRotatef(p['self_rot'], 0, 0, 1)
    glColor3f(*p['color'])
    r = p['radius']*scale_mult
    gluSphere(quadric, r, 16, 16)
    if p['has_rings']:
        draw_saturn_rings(p['radius'])
    glPopMatrix()
    # Draw moons relative to planet
    for m in p['moons']:
        glPushMatrix()
        glRotatef(m['orbit_angle'], 0, 0, 1)
        glTranslatef(m['orbit_radius']*scale_mult, 0, 0)
        glColor3f(*m['color'])
        gluSphere(quadric, m['radius']*scale_mult, 10, 10)
        glPopMatrix()
        # Moon orbit path
        if show_orbits and (focused_planet == idx):
            glColor3f(0.3, 0.3, 0.3)
            glBegin(GL_LINE_LOOP)
            for i in range(80):
                a = 2.0*math.pi*i/80
                mr = m['orbit_radius']*scale_mult
                glVertex3f(mr*math.cos(a), mr*math.sin(a), 0)
            glEnd()
    glPopMatrix()

def draw_asteroid_belt():
    glColor3f(0.6, 0.6, 0.55)
    for ast in asteroids:
        glPushMatrix()
        glTranslatef(ast[0], ast[1], ast[2])
        glutSolidCube(ast[3])
        glPopMatrix()

def draw_comet():
    a = 600
    b = 150
    rad = math.radians(comet_angle)
    cx = a * math.cos(rad) - 200
    cy = b * math.sin(rad)
    
    glPushMatrix()
    glTranslatef(cx, cy, 30)
    
    # Head
    glColor3f(0.5, 0.8, 1.0)
    gluSphere(quadric, 6 * scale_mult, 10, 10)
    
    # Tail (points opposite to velocity vector)
    vx = -a * math.sin(rad)
    vy = b * math.cos(rad)
    mag = math.sqrt(vx*vx + vy*vy)
    if mag == 0: mag = 1
    vx, vy = vx/mag, vy/mag
    
    for i in range(1, 20):
        glPushMatrix()
        dist = i * 4.0 * scale_mult
        glTranslatef(-vx * dist, -vy * dist, 0)
        c = max(0.0, 1.0 - i/20.0)
        glColor3f(c*0.4, c*0.7, c*1.0)
        glScalef(1 - i/25.0, 1 - i/25.0, 1 - i/25.0)
        glutSolidCube(3 * scale_mult)
        glPopMatrix()
        
    glPopMatrix()

def draw_voyager(px, py, pz):
    glPushMatrix()
    glTranslatef(px, py, pz)
    
    # Orbit Earth
    glRotatef(voyager_angle, 0, 0, 1)
    glTranslatef(35 * scale_mult, 0, 0)
    glRotatef(voyager_angle * 2, 1, 1, 0)
    
    # Body
    glColor3f(0.7, 0.7, 0.7)
    glPushMatrix()
    glTranslatef(0, 0, -4)
    gluCylinder(quadric, 2*scale_mult, 2*scale_mult, 8*scale_mult, 10, 1)
    glPopMatrix()
    
    # Dish
    glColor3f(0.9, 0.9, 0.9)
    glPushMatrix()
    glTranslatef(0, 0, 4*scale_mult)
    glScalef(1, 1, 0.2)
    gluSphere(quadric, 4*scale_mult, 10, 10)
    glPopMatrix()
    
    # Antenna
    glColor3f(0.4, 0.4, 0.4)
    glPushMatrix()
    glTranslatef(0, 0, 4*scale_mult)
    gluCylinder(quadric, 0.2*scale_mult, 0.2*scale_mult, 6*scale_mult, 5, 1)
    glPopMatrix()
    
    # Solar Panels
    glColor3f(0.1, 0.2, 0.5)
    glPushMatrix()
    glTranslatef(5*scale_mult, 0, 0)
    glScalef(6*scale_mult, 2*scale_mult, 0.2*scale_mult)
    glutSolidCube(1)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(-5*scale_mult, 0, 0)
    glScalef(6*scale_mult, 2*scale_mult, 0.2*scale_mult)
    glutSolidCube(1)
    glPopMatrix()
    
    glPopMatrix()

def draw_ufo():
    # Orbiting in the asteroid belt
    rad = math.radians(ufo_angle)
    # Give it a wobbly orbit
    orbit_rad = 310 + 20 * math.sin(time.time() * 2)
    cx = orbit_rad * math.cos(rad)
    cy = orbit_rad * math.sin(rad)
    cz = 15 * math.sin(time.time() * 3) # Bobbing up and down
    
    glPushMatrix()
    glTranslatef(cx, cy, cz)
    
    # Tilt it slightly towards movement
    glRotatef(20 * math.sin(time.time() * 4), 1, 1, 0)
    
    # Saucer Body
    glColor3f(0.2, 0.8, 0.3) # Alien green
    glPushMatrix()
    glScalef(2 * scale_mult, 2 * scale_mult, 0.4 * scale_mult)
    gluSphere(quadric, 4, 20, 20)
    glPopMatrix()
    
    # Glass Dome
    glColor3f(0.6, 0.9, 1.0) # Light blue glass
    glPushMatrix()
    glTranslatef(0, 0, 1.5 * scale_mult)
    glScalef(1.2 * scale_mult, 1.2 * scale_mult, 1.2 * scale_mult)
    gluSphere(quadric, 2, 16, 16)
    glPopMatrix()
    
    # Blinking Lights around the rim
    glPushMatrix()
    glRotatef(time.time() * 100, 0, 0, 1) # Spin the lights
    for i in range(8):
        glPushMatrix()
        angle = (360.0 / 8) * i
        glRotatef(angle, 0, 0, 1)
        glTranslatef(7.5 * scale_mult, 0, 0)
        
        # Blink effect
        if int(time.time() * 5 + i) % 2 == 0:
            glColor3f(1.0, 0.1, 0.1) # Red light
        else:
            glColor3f(1.0, 1.0, 0.0) # Yellow light
            
        glutSolidCube(1 * scale_mult)
        glPopMatrix()
    glPopMatrix()
    
    glPopMatrix()

def draw_dyson_sphere():
    # A mega-structure wireframe around the Sun
    glPushMatrix()
    glRotatef(time.time() * 5, 0, 1, 1) # Slow complex rotation
    glColor3f(0.3, 0.5, 0.8) # Metallic blue
    
    # Draw longitude rings
    for i in range(6):
        glPushMatrix()
        glRotatef(i * 30, 0, 1, 0)
        glBegin(GL_LINE_LOOP)
        for j in range(60):
            a = math.radians(j * 6)
            r = SUN_RADIUS * 1.8
            glVertex3f(r * math.cos(a), r * math.sin(a), 0)
        glEnd()
        glPopMatrix()
        
    # Draw latitude rings
    for i in range(1, 4):
        glPushMatrix()
        z_offset = (i - 2) * SUN_RADIUS * 0.8
        r = math.sqrt((SUN_RADIUS * 1.8)**2 - z_offset**2)
        glTranslatef(0, 0, z_offset)
        glBegin(GL_LINE_LOOP)
        for j in range(60):
            a = math.radians(j * 6)
            glVertex3f(r * math.cos(a), r * math.sin(a), 0)
        glEnd()
        glPopMatrix()
        
    # Add a few solid solar panels at intersections
    for i in range(4):
        glPushMatrix()
        glRotatef(i * 90 + time.time() * 10, 1, 0, 0)
        glTranslatef(0, SUN_RADIUS * 1.8, 0)
        glScalef(8, 2, 8)
        glColor3f(0.1, 0.2, 0.4) # Dark blue panels
        glutSolidCube(1)
        glPopMatrix()
        
    glPopMatrix()

def draw_wormhole():
    # Placed far out past Neptune
    wx, wy, wz = 1000, 800, 100
    glPushMatrix()
    glTranslatef(wx, wy, wz)
    
    # Tilt the wormhole to face the inner system somewhat
    glRotatef(45, 1, 1, 0)
    
    # The event horizon (Black sphere)
    glColor3f(0.0, 0.0, 0.0)
    gluSphere(quadric, 35 * scale_mult, 20, 20)
    
    # Accretion disk (swirling particles)
    glPointSize(3)
    glBegin(GL_POINTS)
    for i in range(400):
        # Random distance from center
        dist = 40 * scale_mult + (i % 80) * 1.5 * scale_mult
        # Speed increases closer to the center
        speed = 200.0 / dist
        angle = math.radians((i * 13.7) + (time.time() * speed * 20))
        
        # Color gradient: Purple on outside, bright cyan on inside
        blend = min(1.0, (dist - 40 * scale_mult) / (120 * scale_mult))
        glColor3f(0.2 + (1-blend)*0.8, 0.1 + blend*0.4, 0.8 + (1-blend)*0.2)
        
        x = dist * math.cos(angle)
        y = dist * math.sin(angle)
        # Slight thickness to the disk
        z = 4 * scale_mult * math.sin(i * 2.3 + time.time() * 2)
        glVertex3f(x, y, z)
    glEnd()
    glPointSize(2) # reset point size
    
    glPopMatrix()

def draw_hud():
    # Title
    draw_text(10, W_HEIGHT-30, "3D Solar System Voyager")
    # Time
    state = "PAUSED" if paused else "RUNNING"
    draw_small_text(10, W_HEIGHT-55, f"Time: x{time_scale:.1f} [{state}]")
    draw_small_text(10, W_HEIGHT-75, f"Mode: {cam_mode.upper()}")

    # Controls
    draw_small_text(10, 95, "[1-8] Focus Planet  [0] Overview  [F] Free-roam")
    draw_small_text(10, 75, "[SPACE] Pause  [/] Speed  [O] Orbits  [T] Scale x10")
    draw_small_text(10, 55, "[Arrows] Camera  [+/-] Zoom  [Click] Select")
    draw_small_text(10, 35, "[Ctrl+Drag] Move Planet  [WASD] Fly  [R] Reset")

    # Focused planet info
    if 0 <= focused_planet < len(PLANETS):
        p = PLANETS[focused_planet]
        bx = W_WIDTH - 280
        draw_text(bx, W_HEIGHT-30, f">> {p['name']}")
        draw_small_text(bx, W_HEIGHT-55, f"Distance from Sun: {p['info']['dist']}")
        draw_small_text(bx, W_HEIGHT-75, f"Orbital Period: {p['info']['period']}")
        draw_small_text(bx, W_HEIGHT-95, f"Known Moons: {p['info']['moons_count']}")
        draw_small_text(bx, W_HEIGHT-115, f"Orbit Radius: {p['orbit_radius']:.0f} units")

    # Distance from Earth
    earth_pos = get_planet_pos(2)
    cam_pos = get_cam_pos()
    d = dist3d(cam_pos, earth_pos)
    draw_small_text(W_WIDTH//2-100, 15, f"Distance from Earth: {d:.0f} units")

# ============================================================
# SECTION 7: CAMERA
# ============================================================
def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, W_WIDTH/W_HEIGHT, 1.0, 6000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if cam_mode == 'overview':
        cx, cy, cz = get_cam_pos()
        gluLookAt(cx, cy, cz, 0, 0, 0, 0, 0, 1)
    elif cam_mode == 'track' and focused_planet >= 0:
        px, py, pz = get_planet_pos(focused_planet)
        cx, cy, cz = get_cam_pos()
        gluLookAt(cx, cy, cz, px, py, pz, 0, 0, 1)
    elif cam_mode == 'free':
        yr, pr = math.radians(free_yaw), math.radians(free_pitch)
        lx = math.cos(pr)*math.cos(yr)
        ly = math.cos(pr)*math.sin(yr)
        lz = math.sin(pr)
        fx, fy, fz = free_pos
        gluLookAt(fx, fy, fz, fx+lx, fy+ly, fz+lz, 0, 0, 1)

# ============================================================
# SECTION 8: PICKING & DRAGGING
# ============================================================
def screen_to_world(mx, my):
    try:
        mv = glGetDoublev(GL_MODELVIEW_MATRIX)
        pj = glGetDoublev(GL_PROJECTION_MATRIX)
        vp = glGetIntegerv(GL_VIEWPORT)
        wy = vp[3] - my
        p1 = gluUnProject(mx, wy, 0.0, mv, pj, vp)
        p2 = gluUnProject(mx, wy, 1.0, mv, pj, vp)
        if abs(p2[2]-p1[2]) < 0.0001:
            return None
        t = -p1[2]/(p2[2]-p1[2])
        return (p1[0]+t*(p2[0]-p1[0]), p1[1]+t*(p2[1]-p1[1]))
    except:
        return None

def pick_planet(mx, my):
    try:
        mv = glGetDoublev(GL_MODELVIEW_MATRIX)
        pj = glGetDoublev(GL_PROJECTION_MATRIX)
        vp = glGetIntegerv(GL_VIEWPORT)
        wy = vp[3] - my
        best = -1
        best_d = 40
        for i, p in enumerate(PLANETS):
            px, py, pz = get_planet_pos(i)
            sx, sy, sz = gluProject(px, py, pz, mv, pj, vp)
            d = math.sqrt((sx-mx)**2 + (sy-wy)**2)
            if d < best_d:
                best_d = d
                best = i
        return best
    except:
        return -1

def focus_on_planet(idx):
    global cam_mode, focused_planet, track_angle_h, track_angle_v, track_distance
    focused_planet = idx
    cam_mode = 'track'
    track_angle_h = 0.0
    track_angle_v = 30.0
    track_distance = PLANETS[idx]['radius']*scale_mult*5 + 40

# ============================================================
# SECTION 9: INPUT HANDLERS
# ============================================================
def keyboardListener(key, x, y):
    global cam_mode, focused_planet, time_scale, paused, show_orbits
    global scale_mult, show_labels, free_pos, free_yaw

    if key in [b'1',b'2',b'3',b'4',b'5',b'6',b'7',b'8']:
        focus_on_planet(int(key)-1)
    elif key == b'0':
        reset_view()
    elif key == b'f' or key == b'F':
        if cam_mode != 'free':
            cam_mode = 'free'
            cp = get_cam_pos()
            free_pos = list(cp)
        else:
            cam_mode = 'overview'
    elif key == b']':
        time_scale = min(time_scale*1.5, 50.0)
    elif key == b'[':
        time_scale = max(time_scale/1.5, 0.05)
    elif key == b' ':
        paused = not paused
    elif key == b'o' or key == b'O':
        show_orbits = not show_orbits
    elif key == b't' or key == b'T':
        scale_mult = 1.0 if scale_mult > 1.0 else 10.0
    elif key == b'+' or key == b'=':
        zoom_camera(-1)
    elif key == b'-' or key == b'_':
        zoom_camera(1)
    elif key == b'r' or key == b'R':
        reset_view()
    # Free-roam WASD
    if cam_mode == 'free':
        spd = 15.0
        yr = math.radians(free_yaw)
        pr = math.radians(free_pitch)
        fx = math.cos(pr)*math.cos(yr)
        fy = math.cos(pr)*math.sin(yr)
        fz = math.sin(pr)
        rx = math.cos(yr+math.pi/2)
        ry = math.sin(yr+math.pi/2)
        if key == b'w':
            free_pos[0]+=fx*spd; free_pos[1]+=fy*spd; free_pos[2]+=fz*spd
        elif key == b's':
            free_pos[0]-=fx*spd; free_pos[1]-=fy*spd; free_pos[2]-=fz*spd
        elif key == b'a':
            free_pos[0]-=rx*spd; free_pos[1]-=ry*spd
        elif key == b'd':
            free_pos[0]+=rx*spd; free_pos[1]+=ry*spd

def zoom_camera(direction):
    global ov_distance, track_distance
    if cam_mode == 'overview':
        ov_distance = max(100, min(3000, ov_distance + direction*50))
    elif cam_mode == 'track':
        track_distance = max(20, min(500, track_distance + direction*15))

def specialKeyListener(key, x, y):
    global ov_angle_h, ov_angle_v, ov_distance
    global track_angle_h, track_angle_v, free_yaw, free_pitch
    if cam_mode == 'overview':
        if key == GLUT_KEY_LEFT: ov_angle_h -= 3
        if key == GLUT_KEY_RIGHT: ov_angle_h += 3
        if key == GLUT_KEY_UP: ov_angle_v = min(89, ov_angle_v+3)
        if key == GLUT_KEY_DOWN: ov_angle_v = max(-89, ov_angle_v-3)
    elif cam_mode == 'track':
        if key == GLUT_KEY_LEFT: track_angle_h -= 5
        if key == GLUT_KEY_RIGHT: track_angle_h += 5
        if key == GLUT_KEY_UP: track_angle_v = min(89, track_angle_v+5)
        if key == GLUT_KEY_DOWN: track_angle_v = max(-10, track_angle_v-5)
    elif cam_mode == 'free':
        if key == GLUT_KEY_LEFT: free_yaw += 3
        if key == GLUT_KEY_RIGHT: free_yaw -= 3
        if key == GLUT_KEY_UP: free_pitch = min(89, free_pitch+3)
        if key == GLUT_KEY_DOWN: free_pitch = max(-89, free_pitch-3)

def mouseListener(button, state, x, y):
    global mouse_left_down, last_mx, last_my, dragging_planet, focused_planet, cam_mode
    last_mx, last_my = x, y
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            mouse_left_down = True
            mods = glutGetModifiers()
            ctrl_held = (mods & GLUT_ACTIVE_CTRL) != 0
            hit = pick_planet(x, y)
            if ctrl_held and hit >= 0:
                # Ctrl+Click = start dragging planet (no zoom)
                dragging_planet = hit
            elif hit >= 0:
                # Normal click = zoom/focus on planet
                dragging_planet = -1
                focus_on_planet(hit)
            else:
                dragging_planet = -1
        else:
            mouse_left_down = False
            dragging_planet = -1
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        cam_mode = 'overview'
        focused_planet = -1
    # Scroll zoom
    if button == 3:
        zoom_camera(-1)
    elif button == 4:
        zoom_camera(1)

def motionListener(x, y):
    global last_mx, last_my
    dx = x - last_mx
    dy = y - last_my
    last_mx, last_my = x, y

    if dragging_planet >= 0 and mouse_left_down:
        wpos = screen_to_world(x, y)
        if wpos:
            wx, wy = wpos
            new_radius = math.sqrt(wx*wx + wy*wy)
            new_angle = math.degrees(math.atan2(wy, wx))
            p = PLANETS[dragging_planet]
            p['orbit_radius'] = max(60, new_radius)
            p['orbit_angle'] = new_angle
    elif mouse_left_down and cam_mode == 'overview':
        global ov_angle_h, ov_angle_v
        ov_angle_h -= dx*0.3
        ov_angle_v += dy*0.3
        ov_angle_v = max(-89, min(89, ov_angle_v))
    elif mouse_left_down and cam_mode == 'track':
        global track_angle_h, track_angle_v
        track_angle_h -= dx*0.3
        track_angle_v += dy*0.3
        track_angle_v = max(-10, min(89, track_angle_v))

def passiveMotionListener(x, y):
    global last_mx, last_my, free_yaw, free_pitch
    if cam_mode == 'free':
        dx = x - last_mx
        dy = y - last_my
        free_yaw -= dx*0.15
        free_pitch -= dy*0.15
        free_pitch = max(-89, min(89, free_pitch))
    last_mx, last_my = x, y

def reset_view():
    global cam_mode, focused_planet, ov_angle_h, ov_angle_v, ov_distance
    global time_scale, paused, scale_mult
    cam_mode = 'overview'
    focused_planet = -1
    ov_angle_h = 45.0
    ov_angle_v = 35.0
    ov_distance = 900.0
    time_scale = 1.0
    paused = False
    scale_mult = 1.0

# ============================================================
# SECTION 10: UPDATE & DISPLAY
# ============================================================
def idle():
    global last_time, comet_angle, voyager_angle, ufo_angle
    now = time.time()
    dt = now - last_time
    last_time = now
    if not paused:
        for p in PLANETS:
            p['orbit_angle'] += p['orbit_speed']*time_scale*dt*30
            p['self_rot'] += p['self_rot_spd']*time_scale*dt*30
            for m in p['moons']:
                m['orbit_angle'] += m['orbit_speed']*time_scale*dt*30
        comet_angle += 1.5 * time_scale * dt * 30
        voyager_angle += 2.5 * time_scale * dt * 30
        ufo_angle -= 1.0 * time_scale * dt * 30 # Moves backwards!
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, W_WIDTH, W_HEIGHT)
    setupCamera()

    draw_starfield()
    draw_sun()
    draw_dyson_sphere()

    for i in range(len(PLANETS)):
        if show_orbits or focused_planet == i:
            draw_orbit_path(PLANETS[i]['orbit_radius'])
        draw_planet(i)

    draw_asteroid_belt()
    draw_comet()
    draw_ufo()
    draw_wormhole()
    
    ex, ey, ez = get_planet_pos(2) # Earth is index 2
    draw_voyager(ex, ey, ez)
    
    draw_hud()

    # Planet name labels in 3D
    if show_labels:
        for i, p in enumerate(PLANETS):
            px, py, pz = get_planet_pos(i)
            glPushMatrix()
            glTranslatef(px, py, p['radius']*scale_mult+8)
            glColor3f(1,1,1)
            glRasterPos3f(0, 0, 0)
            for ch in p['name']:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))
            glPopMatrix()

    glutSwapBuffers()

# ============================================================
# SECTION 11: MAIN
# ============================================================
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(W_WIDTH, W_HEIGHT)
    glutInitWindowPosition(50, 50)
    glutCreateWindow(b"3D Solar System Voyager - CSE423 Lab Project")
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.02, 0.02, 0.05, 1.0)

    init_universe()

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutMotionFunc(motionListener)
    glutPassiveMotionFunc(passiveMotionListener)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == "__main__":
    main()
