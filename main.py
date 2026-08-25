import pygame
from os.path import join

# Blue Print
class Entity:
    def __init__(self, left, top, img):
        self.left = left
        self.top = top
        self.height = img.get_height()
        self.width = img.get_width()
        self.right = self.left + self.width
        self.bottom = self.top + self.height
        self.img = img
    
class Platforms(Entity):
    def __init__(self, left, top, img):
        super().__init__(left, top, img)
                
class Jane(Entity):
    def __init__(self, left, top, img):
        super().__init__(left, top, img)
        
        # direction state
        self.move_speed = 10
        self.face_direction = "right"
        self.forward_blocked = False
        self.backward_blocked = False
        # jumping state
        self.jumping = False
        self.jumping_direction = "down"
        self.can_jump = True
        self.can_double_jump = False
        self.jump_height = 100
        self.extra_jump_height = 0
        # ground state
        self.jane_ground = self.bottom
        self.on_platform = False

class Cheese(Entity):
    def __init__(self, left, top, img):
        super().__init__( left, top, img)  
        # direction
        self.facing_right = True
        # state
        self.taken = False

# --- Utility Functions ---
def setSize_W(image, width): 
    w, h = image.get_size()
    ratio = w / h
    height = int(width / ratio)
    return pygame.transform.scale(image, (width, height))

def setSize_WH(image, width, height):
    return pygame.transform.scale(image, (width, height))

def loadImage(path):
    return pygame.image.load(path)

def calc_align_right(image):
    return WINDOW_WIDTH - image.get_width()

def calc_align_bottom(image):
    return WINDOW_HEIGHT - image.get_height()

def flip_x(image):
    return pygame.transform.flip(image, True, False)

def flip_y(image):
    return pygame.transform.flip(image, False, True)

def flip_xy(image):
    return pygame.transform.flip(image, True, True)

def fade_on_approach(jane_x, target_x, target_img):
    distance = target_x - jane_x
    if distance <= 100:
        target_img.set_alpha(int(255 * distance / 100))
    else:
        target_img.set_alpha(255)


# --- Environtment Setup ---
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 500
pygame.init()
display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

# --- Jane Setup ---
jane_initial_img = loadImage(join("assets","jane1.png")).convert_alpha()
jane_initial_img = setSize_W(jane_initial_img, 100)
jane_initial_top = WINDOW_HEIGHT-jane_initial_img.get_height()
jane_initial_left = 0
jane = Jane( top= jane_initial_top ,left = jane_initial_left , img=jane_initial_img)

# --- Cheese Setup ---
cheese_initial_img = loadImage(join("assets","cheese.png")).convert_alpha()
cheese_initial_img = setSize_W(cheese_initial_img, 40)
cheese_initial_top = calc_align_bottom(cheese_initial_img)
cheese_initial_left = calc_align_right(cheese_initial_img) - cheese_initial_img.get_width()
cheese = Cheese(top=cheese_initial_top, left=cheese_initial_left, img=cheese_initial_img)

# --- Firewall Setup ---
firewall_initial_img = loadImage("assets/firewall.png").convert_alpha()
firewall_initial_img = setSize_WH(firewall_initial_img, 100, 200)
firewall_initial_left = calc_align_right(firewall_initial_img) - 400
firewall_initial_top = int(calc_align_bottom(firewall_initial_img) + firewall_initial_img.get_height() / 3)
firewall = Platforms(left= firewall_initial_left, top= firewall_initial_top, img=firewall_initial_img)


# --- Movement ---
starting_ground = WINDOW_HEIGHT

# --- Main Loop ---
running = True
while running:
    prev_ground = jane.jane_ground
    keys = pygame.key.get_pressed()

#SECTION: STATE_&_INPUT_MANAGEMENT
    # Logic(close game, jump_permission, double_jump_permission, cheese_taken_state);
    # Input(QUIT, SPACE, F);
    # Log(jump coordinate, double jump coordinate)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                print("can_jump:", jane.can_jump)
                if jane.can_double_jump and not jane.can_jump:
                    print("second jump at", jane.bottom)
                    jane.jumping_direction = "up"
                    jane.extra_jump_height += 80
                    jane.can_double_jump = False
                elif jane.can_jump:
                    jane.jumping = True
                    jane.jumping_direction = "up"
                    jane.can_jump = False
                    jane.can_double_jump = True
                    print("Jumping:", jane.jumping, "at", jane.bottom)
                    starting_ground = jane.jane_ground
            if event.key == pygame.K_f:
                if (
                    jane.right >= cheese.left and jane.right <= cheese.right
                    or jane.left >= cheese.left and jane.left <= cheese.right 
                    ):
                    if cheese.taken: cheese.taken = False
                    else: cheese.taken = True
    # Logic(move foreward, move backward, flip direction)
    # Input(D, A)
    if keys[pygame.K_d]:
        if not jane.forward_blocked:
            jane.left += jane.move_speed
            if jane.face_direction != "right":
                jane.face_direction = "right"
                jane.img = flip_x(jane.img)
        # else: print("forward Blocked"
    if keys[pygame.K_a] and not jane.backward_blocked:
        jane.left -= jane.move_speed
        if jane.face_direction != "left":
            jane.face_direction = "left"
            jane.img = flip_x(jane.img)
    # Logic(collision blocking)
    if (
        (jane.right >= firewall.left + int(firewall.width / 2) - 20)   
        and 
        (jane.right <= firewall.left + int(firewall.width / 2) + 20)
        and 
        (jane.bottom > firewall.top + 34)
        ):
        jane.forward_blocked = True
    else:
        jane.forward_blocked = False    
    if (
        (jane.left >= firewall.left + int(firewall.width / 2) - 20 )
        and 
        (jane.left <= firewall.left + int(firewall.width / 2) + 20)
        and
        (jane.bottom > firewall.top + 34)
        ):
        jane.backward_blocked = True
    else:
        jane.backward_blocked = False

    # Logic(ground to firewall)
    if (jane.bottom <= firewall.top + 34
        and jane.right >= firewall.left
        and jane.left <= firewall.right):
        jane.on_platform = True
        jane.jane_ground = firewall.top + 34
    else:
        jane.on_platform = False
    # Logic(firewall to ground)
    if not jane.on_platform:
        jane.jane_ground = WINDOW_HEIGHT
    if jane.jane_ground != prev_ground:
        print("ground berubah")
        print("on platform", jane.on_platform)
        if not jane.on_platform and not jane.jumping:
            print("guing_up false")
            jane.jumping = True
            jane.jumping_direction = "down"
    # Log(ground changing)
    if jane.jane_ground != prev_ground:
        print("prev ground: ", prev_ground)
        print("current ground ", jane.jane_ground)
    # Logic(update postition)
    # Log(foot coordinate)
    jane.right = jane.left + jane.width
    if jane.jumping:
        # start jumping
        if jane.jumping_direction == "up":
            jane.bottom -= 10
            jane.top = jane.bottom - jane.height
            print("going up: ", jane.bottom)
        # reach maxiimun
        elif jane.jumping_direction == "down" and jane.bottom < jane.jane_ground:
            print("going down: ", jane.bottom)
            jane.bottom += 10
            jane.top = jane.bottom - jane.height
        # reach the ground === makes stay
        if jane.bottom >= jane.jane_ground:
            jane.jumping = False
            jane.can_jump = True
            print("on the ground: ", jane.bottom)
            jane.can_double_jump = False
            jane.extra_jump_height = 0
        #fall switch === makes fall permission
        if starting_ground - jane.bottom >= (jane.jump_height + jane.extra_jump_height) and jane.jumping_direction == "up":
            print("fall at", jane.bottom)
            print("jump height:", jane.jump_height+ jane.extra_jump_height)
            jane.jumping_direction = "down"
            
# SECTION(RENDER)
    display.fill("black")
    # firewall & jane render
    if jane.left <= (firewall.right/ 2):  
        sprites = [
            (firewall.img, firewall.left, firewall.top),
            (jane.img, jane.left, jane.top),
        ] 
    else:
        sprites = [
            (jane.img, jane.left, jane.top),
            (firewall.img, firewall.left, firewall.top),
        ]
    for sprite, sx, sy in sprites:
        display.blit(sprite, (sx, sy))
    
    # cheese render
    if cheese.taken:
        if jane.face_direction =="right":
            cheese.left = jane.right - 40
            cheese.top = jane.bottom - 40
            display.blit(cheese.img, (cheese.left, cheese.top))
        if jane.face_direction == "left":
            cheese.left = jane.left
            cheese.top = jane.bottom - 40
            display.blit(cheese.img, (cheese.left, cheese.top))
    else:
        cheese.top = calc_align_bottom(cheese.img)
        display.blit(cheese.img, (cheese.left, cheese.top))
    
    pygame.display.update()
    clock.tick(60)

pygame.quit()